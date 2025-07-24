# Project: meity_audit_portal
# App: audit_management
# File: audit_management/urls.py
# Description: URL routing for audit-related functionalities, including document deletion.

from django.urls import path
from . import views

urlpatterns = [
    path('audit-requests/new/', views.create_audit_request, name='create_audit_request'),
    #path('audit-requests/', views.audit_request_list, name='audit_request_list'),
    path('requests/', views.audit_request_list, name='audit_request_list'),
    path('audit-requests/<int:pk>/', views.audit_request_detail, name='audit_request_detail'),
    
    path('documents/<int:pk>/delete/', views.delete_document, name='delete_document'), # New URL for document deletion
]



