from functools import reduce
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import CharField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_nested.relations import NestedHyperlinkedIdentityField
from oauth2_provider.models import get_application_model
from .exceptions import InvalidScopedUserId


class ScopedUserIDField(CharField):

    def __init__(self, **kwargs):
        kwargs['source'] = kwargs.get('source', '*')
        kwargs['read_only'] = True
        kwargs['max_length'] = 100
        kwargs['min_length'] = 30
        super().__init__(**kwargs)

    def to_representation(self, value):
        assert isinstance(value, User)
        token = self.context['request'].auth
        if token:
            app = token.application
            user = value
            scoped_id = get_application_model().get_scoped_user_id(app, user)
        else:
            scoped_id = None
        return scoped_id


class ScopedUserIDHyperlinkedField(HyperlinkedIdentityField):
    def __init__(self, relation_to_user='user', *args, **kwargs):
        """
        For the reverse operation, given an user, return the object
        based off the relation from the user to the object.
        e.g.: relation_to_user='user.profile.student'
        """
        assert(relation_to_user == 'user' or relation_to_user.startswith('user.'))
        self.relation_to_user = relation_to_user
        super().__init__(*args, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Return the object corresponding to a matched URL.

        Takes the matched URL conf arguments, and should return an
        object instance, or raise an `ObjectDoesNotExist` exception.
        """
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        try:
            obj = get_application_model().recover_scoped_user_id(lookup_value)
        except InvalidScopedUserId:
            raise ObjectDoesNotExist('Invalid scoped user id')
        try:
            for attr in self.relation_to_user.split('.')[1:]:
                obj = getattr(obj, attr)
        except AttributeError as e:
            raise ObjectDoesNotExist('Invalid user relation')
        return obj

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None
        # Get the user from the object
        if isinstance(obj, User):
            user = obj
        else:
            user = getattr(obj, 'user', None)
            if user is None:
                raise ValueError("No user found within serialized object")
        app = request.auth.application
        lookup_value = get_application_model().get_scoped_user_id(app, user)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class NestedScopedUserIDHyperlinkedField(NestedHyperlinkedIdentityField):
    def __init__(self, relation_to_user='user', *args, **kwargs):
        """
        For the reverse operation, given an user, return the object
        based off the relation from the user to the object.
        e.g.: relation_to_user='user.profile.student'
        """
        assert(relation_to_user == 'user' or relation_to_user.startswith('user.'))
        self.relation_to_user = relation_to_user
        super().__init__(*args, **kwargs)

    def get_object(self, view_name, view_args, view_kwargs):
        """
        Return the object corresponding to a matched URL.

        Takes the matched URL conf arguments, and should return an
        object instance, or raise an `ObjectDoesNotExist` exception.
        """
        lookup_value = view_kwargs[self.lookup_url_kwarg]
        try:
            obj = get_application_model().recover_scoped_user_id(lookup_value)
        except InvalidScopedUserId:
            raise ObjectDoesNotExist('Invalid scoped user id')
        try:
            for attr in self.relation_to_user.split('.')[1:]:
                obj = getattr(obj, attr)
        except AttributeError as e:
            raise ObjectDoesNotExist('Invalid user relation')
        return obj

    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None
        # Get the user from the object
        if isinstance(obj, User):
            user = obj
        else:
            user = getattr(obj, 'user', None)
            if user is None:
                raise ValueError("No user found within serialized object")
        app = request.auth.application
        lookup_value = get_application_model().get_scoped_user_id(app, user)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        for parent_lookup_kwarg, underscored_lookup in self.parent_lookup_kwargs.items():

            # split each lookup by their __, e.g. "parent__pk" will be split into "parent" and "pk", or
            # "parent__super__pk" would be split into "parent", "super" and "pk"
            lookups = underscored_lookup.split('__')

            # use the Django ORM to lookup this value, e.g., obj.parent.pk
            lookup_value = reduce(getattr, [obj] + lookups)

            # store the lookup_name and value in kwargs, which is later passed to the reverse method
            kwargs.update({parent_lookup_kwarg: lookup_value})
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
