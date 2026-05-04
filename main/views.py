from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .utils import process_xray_image, generate_pdf_report
from .models import Patient, XRay, Report, Notification, UserProfile
from .forms import PatientForm, XRayUploadForm, ReportForm, UserProfileForm, UserForm

import random
import io
import numpy as np
from datetime import datetime, timedelta

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        # Redirect based on user role
        if request.user.groups.filter(name='Doctor').exists():
            return redirect('doctor_dashboard')
        elif request.user.groups.filter(name='Lab Technician').exists():
            return redirect('lab_dashboard')
        elif request.user.is_staff:
            return redirect('admin:index')
    
    # Stats for homepage
    stats = {
        'patients': Patient.objects.count(),
        'xrays': XRay.objects.count(),
        'reports': Report.objects.count(),
        'positive_cases': XRay.objects.filter(ai_result='positive').count(),
    }
    
    return render(request, 'main/home.html', {'stats': stats})

@login_required
def lab_dashboard(request):
    """Dashboard for lab technicians"""
    if not request.user.groups.filter(name='Lab Technician').exists() and not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get statistics
    total_xrays = XRay.objects.count()
    pending_analysis = XRay.objects.filter(status='pending').count()
    completed_today = XRay.objects.filter(
        analyzed_at__date=timezone.now().date()
    ).count()
    positive_cases = XRay.objects.filter(ai_result='positive').count()
    
    # Get recent X-rays
    recent_xrays = XRay.objects.all().order_by('-upload_date')[:10]
    
    context = {
        'total_xrays': total_xrays,
        'pending_analysis': pending_analysis,
        'completed_today': completed_today,
        'positive_cases': positive_cases,
        'recent_xrays': recent_xrays,
    }
    
    return render(request, 'main/lab_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    """Dashboard for doctors"""
    if not request.user.groups.filter(name='Doctor').exists() and not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get statistics
    assigned_cases = XRay.objects.filter(status='analyzed').count()
    pending_review = XRay.objects.filter(status='analyzed', report__isnull=True).count()
    completed_reports = Report.objects.filter(doctor=request.user).count()
    urgent_cases = XRay.objects.filter(
        ai_result='positive', 
        confidence_score__gte=80,
        report__isnull=True
    ).count()
    
    # Get assigned X-rays
    assigned_xrays = XRay.objects.filter(
        status='analyzed'
    ).order_by('-confidence_score')[:5]
    
    context = {
        'assigned_cases': assigned_cases,
        'pending_review': pending_review,
        'completed_reports': completed_reports,
        'urgent_cases': urgent_cases,
        'assigned_xrays': assigned_xrays,
    }
    
    return render(request, 'main/doctor_dashboard.html', context)

class PatientListView(LoginRequiredMixin, ListView):
    """View for listing patients"""
    model = Patient
    template_name = 'main/patients.html'
    context_object_name = 'patients'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(patient_id__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        # Apply age filter
        age_range = self.request.GET.get('age_range', '')
        if age_range:
            min_age, max_age = map(int, age_range.split('-'))
            queryset = queryset.filter(age__gte=min_age, age__lte=max_age)
        
        # Apply gender filter
        gender = self.request.GET.get('gender', '')
        if gender:
            queryset = queryset.filter(gender=gender)
            
        return queryset

@login_required
def add_patient(request):
    """View for adding a new patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient {patient.name} added successfully!")
            return redirect('patients')
    else:
        form = PatientForm()
    
    return render(request, 'main/add_patient.html', {'form': form})

@login_required
def upload_xray(request):
    """View for uploading a new X-ray"""
    if request.method == 'POST':
        form = XRayUploadForm(request.POST, request.FILES)
        if form.is_valid():
            xray = form.save(commit=False)
            xray.save()
            
            # Check if auto-analyze is requested
            if 'auto_analyze' in request.POST:
                return redirect('analyze_xray', pk=xray.id)
            
            messages.success(request, "X-ray uploaded successfully!")
            return redirect('lab_dashboard')
    else:
        # Pre-select patient if provided in URL
        patient_id = request.GET.get('patient')
        if patient_id:
            form = XRayUploadForm(initial={'patient': patient_id})
        else:
            form = XRayUploadForm()
    
    return render(request, 'main/upload_xray.html', {'form': form})

@login_required
def analyze_xray(request, pk):
    """View for analyzing an X-ray with AI"""
    xray = get_object_or_404(XRay, pk=pk)
    
    if xray.status != 'pending':
        messages.info(request, "This X-ray has already been analyzed.")
        return redirect('xray_detail', pk=xray.id)
    
    # Call the renamed utility function
    result, confidence = process_xray_image(xray.image.path)
    
    # Update X-ray with results
    xray.ai_result = result
    xray.confidence_score = confidence
    xray.status = 'analyzed'
    xray.analyzed_by = request.user
    xray.analyzed_at = timezone.now()
    xray.save()
    
    # Create notification for doctors
    doctors = Group.objects.get(name='Doctor').user_set.all()
    for doctor in doctors:
        Notification.objects.create(
            user=doctor,
            title="New X-ray Analysis",
            message=f"X-ray for patient {xray.patient.name} has been analyzed and requires review.",
            notification_type='info',
            related_xray=xray,
            related_patient=xray.patient
        )
    
    messages.success(request, "X-ray analyzed successfully!")
    return redirect('xray_detail', pk=xray.id)

@login_required
def xray_detail(request, pk):
    """View for X-ray details"""
    xray = get_object_or_404(XRay, pk=pk)
    
    # Check if report exists
    try:
        report = Report.objects.get(xray=xray)
    except Report.DoesNotExist:
        report = None
    
    context = {
        'xray': xray,
        'report': report,
    }
    
    return render(request, 'main/xray_detail.html', context)

@login_required
def create_report(request, pk):
    """View for creating a medical report"""
    if not request.user.groups.filter(name='Doctor').exists() and not request.user.is_staff:
        messages.error(request, "Only doctors can create reports.")
        return redirect('home')
    
    xray = get_object_or_404(XRay, pk=pk)
    
    if xray.status != 'analyzed':
        messages.error(request, "This X-ray must be analyzed before creating a report.")
        return redirect('xray_detail', pk=xray.id)
    
    try:
        report = Report.objects.get(xray=xray)
        messages.info(request, "A report already exists for this X-ray.")
        return redirect('xray_detail', pk=xray.id)
    except Report.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.xray = xray
            report.doctor = request.user
            
            pdf_file = generate_pdf_report(xray, report)  # Fixed: Use generate_pdf_report directly
            
            report.pdf_file.save(f"report_{xray.id}.pdf", pdf_file)
            report.save()
            
            xray.status = 'reported'
            xray.save()
            
            lab_techs = Group.objects.get(name='Lab Technician').user_set.all()
            for tech in lab_techs:
                Notification.objects.create(
                    user=tech,
                    title="New Report Created",
                    message=f"Dr. {request.user.get_full_name()} has created a report for patient {xray.patient.name}.",
                    notification_type='success',
                    related_xray=xray,
                    related_patient=xray.patient
                )
            
            messages.success(request, "Report created successfully!")
            return redirect('xray_detail', pk=xray.id)
    else:
        initial_diagnosis = ""
        if xray.ai_result == 'positive':
            initial_diagnosis = "AI analysis indicates pneumonia. "
        elif xray.ai_result == 'negative':
            initial_diagnosis = "AI analysis indicates normal lung condition. "
        else:
            initial_diagnosis = "X-ray not yet analyzed. "
        
        form = ReportForm(initial={'diagnosis': initial_diagnosis})
    
    context = {
        'form': form,
        'xray': xray,
    }
    
    return render(request, 'main/create_report.html', context)
@login_required
def assigned_xrays(request):
    """View for X-rays assigned to doctors"""
    if not request.user.groups.filter(name='Doctor').exists() and not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get filters
    status = request.GET.get('status', '')
    ai_result = request.GET.get('ai_result', '')
    priority = request.GET.get('priority', '')
    
    # Base queryset
    queryset = XRay.objects.filter(status='analyzed')
    
    # Apply filters
    if status:
        queryset = queryset.filter(status=status)
    
    if ai_result:
        queryset = queryset.filter(ai_result=ai_result)
    
    if priority:
        if priority == 'high':
            queryset = queryset.filter(ai_result='positive', confidence_score__gte=80)
        elif priority == 'medium':
            queryset = queryset.filter(ai_result='positive', confidence_score__lt=80)
        elif priority == 'low':
            queryset = queryset.filter(ai_result='negative')
    
    context = {
        'xrays': queryset,
    }
    
    return render(request, 'main/assigned_xrays.html', context)

@login_required
def reports(request):
    """View for listing reports"""
    if not request.user.groups.filter(name='Doctor').exists() and not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get filters
    doctor_id = request.GET.get('doctor', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    severity = request.GET.get('severity', '')
    
    # Base queryset
    if request.user.is_staff:
        queryset = Report.objects.all()
    else:
        queryset = Report.objects.filter(doctor=request.user)
    
    # Apply filters
    if doctor_id and request.user.is_staff:
        queryset = queryset.filter(doctor_id=doctor_id)
    
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    
    if severity:
        queryset = queryset.filter(severity=severity)
    
    # Paginate
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)
    
    context = {
        'reports': reports,
    }
    
    return render(request, 'main/reports.html', context)

@login_required
def download_report(request, pk):
    """View for downloading a report PDF"""
    report = get_object_or_404(Report, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and not request.user.groups.filter(name='Doctor').exists() and report.doctor != request.user:
        messages.error(request, "You don't have permission to download this report.")
        return redirect('home')
    
    # Serve the PDF file
    if report.pdf_file:
        response = HttpResponse(report.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{report.xray.patient.name}.pdf"'
        return response
    else:
        messages.error(request, "PDF file not found.")
        return redirect('reports')

@login_required
def profile(request):
    """View for user profile"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'main/profile.html', context)

@login_required
def notifications_view(request):
    """View for user notifications"""
    user = request.user
    notifications_qs = user.notifications.all().order_by('-created_at')
    unread_count = notifications_qs.filter(is_read=False).count()

    mark_read = request.GET.get('mark_read')
    if mark_read:
        if mark_read == 'all':
            notifications_qs.filter(is_read=False).update(is_read=True)
        else:
            notifications_qs.filter(id=mark_read).update(is_read=True)
        return redirect('notifications')

    paginator = Paginator(notifications_qs, 10)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'main/notifications.html', context)

@login_required
def mark_notification_read(request):
    """AJAX view for marking notifications as read"""
    if request.method == 'POST' and request.is_ajax():
        notification_id = request.POST.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})