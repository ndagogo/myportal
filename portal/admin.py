from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task, Applicant, Service, Notification, Transaction

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'phone', 'is_verified', 'wallet_balance')
    list_filter = ('user_type', 'is_verified')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'phone', 'wallet_balance', 'is_verified')}),
    )

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', 'assigned_by', 'assigned_to', 'status', 'created_at')
    list_filter = ('status', 'service', 'created_at')
    search_fields = ('title', 'assigned_by__username', 'assigned_to__username')

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone')
    search_fields = ('full_name', 'email', 'phone')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Service)
admin.site.register(Notification)
admin.site.register(Transaction)