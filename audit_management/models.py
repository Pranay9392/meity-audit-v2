# Project: meity_audit_portal
# App: audit_management
# File: audit_management/models.py
# Description: Defines models for AuditRequest, Remark, and Document.


# audit_management/models.py






# Project: meity_audit_portal
# App: audit_management
# File: audit_management/models.py
# Description: Django models for the audit management system.

from django.db import models
from django.conf import settings

# A list of choices for the status field on an AuditRequest.
STATUS_CHOICES = (
    ('Submitted_by_CSP', 'Submitted by CSP'), # Initial state
    ('Forwarded_to_STQC', 'Forwarded to STQC for Audit'), # After MeitY Reviewer forwards
    ('Audit_Completed_by_STQC', 'Audit Completed by STQC'), # After STQC Auditor completes
    ('Approved_by_ScientistF', 'Approved by Scientist F'), # Final approval
    ('Rejected_by_ScientistF', 'Rejected by Scientist F'), # Final rejection
)

class AuditRequest(models.Model):
    """
    Represents an audit request submitted by a CSP.
    """
    # The ForeignKey to the CSP user. The related_name 'audit_requests' allows
    # us to easily get all audit requests for a given CSP.
    # The 'limit_choices_to' ensures only CSP users can be linked.

    STATUS_CHOICES = (
        ('Submitted_by_CSP', 'Submitted by CSP'), # Initial state
        ('Forwarded_to_STQC', 'Forwarded to STQC for Audit'), # After MeitY Reviewer forwards
        ('Audit_Completed_by_STQC', 'Audit Completed by STQC'), # After STQC Auditor completes
        ('Approved_by_ScientistF', 'Approved by Scientist F'), # Final approval
        ('Rejected_by_ScientistF', 'Rejected by Scientist F'), # Final rejection
    )

    csp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            limit_choices_to={'role': 'CSP'}, related_name='audit_requests')
    service_provider_name = models.CharField(max_length=255, help_text="Name of the Cloud Service Provider")
    data_center_location = models.CharField(max_length=255)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted_by_CSP')
    description = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Field to store the Certificate of Empanelment file
    certificate_of_empanelment = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Audit Request for {self.service_provider_name} - {self.get_status_display()} (ID: {self.id})"

    class Meta:
        ordering = ['-request_date'] # Order by most recent requests first


class Document(models.Model):
    """
    Represents a document attached to an audit request.
    Can be uploaded by CSP or STQC Auditor.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('CSP_Submission', 'CSP Submission'),
        ('Audit_Report', 'Audit Report'),
        ('Other', 'Other'),
    )

    audit_request = models.ForeignKey(AuditRequest, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='audit_documents/') # Files will be stored in MEDIA_ROOT/audit_documents/
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Document for Request {self.audit_request.id} - {self.get_document_type_display()} by {self.uploaded_by.username}"

    class Meta:
        ordering = ['-upload_date']


class Remark(models.Model):
    """
    Represents remarks or comments on an audit request by various roles.
    """
    audit_request = models.ForeignKey(AuditRequest, on_delete=models.CASCADE, related_name='remarks')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remark by {self.author.username} on Request {self.audit_request.id}"

    class Meta:
        ordering = ['timestamp']













# from django.db import models
# from django.conf import settings

# class AuditRequest(models.Model):
#     """
#     Represents an audit request submitted by a CSP.
#     """
#     STATUS_CHOICES = (
#         ('Submitted_by_CSP', 'Submitted by CSP'), # Initial state
#         ('Forwarded_to_STQC', 'Forwarded to STQC for Audit'), # After MeitY Reviewer forwards
#         ('Audit_Completed_by_STQC', 'Audit Completed by STQC'), # After STQC Auditor completes
#         ('Approved_by_ScientistF', 'Approved by Scientist F'), # Final approval
#         ('Rejected_by_ScientistF', 'Rejected by Scientist F'), # Final rejection
#     )

#     csp = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
#                             limit_choices_to={'role': 'CSP'}, related_name='audit_requests')
#     service_provider_name = models.CharField(max_length=255, help_text="Name of the Cloud Service Provider")
#     data_center_location = models.CharField(max_length=255)
#     request_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted_by_CSP')
#     description = models.TextField(blank=True, null=True)
#     last_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Audit Request for {self.service_provider_name} - {self.get_status_display()} (ID: {self.id})"

#     class Meta:
#         ordering = ['-request_date'] # Order by most recent requests first


# class Document(models.Model):
#     """
#     Represents a document attached to an audit request.
#     Can be uploaded by CSP or STQC Auditor.
#     """
#     DOCUMENT_TYPE_CHOICES = (
#         ('CSP_Submission', 'CSP Submission'),
#         ('Audit_Report', 'Audit Report'),
#         ('Other', 'Other'),
#     )

#     audit_request = models.ForeignKey(AuditRequest, on_delete=models.CASCADE, related_name='documents')
#     uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
#     file = models.FileField(upload_to='audit_documents/') # Files will be stored in MEDIA_ROOT/audit_documents/
#     upload_date = models.DateTimeField(auto_now_add=True)
#     description = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"Document for Request {self.audit_request.id} - {self.get_document_type_display()} by {self.uploaded_by.username}"

#     class Meta:
#         ordering = ['-upload_date']


# class Remark(models.Model):
#     """
#     Represents remarks or comments on an audit request by various roles.
#     """
#     audit_request = models.ForeignKey(AuditRequest, on_delete=models.CASCADE, related_name='remarks')
#     author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     comment = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Remark by {self.author.username} on Request {self.audit_request.id}"

#     class Meta:
#         ordering = ['timestamp']


# # --- UPDATED: This is the key change here. ---
#     # Field to store the Certificate of Empanelment file
# class AuditRequest(models.Model):
#     # ...
#     certificate_of_empanelment = models.FileField(
#         upload_to='certificates/',
#         null=True,
#         blank=True
#     )
