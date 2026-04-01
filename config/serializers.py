from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Module, ModulePermission, ApiKey


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class ModulePermissionSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)

    class Meta:
        model = ModulePermission
        fields = '__all__'
        extra_fields = ['module_name']


class ApiKeySerializer(serializers.ModelSerializer):
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApiKey
        fields = '__all__'
        read_only_fields = ['key', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name',
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'date_joined', 'groups',
        ]
        read_only_fields = ['last_login', 'date_joined']
