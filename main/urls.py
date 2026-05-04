from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='main/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Main pages
    # path('', views.home, name='home'),
    
    path('', views.doctor_dashboard, name='home'),
    
    
    path('lab-dashboard/', views.lab_dashboard, name='lab_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Patient management
    path('patients/', views.PatientListView.as_view(), name='patients'),
    path('patients/add/', views.add_patient, name='add_patient'),
    
    # X-ray management
    path('upload-xray/', views.upload_xray, name='upload_xray'),
    path('xray/<int:pk>/', views.xray_detail, name='xray_detail'),
    path('xray/<int:pk>/analyze/', views.analyze_xray, name='analyze_xray'),
    
    # Report management
    path('xray/<int:pk>/report/', views.create_report, name='create_report'),
    path('reports/', views.reports, name='reports'),
    path('report/<int:pk>/download/', views.download_report, name='download_report'),
    
    # Doctor views
    path('assigned-xrays/', views.assigned_xrays, name='assigned_xrays'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
]
