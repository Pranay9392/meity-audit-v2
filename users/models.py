# Project: meity_audit_portal
# App: users
# File: users/models.py
# Description: Defines the CustomUser model with roles.

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Define roles as choices for better management
    ROLE_CHOICES = (
        ('CSP', 'Cloud Service Provider'),
        ('MeitY_Reviewer', 'MeitY Reviewer'),
        ('STQC_Auditor', 'STQC Auditor'),
        ('Scientist_F', 'Scientist F (Governing Authority)'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='CSP')
    organization = models.CharField(max_length=255, blank=True, null=True) # E.g., AWS, Azure, MeitY, STQC

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Helper properties for role-based access control
    @property
    def is_csp(self):
        return self.role == 'CSP'

    @property
    def is_meity_reviewer(self):
        return self.role == 'MeitY_Reviewer'

    @property
    def is_stqc_auditor(self):
        return self.role == 'STQC_Auditor'

    @property
    def is_scientist_f(self):
        return self.role == 'Scientist_F'

    # You can add more specific permissions if needed,
    # but for simple role checks, properties are convenient.
