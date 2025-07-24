# Project: meity_audit_portal
# App: audit_management
# File: audit_management/serializers.py
# Description: Defines serializers for AuditRequest, Document, and Remark models for API use.

from rest_framework import serializers
from .models import AuditRequest, Document, Remark
from users.serializers import CustomUserSerializer # Import CustomUserSerializer

class RemarkSerializer(serializers.ModelSerializer):
    """
    Serializer for the Remark model.
    Includes read-only fields for author details.
    """
    author = CustomUserSerializer(read_only=True) # Nested serializer for author details

    class Meta:
        model = Remark
        fields = ['id', 'audit_request', 'author', 'comment', 'timestamp']
        read_only_fields = ['id', 'audit_request', 'author', 'timestamp'] # These are set by the view

class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model.
    Includes read-only fields for uploader details and full file URL.
    """
    uploaded_by = CustomUserSerializer(read_only=True) # Nested serializer for uploader details
    file_url = serializers.SerializerMethodField() # Custom field to get full URL

    class Meta:
        model = Document
        fields = ['id', 'audit_request', 'uploaded_by', 'document_type', 'file', 'file_url', 'upload_date', 'description']
        read_only_fields = ['id', 'audit_request', 'uploaded_by', 'upload_date', 'file_url'] # These are set by the view

    def get_file_url(self, obj):
        """
        Returns the absolute URL for the uploaded file.
        """
        if obj.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

class AuditRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the AuditRequest model.
    Includes nested serializers for related documents and remarks,
    and read-only fields for CSP details.
    """
    csp = CustomUserSerializer(read_only=True) # Nested serializer for CSP details
    documents = DocumentSerializer(many=True, read_only=True) # Nested serializer for documents
    remarks = RemarkSerializer(many=True, read_only=True) # Nested serializer for remarks
    
    # Custom field to get the display value of the status
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AuditRequest
        fields = [
            'id', 'csp', 'service_provider_name', 'data_center_location',
            'request_date', 'status', 'status_display', 'description', 'last_updated',
            'documents', 'remarks'
        ]
        read_only_fields = ['id', 'csp', 'request_date', 'status', 'status_display', 'last_updated', 'documents', 'remarks']

class AuditRequestStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating the status of an AuditRequest.
    """
    class Meta:
        model = AuditRequest
        fields = ['status']
