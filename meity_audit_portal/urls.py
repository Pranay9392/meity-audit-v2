'''
# Project: meity_audit_portal
# File: meity_audit_portal/urls.py
# Description: Main URL routing for the project.

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root URL, serving the landing page.
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('', include('users.urls')), # Include URLs from the users app
    path('', include('audit_management.urls')), # Include URLs from the audit_management app
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

'''



# meity_audit_portal/urls.py (Example - not for editing)

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Import JWT views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Web app URLs (from users/urls.py and audit_management/urls.py)
    path('', include('users.urls')),
    path('', include('audit_management.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    # API Endpoints (from users/api_urls.py and audit_management/api_urls.py)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/users/', include('users.api_urls')), # Includes API user URLs
    path('api/audit-management/', include('audit_management.api_urls')), # Includes API audit URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)