from celery.app import shared_task
from django.urls import reverse
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from oauth.models import get_user_apps
from search.finder import RedisFinder
from oauth2_provider.models import get_application_model


@shared_task
def refresh_profile_pics(instance_pk):
    from user_data.models import Profile
    from project.views import PictureProxyView
    instance = Profile.objects.get(pk=instance_pk)
    user = instance.user
    sizes = PictureProxyView.picture_sizes.keys()
    App = get_application_model()
    # Delete picture cache
    for app in get_user_apps(user):
        user_id = App.get_scoped_user_id(app, user)
        url = reverse('static_content:profile_picture_proxy', kwargs={'user_id': user_id})
        RedisFinder().delete_key(url)
        for size in sizes:
            url = reverse('static_content:profile_picture_proxy', kwargs={'user_id': user_id}) + f'?size={size}'
            RedisFinder().delete_key(url)

    # Delete old generated images
    instance.picture.delete_all_created_images()
    # Generate new warm images
    VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='profile_picture',
        image_attr='picture'
    ).warm()
