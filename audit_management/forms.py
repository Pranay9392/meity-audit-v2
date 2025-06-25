# Project: meity_audit_portal
# App: audit_management
# File: audit_management/forms.py
# Description: Defines forms for AuditRequest, Document, and Remark, including dynamic status choices.

from django import forms
from .models import AuditRequest, Document, Remark

class AuditRequestForm(forms.ModelForm):
    """
    Form for Cloud Service Providers (CSPs) to create a new Audit Request.
    """
    class Meta:
        model = AuditRequest
        # CSPs should only submit these fields
        fields = ['service_provider_name', 'data_center_location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), # Make textarea larger
        }
        labels = {
            'service_provider_name': 'Cloud Service Provider Name',
            'data_center_location': 'Data Center Location (e.g., Mumbai, Chennai)',
            'description': 'Description of Services/Scope of Audit (Optional)',
        }
        help_texts = {
            'description': 'Provide any additional details relevant to the audit request.',
        }

class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading documents related to an Audit Request.
    """
    class Meta:
        model = Document
        fields = ['document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'document_type': 'Type of Document',
            'file': 'Select File',
            'description': 'Brief description of the document (Optional)',
        }
        help_texts = {
            'file': 'Supported formats: PDF, JPG, PNG.',
        }

class RemarkForm(forms.ModelForm):
    """
    Form for adding remarks to an Audit Request.
    """
    class Meta:
        model = Remark
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'comment': 'Your Remark',
        }

class AuditRequestStatusUpdateForm(forms.ModelForm):
    """
    Form for updating the status of an Audit Request.
    Dynamically sets choices based on the user's role and current request status
    to enforce workflow transitions.
    """
    class Meta:
        model = AuditRequest
        fields = ['status']
        labels = {
            'status': 'Update Status',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        current_status = kwargs.pop('current_status', None)
        super().__init__(*args, **kwargs)

        # Get all status choices from the model
        all_choices = AuditRequest.STATUS_CHOICES
        available_choices = []

        if user:
            if user.is_meity_reviewer and current_status == 'Submitted_by_CSP':
                # MeitY Reviewer can only forward to STQC Audit
                available_choices = [('Forwarded_to_STQC', 'Forward to STQC for Audit')]
            elif user.is_stqc_auditor and current_status == 'Forwarded_to_STQC':
                # STQC Auditor can only mark as Audit Completed
                available_choices = [('Audit_Completed_by_STQC', 'Audit Completed')]
            elif user.is_scientist_f and current_status == 'Audit_Completed_by_STQC':
                # Scientist F can Approve or Reject completed audits
                available_choices = [
                    ('Approved_by_ScientistF', 'Approve Audit'),
                    ('Rejected_by_ScientistF', 'Reject Audit')
                ]
            
        if available_choices:
            # Add the current status as the default selected option if it's not already there
            current_choice_display = dict(all_choices).get(current_status, current_status)
            if (current_status, current_choice_display) not in available_choices:
                # Only add if not already present and if it makes sense to show as "current"
                # This ensures the list only contains valid transitions + current status (if not a transition option)
                pass # The view will handle if no form is presented at all.
            self.fields['status'].choices = available_choices
        else:
            # If no valid transitions for the current user/status, hide the field
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['status'].required = False
            # Optionally, if you still want to show the current status as read-only, you could do:
            # self.fields['status'].initial = current_status
            # self.fields['status'].widget.attrs['disabled'] = 'disabled' # Makes it read-only
            # self.fields['status'].widget.attrs['class'] = 'form-control-plaintext' # Style as plain text
