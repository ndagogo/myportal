from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Task, Applicant, Service

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'phone')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'service', 'assigned_to', 'time_allocated', 'application_form', 'supporting_docs')
        widgets = {
            'time_allocated': forms.TextInput(attrs={'type': 'time'}),
        }

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ('full_name', 'email', 'phone', 'address', 'additional_info')

class TaskDocumentForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('processed_document',)