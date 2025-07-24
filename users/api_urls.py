# Project: meity_audit_portal
# App: users
# File: users/api_urls.py
# Description: API URL routing for user-related functionalities (registration, user details).

from django.urls import path
from .api_views import RegisterUserAPIView, UserDetailAPIView # Import API views

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='api_register'),
    path('me/', UserDetailAPIView.as_view(), name='api_user_detail'), # Endpoint to get current user's details
]
