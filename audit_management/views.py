# Project: meity_audit_portal
# App: audit_management
# File: audit_management/views.py
# Description: Handles audit request creation, listing, detail views, document uploads, remarks, and status updates, including document deletion.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q # For complex queries
# Removed JsonResponse and render_to_string for non-AJAX approach

from .forms import AuditRequestForm, DocumentUploadForm, RemarkForm, AuditRequestStatusUpdateForm
from .models import AuditRequest, Document, Remark
from users.models import CustomUser # Import CustomUser to check roles

# Helper functions for role-based access checks
def is_csp(user):
    """Checks if the user is a Cloud Service Provider."""
    return user.is_authenticated and user.is_csp

def is_meity_reviewer(user):
    """Checks if the user is a MeitY Reviewer."""
    return user.is_authenticated and user.is_meity_reviewer

def is_stqc_auditor(user):
    """Checks if the user is an STQC Auditor."""
    return user.is_authenticated and user.is_stqc_auditor

def is_scientist_f(user):
    """Checks if the user is a Scientist F (Governing Authority)."""
    return user.is_authenticated and user.is_scientist_f

def is_meity_or_stqc_or_scientist_f(user):
    """Checks if the user is any of the reviewing/auditing roles."""
    return user.is_meity_reviewer or user.is_stqc_auditor or user.is_scientist_f

@login_required
@user_passes_test(is_csp, login_url='dashboard') # Only CSPs can create requests
def create_audit_request(request):
    """
    Allows CSPs to submit a new audit request.
    Initializes the audit request status to 'Submitted_by_CSP'.
    """
    if request.method == 'POST':
        form = AuditRequestForm(request.POST)
        if form.is_valid():
            audit_request = form.save(commit=False)
            audit_request.csp = request.user # Assign the logged-in CSP as the requestor
            audit_request.status = 'Submitted_by_CSP' # Set initial status
            audit_request.save()
            # Add an initial remark to track the submission
            Remark.objects.create(
                audit_request=audit_request,
                author=request.user,
                comment=f"Audit request submitted by CSP: {audit_request.csp.username}."
            )
            messages.success(request, 'Audit request submitted successfully! It is now awaiting MeitY Review.')
            # Redirect to the detail page of the newly created request
            return redirect('audit_request_detail', pk=audit_request.pk)
        else:
            # Add form errors to messages for display
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AuditRequestForm() # Empty form for GET request
    return render(request, 'audit_management/create_audit_request.html', {'form': form})

@login_required
def audit_request_list(request):
    """
    Displays a list of audit requests relevant to the logged-in user's role.
    Filters requests based on role-specific access permissions.
    """
    # Initialize querysets as empty
    pending_requests = AuditRequest.objects.none()
    reviewed_requests = AuditRequest.objects.none()
    
    # Start with all audit requests for generic filtering, then apply role-specific logic
    audit_requests_all = AuditRequest.objects.all()

    # Apply role-based filtering
    if request.user.is_csp:
        # CSPs see only their own submitted requests
        audit_requests = audit_requests_all.filter(csp=request.user)
    elif request.user.is_meity_reviewer:
        # MeitY Reviewers see requests ready for their review (Submitted by CSP)
        pending_requests = audit_requests_all.filter(status='Submitted_by_CSP')
        # MeitY Reviewers also see requests they've already "reviewed" (i.e., forwarded or moved past their stage)
        reviewed_requests = audit_requests_all.filter(
            Q(status='Forwarded_to_STQC') | 
            Q(status='Audit_Completed_by_STQC') |
            Q(status='Approved_by_ScientistF') |
            Q(status='Rejected_by_ScientistF')
        )
        audit_requests = pending_requests # Default list for display if not explicitly handled
    elif request.user.is_stqc_auditor:
        # STQC Auditors see requests forwarded to them for audit
        audit_requests = audit_requests_all.filter(status='Forwarded_to_STQC')
        print(f"STQC Auditor: Filtering for status 'Forwarded_to_STQC'. Found {audit_requests.count()} requests.") # DEBUG
        for req in audit_requests: # DEBUG
            print(f"  - Request ID: {req.id}, Current Status: {req.status}") # DEBUG
    elif request.user.is_scientist_f:
        # Scientist F sees all requests, no additional filtering applied
        audit_requests = audit_requests_all # Scientist F views all requests
    else:
        # Should ideally not be reached due to @login_required and role checks,
        # but provides a safe fallback for unrecognized roles.
        messages.error(request, "Access denied. Your role cannot view audit requests.")
        return redirect('dashboard')

    context = {
        'audit_requests': audit_requests, # This remains the main list for non-MeitY roles
        'pending_requests': pending_requests, # Specific for MeitY reviewer
        'reviewed_requests': reviewed_requests, # Specific for MeitY reviewer
    }
    return render(request, 'audit_management/audit_request_list.html', context)


@login_required
def audit_request_detail(request, pk):
    """
    Displays the detailed view of a specific audit request.
    Manages forms for adding remarks, uploading documents, and updating status,
    with forms displayed conditionally based on user role and request status.
    Uses traditional form submissions (full page reload).
    """
    audit_request = get_object_or_404(AuditRequest, pk=pk)

    # Initialize forms
    remark_form = RemarkForm()
    document_form = DocumentUploadForm()
    status_form = None # Will be initialized conditionally
    status_form_title = ""
    status_submit_button_text = "Update Status"

    # Handle POST requests
    if request.method == 'POST':
        print(f"POST request received for Audit Request {pk}. Action: {list(request.POST.keys())}") # DEBUG
        # Determine which form was submitted based on the button's 'name' attribute
        if 'add_remark' in request.POST:
            remark_form = RemarkForm(request.POST)
            if is_meity_or_stqc_or_scientist_f(request.user):
                if remark_form.is_valid():
                    remark = remark_form.save(commit=False)
                    remark.audit_request = audit_request
                    remark.author = request.user
                    remark.save()
                    messages.success(request, 'Remark added successfully!')
                    print(f"Remark added by {request.user.username} to request {pk}.") # DEBUG
                else:
                    messages.error(request, 'Error adding remark. Please check the form.')
                    print(f"Remark form invalid. Errors: {remark_form.errors}") # DEBUG
            else:
                messages.error(request, 'You are not authorized to add remarks.')
                print(f"Unauthorized attempt to add remark by {request.user.username}.") # DEBUG
            return redirect('audit_request_detail', pk=pk)

        elif 'upload_document' in request.POST:
            document_form = DocumentUploadForm(request.POST, request.FILES)
            # Check for CSP permissions
            if request.user.is_csp and request.user == audit_request.csp:
                if document_form.is_valid():
                    document = document_form.save(commit=False)
                    document.audit_request = audit_request
                    document.uploaded_by = request.user
                    document.save()
                    messages.success(request, 'Document uploaded successfully!')
                    print(f"Document uploaded by CSP {request.user.username} to request {pk}.") # DEBUG
                else:
                    messages.error(request, 'Error uploading document. Please check the form.')
                    print(f"CSP document upload form invalid. Errors: {document_form.errors}") # DEBUG
            # Check for STQC Auditor permissions
            elif request.user.is_stqc_auditor and audit_request.status == 'Forwarded_to_STQC':
                 if document_form.is_valid():
                    document = document_form.save(commit=False)
                    document.audit_request = audit_request
                    document.uploaded_by = request.user
                    document.save()
                    messages.success(request, 'Document uploaded successfully!')
                    print(f"Document uploaded by STQC Auditor {request.user.username} to request {pk}.") # DEBUG
                 else:
                    messages.error(request, 'Error uploading document. Please check the form.')
                    print(f"STQC document upload form invalid. Errors: {document_form.errors}") # DEBUG
            else:
                messages.error(request, 'You are not authorized to upload documents at this stage or for this request.')
                print(f"Unauthorized attempt to upload document by {request.user.username}.") # DEBUG
            return redirect('audit_request_detail', pk=pk)


        elif 'update_status' in request.POST:
            print(f"Update Status initiated by {request.user.username} ({request.user.role}) for request {pk}.") # DEBUG
            # Re-fetch the audit_request instance from the database
            # to ensure we are working with the most current status.
            audit_request = get_object_or_404(AuditRequest, pk=pk)
            print(f"Current Audit Request Status from DB: {audit_request.status}") # DEBUG
            status_form = AuditRequestStatusUpdateForm(request.POST, instance=audit_request, user=request.user, current_status=audit_request.status)
            
            print(f"Status Form is valid: {status_form.is_valid()}") # DEBUG
            if status_form.is_valid():
                new_status = status_form.cleaned_data['status']
                print(f"New Status selected in form: {new_status}") # DEBUG
                
                can_update = False
                success_message = ""
                remark_text = ""

                # Server-side validation for status transitions based on role and current status
                if request.user.is_meity_reviewer:
                    if audit_request.status == 'Submitted_by_CSP' or audit_request.status == 'Forwarded_to_STQC' and new_status == 'Forwarded_to_STQC': # RECTIFIED THE BUG OF STATUS CHANGE WITH KEEPING OR
                        can_update = True
                        success_message = 'Audit request successfully forwarded to STQC for auditing!'
                        remark_text = f"MeitY Reviewer forwarded request to STQC. Status changed to '{AuditRequest.STATUS_CHOICES[1][1]}'."
                        print(f"MeitY Reviewer: Conditions met for forwarding. Can update = {can_update}") # DEBUG
                    else:
                        messages.error(request, f'MeitY Reviewers can only forward requests in "Submitted by CSP" status. This request is currently in "{audit_request.get_status_display()}" status. Cannot forward.')
                        print(f"MeitY Reviewer: Conditions NOT met. Current status: {audit_request.status}, New status requested: {new_status}") # DEBUG
                        
                elif request.user.is_stqc_auditor:
                    if audit_request.status == 'Forwarded_to_STQC' or audit_request.status == 'Audit_Completed_by_STQC' and new_status == 'Audit_Completed_by_STQC':
                        can_update = True
                        success_message = 'Audit completed by STQC Auditor. Now awaiting Scientist F review.'
                        remark_text = f"STQC Auditor marked audit as completed. Status changed to '{AuditRequest.STATUS_CHOICES[2][1]}'."
                        print(f"STQC Auditor: Conditions met for completing audit. Can update = {can_update}") # DEBUG
                    else:
                        messages.error(request, f'STQC Auditors can only mark requests that are "Forwarded to STQC" as "Audit Completed". This request is currently in "{audit_request.get_status_display()}" status.')
                        print(f"STQC Auditor: Conditions NOT met. Current status: {audit_request.status}, New status requested: {new_status}") # DEBUG

                elif request.user.is_scientist_f:
                    if (audit_request.status == 'Audit_Completed_by_STQC' or audit_request.status == 'Approved_by_ScientistF' and new_status == 'Approved_by_ScientistF') or \
                       (audit_request.status == 'Audit_Completed_by_STQC' or audit_request.status == 'Rejected_by_ScientistF' and new_status == 'Rejected_by_ScientistF'):
                        can_update = True
                        success_message = f'Audit request {audit_request.get_status_display().lower()} successfully!'
                        remark_text = f"Scientist F made final decision: '{audit_request.get_status_display()}'."
                        print(f"Scientist F: Conditions met for final decision. Can update = {can_update}") # DEBUG
                    else:
                        messages.error(request, f'Scientist F can only approve/reject requests that are "Audit Completed by STQC". This request is currently in "{audit_request.get_status_display()}" status.')
                        print(f"Scientist F: Conditions NOT met. Current status: {audit_request.status}, New status requested: {new_status}") # DEBUG
                
                else:
                    messages.error(request, 'You do not have permission to change the status of this audit request.')
                    print(f"Unauthorized attempt to change status by {request.user.username}.") # DEBUG

                if can_update:
                    status_form.save() # This saves the new status to the database
                    Remark.objects.create(audit_request=audit_request, author=request.user, comment=remark_text)
                    messages.success(request, success_message)
                    print(f"Audit Request {audit_request.pk} status saved to: {audit_request.status}. Redirecting to list.") # DEBUG
                    # After successful status update, redirect to the list page to clearly show the change
                    return redirect('audit_request_list') 
                else:
                    # If update was not allowed or form invalid, stay on the detail page and show error
                    print(f"Update NOT allowed for request {pk}. Redirecting to detail.") # DEBUG
                    return redirect('audit_request_detail', pk=pk)
            else:
                messages.error(request, 'Error updating status. Please check the form.')
                print(f"Status form invalid. Errors: {status_form.errors}") # DEBUG
                return redirect('audit_request_detail', pk=pk)


    # For GET requests or after a failed POST, prepare forms and context
    # Re-fetch audit_request to ensure it's fresh if a POST occurred
    audit_request = get_object_or_404(AuditRequest, pk=pk)
    documents = audit_request.documents.all()
    remarks = audit_request.remarks.all()

    # Conditionally prepare the status update form for GET requests (or re-rendering after failed POST)
    if request.user.is_meity_reviewer and audit_request.status == 'Submitted_by_CSP':
        status_form = AuditRequestStatusUpdateForm(instance=audit_request, user=request.user, current_status=audit_request.status)
        status_form_title = "Action: Forward to STQC for Audit"
        status_submit_button_text = "Forward to STQC"
    elif request.user.is_stqc_auditor and audit_request.status == 'Forwarded_to_STQC':
        status_form = AuditRequestStatusUpdateForm(instance=audit_request, user=request.user, current_status=audit_request.status)
        status_form_title = "Action: Mark Audit as Completed"
        status_submit_button_text = "Mark Audit Completed"
    elif request.user.is_scientist_f and audit_request.status == 'Audit_Completed_by_STQC':
        status_form = AuditRequestStatusUpdateForm(instance=audit_request, user=request.user, current_status=audit_request.status)
        status_form_title = "Action: Finalize Audit Decision"
        status_submit_button_text = "Finalize Decision"
    
    context = {
        'audit_request': audit_request,
        'documents': documents,
        'remarks': remarks,
        'remark_form': remark_form,
        'document_form': document_form,
        'status_form': status_form, # This will be None if no form applies
        'status_form_title': status_form_title,
        'status_submit_button_text': status_submit_button_text,
    }
    return render(request, 'audit_management/audit_request_detail.html', context)

@login_required
def delete_document(request, pk):
    """
    Allows the user who uploaded a document to delete it.
    Ensures only the uploader can delete their document.
    """
    document = get_object_or_404(Document, pk=pk)
    audit_request_pk = document.audit_request.pk # Get PK before deleting document

    if request.user == document.uploaded_by:
        document.delete()
        messages.success(request, 'Document deleted successfully!')
    else:
        messages.error(request, 'You are not authorized to delete this document.')
    
    return redirect('audit_request_detail', pk=audit_request_pk)
