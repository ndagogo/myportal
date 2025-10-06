from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/action/<str:action>/', views.task_action, name='task_action'),
    path('tasks/<int:task_id>/update-document/', views.update_task_document, name='update_task_document'),
    path('tasks/<int:task_id>/approve/', views.approve_task, name='approve_task'),
    path('tasks/<int:task_id>/query/', views.query_task, name='query_task'),
]