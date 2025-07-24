# Project: meity_audit_portal
# App: audit_management
# File: audit_management/api_urls.py
# Description: API URL routing for audit request management.

from django.urls import path
from .api_views import (
    AuditRequestListCreateAPIView,
    AuditRequestDetailAPIView,
    DocumentUploadAPIView,
    RemarkCreateAPIView,
    AuditRequestStatusUpdateAPIView,
    DocumentDeleteAPIView,
)

urlpatterns = [
    # Audit Request List (GET) and Create (POST)
    path('requests/', AuditRequestListCreateAPIView.as_view(), name='api_audit_request_list_create'),
    
    # Audit Request Detail (GET), Update (PUT/PATCH)
    path('requests/<int:pk>/', AuditRequestDetailAPIView.as_view(), name='api_audit_request_detail'),
    
    # Document Upload (POST)
    path('requests/<int:audit_request_pk>/documents/upload/', DocumentUploadAPIView.as_view(), name='api_document_upload'),
    
    # Document Delete (DELETE)
    path('documents/<int:pk>/delete/', DocumentDeleteAPIView.as_view(), name='api_document_delete'),

    # Remark Create (POST)
    path('requests/<int:audit_request_pk>/remarks/add/', RemarkCreateAPIView.as_view(), name='api_remark_add'),

    # Status Update (PATCH)
    path('requests/<int:pk>/status-update/', AuditRequestStatusUpdateAPIView.as_view(), name='api_audit_request_status_update'),
]
