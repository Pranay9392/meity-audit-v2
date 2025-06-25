# Project: meity_audit_portal
# App: users
# File: users/forms.py
# Description: Defines the custom user creation form for registration and update.

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    class Meta:
        model = CustomUser
        # Include all fields from AbstractUser that you want in the registration form,
        # plus your custom fields like 'role' and 'organization'.
        fields = UserCreationForm.Meta.fields + ('role', 'organization')

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users in the admin interface.
    """
    class Meta:
        model = CustomUser
        # Include all fields from AbstractUser that you want to be editable
        # in the admin's user change form, plus your custom fields.
        fields = ('username', 'email', 'role', 'organization', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
