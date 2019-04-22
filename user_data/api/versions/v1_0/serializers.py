from django.contrib.auth.models import User
from rest_framework import serializers
from oauth.fields import ScopedUserIDField
from project.mixins import QueryFieldsPermissionMixin, PrefetchMixin, QueryFieldsMixin
from project.serializers import ProfilePictureSerializer
from ....models import Driver, Student, Profile


class NotPermissionedDriverSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    class Meta:
        model = Driver
        exclude = ['id', 'user']


class DriverSerializer(
        QueryFieldsPermissionMixin,
        serializers.ModelSerializer):
    class Meta:
        model = Driver
        exclude = ['id', 'user']
        field_permissions = {
            'driver:read': ['car_make', 'car_model', 'car_color'],
            'driver:preferences:read': ['likes_pets', 'likes_smoking', 'likes_music', 'likes_talking']
        }
        extra_kwargs = {
            'car_make': {'help_text': "Requer `driver:read`", "required": False},
            'car_model': {'help_text': "Requer `driver:read`", "required": False},
            'car_color': {'help_text': "Requer `driver:read`", "required": False},
            'likes_pets': {'help_text': "Requer `driver:preferences:read`", "required": False},
            'likes_smoking': {'help_text': "Requer `driver:preferences:read`", "required": False},
            'likes_talking': {'help_text': "Requer `driver:preferences:read`", "required": False},
            'likes_music': {'help_text': "Requer `driver:preferences:read`", "required": False},
        }


class BasicStudentSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['university', 'enroll_year', 'course']


class StudentSerializer(
        QueryFieldsPermissionMixin,
        serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['id', 'user']
        field_permissions = {
            'student:read': ['university', 'university_id', 'enroll_year', 'course'],
            'email:read': ['university_email'],
        }
        extra_kwargs = {
            'university': {'help_text': "Requer `student:read`", "required": False},
            'university_id': {'help_text': "Requer `student:read`", "required": False},
            'enroll_year': {'help_text': "Requer `student:read`", "required": False},
            'course': {'help_text': "Requer `student:read`", "required": False},
            'university_email': {'help_text': "Requer `email:read`", "required": False},
        }


class NotPermissionedProfileSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    picture = ProfilePictureSerializer(label='Foto de perfil')

    class Meta:
        model = Profile
        exclude = ['id', 'user']


class BasicProfileSerializer(
        QueryFieldsMixin,
        serializers.ModelSerializer):

    picture = ProfilePictureSerializer(label='Foto de perfil')

    class Meta:
        model = Profile
        fields = ['gender', 'birthday', 'picture']


class ProfileSerializer(
        QueryFieldsPermissionMixin,
        serializers.ModelSerializer):

    picture = ProfilePictureSerializer(help_text="Requer `profile:read`", required=False)

    class Meta:
        model = Profile
        exclude = ['id', 'user']
        field_permissions = {
            'profile:read': ['birthday', 'gender', 'picture'],
            'phone:read': ['phone'],
        }
        extra_kwargs = {
            'birthday': {'help_text': "Requer `profile:read`", "required": False},
            'gender': {'help_text': "Requer `profile:read`", "required": False},
            'phone': {'help_text': "Requer `phone:read`", "required": False},
            'picture': {'help_text': "Requer `profile:read`", "required": False},
        }


class UserDataSerializer(
        QueryFieldsPermissionMixin,
        PrefetchMixin,
        serializers.ModelSerializer):

    user_id = ScopedUserIDField(label="ID do usuário", help_text="Requer `basic:read`")

    profile = ProfileSerializer(required=False, help_text="Representa o perfil do usuário")

    student = StudentSerializer(required=False, help_text="Representa os dados de estudante do usuário")

    driver = DriverSerializer(required=False, help_text="Representa os dados de motorista do usuário. **Obs:**Caso o usuário não seja motorista, todos os seus valores serão `null`")

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'profile',
                  'student', 'driver']
        select_related_fields = ['profile', 'student', 'driver']
        extra_kwargs = {
            'first_name': {'help_text': "Requer `basic:read`", "required": False},
            'last_name': {'help_text': "Requer `basic:read`", "required": False},
            'email': {'help_text': "Requer `email:read`", "required": False},
        }
