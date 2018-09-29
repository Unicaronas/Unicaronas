from rest_framework.views import exception_handler
from ..serializers import ExceptionSerializer


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    return response

    # Now add the HTTP status code to the response.
    if response is not None:
        data = {'detail': response.data.get('detail', ''), 'status_code': response.status_code}
        response.data = ExceptionSerializer(data).data

    return response
