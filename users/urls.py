# Project: meity_audit_portal
# App: users
# File: users/urls.py
# Description: URL routing for user-related functionalities.

from django.urls import path,include
from . import views

urlpatterns = [
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    #path('api/', include('audit_management.api_urls'))
    path('api/', include('users.api_urls')),  # ✅ Add this line
    #path('api/audit/', include('audit_management.api_urls')),  # Moved here with prefix
]
