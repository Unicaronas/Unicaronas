class PrefetchQuerysetModelMixin(object):
    """Lists a prefetched version of the model list

    To be used with PrefetchMixin
    """

    def get_queryset(self):
        assert self.queryset is not None
        queryset = self.queryset
        if hasattr(self.get_serializer_class(), 'setup_eager_loading'):
            queryset = self.get_serializer().setup_eager_loading(queryset)
        return queryset


class PrefetchMixin(object):

    @classmethod
    def setup_eager_loading(cls, queryset):
        meta = cls.Meta
        if hasattr(meta, "select_related_fields"):
            queryset = queryset.select_related(*meta.select_related_fields)
        if hasattr(meta, "prefetch_related_fields"):
            queryset = queryset.prefetch_related(*meta.prefetch_related_fields)
        return queryset
