# Project: meity_audit_portal
# App: audit_management
# File: audit_management/admin.py
# Description: Registers models for the audit_management app with the Django admin interface.

from django.contrib import admin
from .models import AuditRequest, Document, Remark

@admin.register(AuditRequest)
class AuditRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_provider_name', 'csp', 'status', 'request_date', 'last_updated')
    list_filter = ('status', 'request_date', 'csp__organization') # Filter by status, date, and CSP's organization
    search_fields = ('service_provider_name', 'data_center_location', 'description', 'csp__username')
    raw_id_fields = ('csp',) # Use a raw ID field for CSP for better performance with many users

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit_request', 'document_type', 'uploaded_by', 'upload_date', 'file')
    list_filter = ('document_type', 'upload_date', 'uploaded_by__role')
    search_fields = ('audit_request__service_provider_name', 'description', 'uploaded_by__username')
    raw_id_fields = ('audit_request', 'uploaded_by')

@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit_request', 'author', 'timestamp', 'comment_snippet')
    list_filter = ('timestamp', 'author__role')
    search_fields = ('audit_request__service_provider_name', 'comment', 'author__username')
    raw_id_fields = ('audit_request', 'author')

    def comment_snippet(self, obj):
        """Display a snippet of the comment in the list view."""
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_snippet.short_description = 'Comment'
