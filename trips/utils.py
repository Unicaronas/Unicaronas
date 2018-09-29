from django.contrib.auth.models import User


def user_is_driver(user):
    """Whether or not the user is a driver"""
    try:
        user.driver
    except User.driver.RelatedObjectDoesNotExist:
        return False
    return True
