from rest_framework.reverse import reverse
from rest_framework import serializers
from oauth2_provider.models import get_application_model
from user_data.models import Profile
from ..mixins import QueryFieldsMixin


class ProfilePictureField(serializers.URLField):

    def __init__(self, size='medium_256', **kwargs):
        self.size = size
        kwargs['source'] = kwargs.get('source', '*')
        kwargs['read_only'] = True
        kwargs['allow_null'] = True
        kwargs['read_only'] = True
        super(serializers.CharField, self).__init__(**kwargs)

    def to_representation(self, value):
        assert isinstance(value, Profile)
        request = self.context.get('request', None)
        if hasattr(request, 'auth') and bool(value.picture.name):
            token = request.auth
            app = token.application
            user = value.user
            scoped_id = get_application_model().get_scoped_user_id(app, user)
            url = reverse(
                'static_content:profile_picture_proxy', kwargs={'user_id': scoped_id},
                request=request
            ) + f'?size={self.size}'
        else:
            url = None
        return url


class ProfilePictureSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        kwargs['source'] = kwargs.get('source', '*')
        kwargs['label'] = kwargs.get('label', 'Foto de perfil')
        super().__init__(*args, **kwargs)

    small_32 = ProfilePictureField(size='small_32', label="Foto 32x32")
    small_64 = ProfilePictureField(size='small_64', label="Foto 64x64")
    medium_128 = ProfilePictureField(size='medium_128', label="Foto 128x128")
    medium_256 = ProfilePictureField(size='medium_256', label="Foto 256x256")
    large_512 = ProfilePictureField(size='large_512', label="Foto 512x512", help_text='Como o tamanho mínimo de imagens é 256x256, fotos nessa dimensão pode ter as mesmas dimensões da imagem orignal.')
    large_1024 = ProfilePictureField(size='large_1024', label="Foto 1024x1024", help_text='Como o tamanho mínimo de imagens é 256x256, fotos nessa dimensão pode ter as mesmas dimensões da imagem orignal.')
    original = ProfilePictureField(size='original', label="Foto original", help_text='Pode ter qualquer dimensão quadrada entre 256x256 e 2048x2048')

    class Meta:
        model = Profile
        fields = (
            "small_32",
            "small_64",
            "medium_128",
            "medium_256",
            "large_512",
            "large_1024",
            "original"
        )
