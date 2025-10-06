# business_portal/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from portal import views  # Import your custom views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('portal.urls')),
    # Add Django authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='portal/login.html'), name='login'),
   path('accounts/logout/', views.custom_logout, name='logout'),  # Use custom logout
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)