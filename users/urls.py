# Project: meity_audit_portal
# App: users
# File: users/urls.py
# Description: URL routing for user-related functionalities.

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
