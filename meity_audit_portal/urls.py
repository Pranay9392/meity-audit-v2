
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

