# Project: meity_audit_portal
# App: audit_management
# File: audit_management/api_views.py
# Description: API views for AuditRequest, Document, and Remark models using Django REST Framework.

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser # For file uploads
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q # For complex queries

from .models import AuditRequest, Document, Remark
from .serializers import (
    AuditRequestSerializer,
    DocumentSerializer,
    RemarkSerializer,
    AuditRequestStatusUpdateSerializer
)
from users.models import CustomUser # Import CustomUser to check roles

# Helper functions for role-based access checks (ensure these are consistent with CustomUser model)
def is_csp(user):
    """Checks if the user is a Cloud Service Provider."""
    
    return user.is_authenticated and user.role == 'CSP'

def is_meity_reviewer(user):
    """Checks if the user is a MeitY Reviewer."""
    return user.is_authenticated and user.role == 'MeitY_Reviewer'

def is_stqc_auditor(user):
    """Checks if the user is an STQC Auditor."""
    return user.is_authenticated and user.role == 'STQC_Auditor'

def is_scientist_f(user):
    """Checks if the user is a Scientist F (Governing Authority)."""
    return user.is_authenticated and user.role == 'Scientist_F'

def is_meity_or_stqc_or_scientist_f(user):
    """Checks if the user is any of the reviewing/auditing roles."""
    return user.is_authenticated and (
        user.role == 'MeitY_Reviewer' or
        user.role == 'STQC_Auditor' or
        user.role == 'Scientist_F'
    )

class AuditRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing all audit requests and creating new ones.
    - GET: Lists audit requests based on user's role.
    - POST: Allows CSPs to create a new audit request.
    """
    serializer_class = AuditRequestSerializer
    permission_classes = [permissions.IsAuthenticated] # All users must be authenticated to access this API

    def get_queryset(self):
        
        """
        Filters audit requests based on the authenticated user's role.
        This ensures users only see requests relevant to them.
        Includes print statements for debugging empty querysets.
        """
        user = self.request.user
        queryset = AuditRequest.objects.none() # Default empty queryset

        if user.is_csp:
            print('pranay1')
            queryset = AuditRequest.objects.filter(csp=user).order_by('-last_updated')
            print(queryset)
            print('pranay')
            if not queryset.exists():
                print(f"Backend: No audit requests found for CSP '{user.username}'.")
        elif user.is_meity_reviewer:
            queryset = AuditRequest.objects.filter(
                Q(status='Submitted_by_CSP') |
                Q(status='Forwarded_to_STQC') |
                Q(status='Audit_Completed_by_STQC') |
                Q(status='Approved_by_ScientistF') |
                Q(status='Rejected_by_ScientistF')
            ).order_by('-last_updated')
            if not queryset.exists():
                print(f"Backend: No relevant audit requests found for MeitY Reviewer '{user.username}'.")
        elif user.is_stqc_auditor:
            queryset = AuditRequest.objects.filter(status='Forwarded_to_STQC').order_by('-last_updated')
            if not queryset.exists():
                print(f"Backend: No audit requests forwarded to STQC Auditor '{user.username}'.")
        elif user.is_scientist_f:
            queryset = AuditRequest.objects.all().order_by('-last_updated')
            if not queryset.exists():
                print(f"Backend: No audit requests found for Scientist F '{user.username}'.")
        else:
            print(f"Backend: No specific audit requests for user '{user.username}' with role '{user.role}'. Returning empty.")
            
        return queryset

    def perform_create(self, serializer):
        """
        Sets the CSP and initial status for new audit requests.
        Only CSPs can create audit requests.
        """
        user = self.request.user
        if not is_csp(user):
            # If the user is not a CSP, raise a permission denied error.
            # This is a critical security check.
            raise permissions.PermissionDenied("Only CSPs can create audit requests.")
        
        # Save the audit request, automatically assigning the logged-in CSP and initial status.
        audit_request = serializer.save(csp=user, status='Submitted_by_CSP')
        
        # Add an initial remark to log the submission of the request.
        Remark.objects.create(
            audit_request=audit_request,
            author=user,
            comment=f"Audit request submitted by CSP: {user.username}."
        )


class AuditRequestDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating a single audit request.
    - GET: Retrieves details of a specific audit request.
    - PUT/PATCH: Allows authorized users to update *certain* audit request details (e.g., description).
                 Status updates are handled by a separate, dedicated endpoint.
    """
    queryset = AuditRequest.objects.all()
    serializer_class = AuditRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Custom method to retrieve the object and enforce granular permissions.
        Ensures users can only access audit requests they are authorized to see.
        """
        obj = super().get_object() # Get the audit request object
        user = self.request.user
        

        # CSP can only view their own requests
        if user.is_csp and obj.csp != user:
            raise permissions.PermissionDenied("You do not have permission to view this audit request.")
        
        # MeitY Reviewer, STQC Auditor, Scientist F can view requests based on their general purview.
        # The `get_queryset` in the list view already filters what they can *see*.
        # Here, we ensure that if they somehow get an ID for a request outside their role's scope,
        # they are still denied. For simplicity, if they are any of these roles, they can view any request
        # that is *not* exclusively owned by another CSP they are not reviewing.
        # The `get_queryset` of the list view is the primary filter.
        if is_meity_or_stqc_or_scientist_f(user):
            # If the request is a CSP's request and this user is not the CSP,
            # we need to ensure the request is part of the workflow they are involved in.
            # This check is largely redundant if `get_queryset` is robust, but good for defense-in-depth.
            pass
        else:
            # If not a CSP (and not the owner), and not a reviewer/auditor/scientist, deny access.
            if not user.is_csp: # CSP case already handled above
                 raise permissions.PermissionDenied("You do not have permission to view this audit request.")

        return obj

    def perform_update(self, serializer):
        """
        Allows updates to fields other than status.
        Only CSP can update their own request's description if it's still in the initial state.
        This method is for general request data updates, not status changes.
        """
        user = self.request.user
        audit_request = self.get_object() # Ensures permission check is run by get_object()

        # Example: Only the owning CSP can update the description field
        # and only if the request is still in the 'Submitted_by_CSP' status.
        # This prevents CSPs from changing details after it's been forwarded.
        if user.is_csp and audit_request.csp == user and audit_request.status == 'Submitted_by_CSP':
            # The serializer's `read_only_fields` will prevent unauthorized updates to other fields.
            serializer.save()
            # Add a remark for the update
            Remark.objects.create(
                audit_request=audit_request,
                author=user,
                comment=f"CSP updated details for request #{audit_request.id}."
            )
        else:
            raise permissions.PermissionDenied(
                "You do not have permission to update this audit request at this stage or for this request."
            )


class DocumentUploadAPIView(generics.CreateAPIView):
    """
    API view for uploading documents related to an audit request.
    - POST: Allows CSPs and STQC Auditors to upload documents.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser] # Essential for handling file uploads (multipart/form-data)
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Associates the uploaded document with the correct audit request and uploader.
        Enforces role-based permissions and status-based restrictions for document uploads.
        """
        audit_request_pk = self.kwargs.get('audit_request_pk')
        audit_request = get_object_or_404(AuditRequest, pk=audit_request_pk)
        user = self.request.user

        # CSP can upload documents only for their own requests and when the status allows.
        if is_csp(user) and audit_request.csp == user:
            # CSPs can upload documents when the request is 'Submitted_by_CSP' (initial submission)
            # or 'Forwarded_to_STQC' (e.g., providing additional info requested by auditor).
            if audit_request.status in ['Submitted_by_CSP', 'Forwarded_to_STQC']:
                serializer.save(audit_request=audit_request, uploaded_by=user)
                Remark.objects.create(
                    audit_request=audit_request,
                    author=user,
                    comment=f"CSP uploaded a document of type '{serializer.validated_data.get('document_type')}'."
                )
            else:
                raise permissions.PermissionDenied(
                    f"CSPs can only upload documents when the request is in 'Submitted by CSP' or 'Forwarded to STQC' status. Current status: {audit_request.get_status_display()}."
                )
        
        # STQC Auditor can upload documents only when the request is 'Forwarded_to_STQC'.
        elif is_stqc_auditor(user) and audit_request.status == 'Forwarded_to_STQC':
            serializer.save(audit_request=audit_request, uploaded_by=user)
            Remark.objects.create(
                audit_request=audit_request,
                author=user,
                comment=f"STQC Auditor uploaded a document of type '{serializer.validated_data.get('document_type')}'."
            )
        else:
            raise permissions.PermissionDenied(
                f"You do not have permission to upload documents for this request at this stage. Current status: {audit_request.get_status_display()}."
            )

class DocumentDeleteAPIView(generics.DestroyAPIView):
    """
    API view for deleting a document.
    - DELETE: Allows the uploader of the document to delete it.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer # Using serializer for consistency, though not strictly needed for DELETE
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Ensures only the document uploader can delete their document.
        """
        obj = super().get_object()
        if obj.uploaded_by != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to delete this document.")
        return obj

    def perform_destroy(self, instance):
        """
        Performs the deletion and logs a remark.
        """
        audit_request = instance.audit_request
        document_type = instance.document_type
        instance.delete()
        Remark.objects.create(
            audit_request=audit_request,
            author=self.request.user,
            comment=f"Document of type '{document_type}' deleted by {self.request.user.username}."
        )


class RemarkCreateAPIView(generics.CreateAPIView):
    """
    API view for creating a new remark for an audit request.
    - POST: Allows MeitY Reviewers, STQC Auditors, and Scientist F to add remarks.
    """
    queryset = Remark.objects.all()
    serializer_class = RemarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Associates the remark with the correct audit request and author.
        Enforces role-based permissions for adding remarks.
        """
        audit_request_pk = self.kwargs.get('audit_request_pk')
        audit_request = get_object_or_404(AuditRequest, pk=audit_request_pk)
        user = self.request.user

        if not is_meity_or_stqc_or_scientist_f(user):
            raise permissions.PermissionDenied("Only MeitY Reviewers, STQC Auditors, or Scientist F can add remarks.")
        
        # Save the remark, associating it with the audit request and the logged-in user.
        serializer.save(audit_request=audit_request, author=user)


class AuditRequestStatusUpdateAPIView(generics.UpdateAPIView):
    """
    API view for updating the status of an audit request.
    - PATCH: Allows specific roles to transition the status.
    """
    queryset = AuditRequest.objects.all()
    serializer_class = AuditRequestStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch'] # Explicitly allow only PATCH for status updates

    def get_object(self):
        """
        Retrieves the audit request object and enforces role-based permissions
        for initiating a status update.
        """
        obj = super().get_object() # Get the audit request object
        user = self.request.user

        # Check if the user's role and the current status allow for a status update.
        can_update = False
        if is_meity_reviewer(user) and obj.status == 'Submitted_by_CSP':
            can_update = True
        elif is_stqc_auditor(user) and obj.status == 'Forwarded_to_STQC':
            can_update = True
        elif is_scientist_f(user) and obj.status == 'Audit_Completed_by_STQC':
            can_update = True
        
        if not can_update:
            raise permissions.PermissionDenied(
                f"You do not have permission to change the status of this audit request at its current stage ({obj.get_status_display()})."
            )
        
        return obj

    def partial_update(self, request, *args, **kwargs):
        """
        Handles the PATCH request for status update.
        Includes server-side validation for valid status transitions based on business logic.
        """
        instance = self.get_object() # This will run the `get_object` permission check first.
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True) # Validate incoming data (only 'status' field)

        new_status = serializer.validated_data.get('status')
        user = request.user

        # Further, explicit server-side validation for allowed status transitions.
        # This is crucial for maintaining workflow integrity.
        valid_transition = False
        remark_text = ""

        if is_meity_reviewer(user) and instance.status == 'Submitted_by_CSP' and new_status == 'Forwarded_to_STQC':
            valid_transition = True
            remark_text = f"MeitY Reviewer forwarded request to STQC. Status changed to '{AuditRequest.STATUS_CHOICES[1][1]}'."
        elif is_stqc_auditor(user) and instance.status == 'Forwarded_to_STQC' and new_status == 'Audit_Completed_by_STQC':
            valid_transition = True
            remark_text = f"STQC Auditor marked audit as completed. Status changed to '{AuditRequest.STATUS_CHOICES[2][1]}'."
        elif is_scientist_f(user) and instance.status == 'Audit_Completed_by_STQC' and \
             (new_status == 'Approved_by_ScientistF' or new_status == 'Rejected_by_ScientistF'):
            valid_transition = True
            # Get the display name for the new status for the remark
            new_status_display = dict(AuditRequest.STATUS_CHOICES).get(new_status, new_status)
            remark_text = f"Scientist F made final decision: '{new_status_display}'."
        
        if not valid_transition:
            # If the requested transition is not allowed, return a 400 Bad Request.
            return Response(
                {"detail": "Invalid status transition for your role or current request status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_update(serializer) # Save the new status to the database.
        
        # Add a remark to log the status change.
        Remark.objects.create(
            audit_request=instance,
            author=user,
            comment=remark_text
        )

        return Response(serializer.data) # Return the updated audit request data
