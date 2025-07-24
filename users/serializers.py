# Project: meity_audit_portal
# App: users
# File: users/serializers.py
# Description: Defines serializers for the CustomUser model for API use.

from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Used for user registration and fetching user details.
    """
    password = serializers.CharField(write_only=True) # Password should only be written, not read back

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'organization', 'password']
        read_only_fields = ['id'] # ID is automatically generated

    def create(self, validated_data):
        """
        Create and return a new `CustomUser` instance, given the validated data.
        Hashes the password before saving.
        """
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'CSP'), # Default to CSP if not provided
            organization=validated_data.get('organization', None)
        )
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing `CustomUser` instance, given the validated data.
        Handles password update separately.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.organization = validated_data.get('organization', instance.organization)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password) # Use set_password to hash the new password

        instance.save()
        return instance

