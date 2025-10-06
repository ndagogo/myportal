from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal
import os

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('partner', 'Partner'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='staff')
    phone = models.CharField(max_length=15, blank=True, null=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

def application_upload_path(instance, filename):
    return f'applications/task_{instance.task.id}/{filename}'

class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Acceptance'),
        ('accepted', 'Accepted'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
        ('queried', 'Queried'),
        ('declined', 'Declined'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(CustomUser, related_name='tasks_assigned', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='tasks_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    time_allocated = models.DurationField()  # Time allocated for completion
    time_accepted = models.DateTimeField(null=True, blank=True)
    time_completed = models.DateTimeField(null=True, blank=True)
    time_approved = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Document fields
    application_form = models.FileField(upload_to=application_upload_path)
    supporting_docs = models.FileField(upload_to=application_upload_path, blank=True, null=True)
    processed_document = models.FileField(upload_to=application_upload_path, blank=True, null=True)
    
    # Query fields
    query_reason = models.TextField(blank=True)
    query_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def get_time_remaining(self):
        if self.status == 'accepted' and self.time_accepted:
            # Calculate remaining time logic
            pass
        return None

class Applicant(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='applicant')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    additional_info = models.JSONField(default=dict)  # For flexible field storage
    
    def __str__(self):
        return self.full_name

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"