# Modified from https://github.com/wimglenn/djangorestframework-queryfields
import warnings
import re
from rest_framework import serializers


class QueryFieldsMixin(object):

    # If using Django filters in the API, these labels mustn't conflict with any model field names.
    include_arg_name = 'fields'
    exclude_arg_name = 'exclude'

    # Split field names by this string.  It doesn't necessarily have to be a single character.
    # Avoid RFC 1738 reserved characters i.e. ';', '/', '?', ':', '@', '=' and '&'
    delimiter = ','

    # Start and end arguments to filter nested fields
    child_start_arg_name = '{'
    child_end_arg_name = '}'

    def get_parent(self):
        """Gets field parent, ignoring ListSerializers"""
        if isinstance(self.parent, serializers.ListSerializer):
            return self.parent.parent
        return self.parent

    @property
    def is_child(self):
        """Whether or not the serializer is a child of another serializer"""
        return self.get_parent() is not None

    def get_field_name_as_child(self):
        """Returns the field name of the serializer as declared on the parent"""
        for k, v in self.get_parent().fields.items():
            if v is self:
                return k

    def get_query_params(self, request):
        """Returns the query parameters from the request"""
        try:
            query_params = request.query_params
        except AttributeError:
            # DRF 2
            query_params = getattr(request, 'QUERY_PARAMS', request.GET)
        return query_params

    def process_query_fields(self, query):
        """Processes a query string and turns it into a dict of fields"""
        query = re.sub(f'{self.child_start_arg_name}', '{', query)
        query = re.sub(f'{self.child_end_arg_name}', '}', query)
        query = re.sub(f'{self.delimiter}', ',', query)
        query = re.sub(r"(\w+)", r'"\1"', query)
        query = re.sub(r"{", ":{", query)
        query = '{' + query + '}'
        query = re.sub(r'",', r'":{},', query)
        query = re.sub(r'"}', r'":{}}', query)
        try:
            result = eval(query)
        except SyntaxError:
            raise serializers.ValidationError("Malformed query")
        return result

    def get_include_fields_dict(self, query_params):
        """Returns the include fields for the current serializer as a dict"""
        if self.is_child:
            parent_include_fields = self.get_parent().get_include_fields_dict(query_params)
            child_field_name = self.get_field_name_as_child()
            return parent_include_fields.get(child_field_name, {})

        includes = query_params.getlist(self.include_arg_name)
        return {name: val for names in includes for name, val in self.process_query_fields(names).items() if name}

    def get_include_fields(self, query_params):
        """Returns a list of include fields for the current serializer"""
        return self.get_include_fields_dict(query_params).keys()

    def get_exclude_fields_dict(self, query_params):
        """Returns the exclude fields for the current serializer as a dict"""
        if self.is_child:
            parent_exclude_fields = self.get_parent().get_exclude_fields_dict(query_params)
            child_field_name = self.get_field_name_as_child()
            return parent_exclude_fields.get(child_field_name, {})

        excludes = query_params.getlist(self.exclude_arg_name)
        return {name: val for names in excludes for name, val in self.process_query_fields(names).items() if name}

    def get_exclude_fields(self, query_params):
        """Returns the exclude fields for the current serializer as a list"""
        exclude_dict = self.get_exclude_fields_dict(query_params)
        # Do not exclude fields that filter deeper down
        return {field for field, children in exclude_dict.items() if not children}

    def get_view(self):
        """Returns the view of the serializer"""
        return self.context['view']

    def get_all_fields(self):
        """Returns all declared fields of the serializer"""
        return super().fields

    def get_allowed_serializer_fields(self, request):
        """Returns only the fields that are allowed given the user permissions"""
        all_fields = self.get_all_fields().keys()
        return all_fields

    @property
    def fields(self):
        try:
            request = self.context['request']
            method = request.method
        except (AttributeError, TypeError, KeyError):
            warnings.warn('The serializer was not initialized with request context.')
            return

        if method != 'GET':
            # If not GET, this mixin does nothing
            return super().fields

        query_params = self.get_query_params(request)

        include_fields = self.get_include_fields(query_params)

        exclude_fields = self.get_exclude_fields(query_params)

        allowed_fields = self.get_allowed_serializer_fields(request)
        fields_to_drop = allowed_fields & exclude_fields
        if include_fields:
            fields_to_drop |= allowed_fields - include_fields

        allowed_fields -= fields_to_drop
        all_fields = self.get_all_fields()
        return_data = {}
        for key, value in all_fields.items():
            if key in allowed_fields:
                return_data[key] = value
        return return_data


class QueryFieldsPermissionMixin(QueryFieldsMixin):

    def get_field_permissions(self):
        """Returns the field permissions dict from the view or serializer"""
        view = self.get_view()
        return getattr(self.Meta, 'field_permissions', {}) or getattr(view, 'field_permissions', {})

    def get_allowed_serializer_fields(self, request):
        """Returns only the fields that are allowed given the user permissions"""
        token = request.auth
        allowed_fields = set([])
        all_fields = self.get_all_fields().keys()
        if token:
            for scope, fields in self.get_field_permissions().items():
                # If the token allows the scope, add its fields to the set
                if token.allow_scopes([scope]):
                    allowed_fields |= set(fields)
        else:
            allowed_fields = all_fields
        # Return the subset of all fields that contains the allowed fields
        return all_fields & allowed_fields
