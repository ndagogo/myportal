from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import *
from .forms import *
from django.contrib.auth import logout

# Permission decorators
def is_admin(user):
    return user.user_type in ['admin', 'super_admin']

def is_staff(user):
    return user.user_type == 'staff'

def is_partner(user):
    return user.user_type == 'partner'

def is_super_admin(user):
    return user.user_type == 'super_admin'

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.user_type in ['admin', 'super_admin']:
        tasks = Task.objects.filter(assigned_by=user)
        pending_tasks = tasks.filter(status='pending').count()
        processing_tasks = tasks.filter(status='processing').count()
        context.update({
            'pending_tasks': pending_tasks,
            'processing_tasks': processing_tasks,
            'recent_tasks': tasks.order_by('-created_at')[:5]
        })
    elif user.user_type == 'staff':
        tasks = Task.objects.filter(assigned_to=user)
        pending_tasks = tasks.filter(status='pending').count()
        processing_tasks = tasks.filter(status='processing').count()
        context.update({
            'pending_tasks': pending_tasks,
            'processing_tasks': processing_tasks,
            'recent_tasks': tasks.order_by('-created_at')[:5]
        })
    elif user.user_type == 'partner':
        tasks = Task.objects.filter(assigned_by=user)
        context.update({
            'recent_tasks': tasks.order_by('-created_at')[:5]
        })
    
    return render(request, 'portal/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def create_task(request):
    if request.method == 'POST':
        task_form = TaskForm(request.POST, request.FILES)
        applicant_form = ApplicantForm(request.POST)
        
        if task_form.is_valid() and applicant_form.is_valid():
            with transaction.atomic():
                task = task_form.save(commit=False)
                task.assigned_by = request.user
                task.save()
                
                applicant = applicant_form.save(commit=False)
                applicant.task = task
                applicant.save()
                
                # Send notification to assigned staff
                notification = Notification.objects.create(
                    user=task.assigned_to,
                    message=f'You have a new task "{task.title}" from {request.user.get_full_name()}. Please accept or decline.',
                    related_task=task
                )
                
                # Send email and SMS (pseudo-code)
                # send_notification(task.assigned_to, 'new_task', task)
                
            messages.success(request, 'Task created successfully and assigned to staff.')
            return redirect('task_list')
    else:
        task_form = TaskForm()
        applicant_form = ApplicantForm()
    
    return render(request, 'portal/create_task.html', {
        'task_form': task_form,
        'applicant_form': applicant_form
    })

@login_required
@user_passes_test(is_staff)
def task_action(request, task_id, action):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    
    if action == 'accept' and task.status == 'pending':
        task.status = 'accepted'
        task.time_accepted = timezone.now()
        task.save()
        
        # Notify admin
        Notification.objects.create(
            user=task.assigned_by,
            message=f'{request.user.get_full_name()} has accepted the task "{task.title}".',
            related_task=task
        )
        # send_notification(task.assigned_by, 'task_accepted', task)
        
        messages.success(request, 'Task accepted successfully.')
    
    elif action == 'decline' and task.status == 'pending':
        task.status = 'declined'
        task.save()
        
        # Notify admin
        Notification.objects.create(
            user=task.assigned_by,
            message=f'{request.user.get_full_name()} has declined the task "{task.title}".',
            related_task=task
        )
        # send_notification(task.assigned_by, 'task_declined', task)
        
        messages.success(request, 'Task declined successfully.')
    
    elif action == 'complete' and task.status in ['accepted', 'processing', 'queried']:
        task.status = 'completed'
        task.time_completed = timezone.now()
        task.save()
        
        # Notify admin
        Notification.objects.create(
            user=task.assigned_by,
            message=f'{request.user.get_full_name()} has completed the task "{task.title}". Please review.',
            related_task=task
        )
        # send_notification(task.assigned_by, 'task_completed', task)
        
        messages.success(request, 'Task marked as completed successfully.')
    
    return redirect('task_detail', task_id=task_id)

@login_required
def update_task_document(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if not (request.user == task.assigned_to or request.user == task.assigned_by):
        messages.error(request, 'You do not have permission to update this task.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TaskDocumentForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            
            if request.user == task.assigned_to:
                task.status = 'processing'
                task.save()
            
            messages.success(request, 'Document updated successfully.')
            return redirect('task_detail', task_id=task_id)
    else:
        form = TaskDocumentForm(instance=task)
    
    return render(request, 'portal/update_document.html', {'form': form, 'task': task})

@login_required
@user_passes_test(is_admin)
def approve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_by=request.user)
    
    if task.status == 'completed':
        task.status = 'approved'
        task.time_approved = timezone.now()
        task.save()
        
        # Credit staff's wallet
        credit_amount = task.service.fee * Decimal('0.7')  # Example: 70% of service fee
        staff = task.assigned_to
        staff.wallet_balance += credit_amount
        staff.save()
        
        # Record transaction
        Transaction.objects.create(
            user=staff,
            task=task,
            amount=credit_amount,
            transaction_type='credit',
            description=f'Payment for completing task: {task.title}'
        )
        
        # Notify staff
        Notification.objects.create(
            user=task.assigned_to,
            message=f'Your task "{task.title}" has been approved. Your wallet has been credited with ${credit_amount}.',
            related_task=task
        )
        # send_notification(task.assigned_to, 'task_approved', task)
        
        messages.success(request, 'Task approved and staff payment processed.')
    
    return redirect('task_detail', task_id=task_id)

@login_required
@user_passes_test(is_admin)
def query_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_by=request.user)
    
    if request.method == 'POST':
        query_reason = request.POST.get('query_reason')
        if query_reason:
            task.status = 'queried'
            task.query_reason = query_reason
            task.query_resolved = False
            task.save()
            
            # Notify staff
            Notification.objects.create(
                user=task.assigned_to,
                message=f'Your task "{task.title}" has been queried. Reason: {query_reason}',
                related_task=task
            )
            # send_notification(task.assigned_to, 'task_queried', task)
            
            messages.success(request, 'Task queried successfully.')
            return redirect('task_detail', task_id=task_id)
    
    return render(request, 'portal/query_task.html', {'task': task})

# Additional views for task list, detail, etc.
@login_required
def task_list(request):
    if request.user.user_type in ['admin', 'super_admin']:
        tasks = Task.objects.filter(assigned_by=request.user)
    elif request.user.user_type == 'staff':
        tasks = Task.objects.filter(assigned_to=request.user)
    elif request.user.user_type == 'partner':
        tasks = Task.objects.filter(assigned_by=request.user)
    else:
        tasks = Task.objects.none()
    
    return render(request, 'portal/task_list.html', {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check if user has permission to view this task
    if not (request.user == task.assigned_to or request.user == task.assigned_by):
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('dashboard')
    
    return render(request, 'portal/task_detail.html', {'task': task})

def custom_logout(request):
    logout(request)
    return redirect('login')