# Project: meity_audit_portal
# App: users
# File: users/admin.py
# Description: Registers the CustomUser model with the Django admin interface.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register CustomUser with the admin site
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom Admin interface for CustomUser model.
    Overrides default UserAdmin to include custom fields.
    """
    add_form = CustomUserCreationForm # Form to use when creating a user in admin
    form = CustomUserChangeForm # Form to use when changing an existing user in admin
    model = CustomUser
    list_display = ('username', 'email', 'role', 'organization', 'is_staff') # Fields to display in the list view

    # Add custom fields to the fieldsets for both viewing/editing and adding users
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'organization')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'organization')}),
    )
