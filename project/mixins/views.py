from rest_framework.response import Response


class PatchModelMixin(object):
    """
    Patch a model instance.

    Actually used to allow views to receive PATCH requests and process dara
    For this reason, it does not process the instance, only the data from the request
    """

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.validated_data)
