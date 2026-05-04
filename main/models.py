from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os
from datetime import date

def get_xray_upload_path(instance, filename):
    """Generate a unique path for uploaded X-ray images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('xrays', filename)

def get_report_upload_path(instance, filename):
    """Generate a unique path for uploaded report files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('reports', filename)

class Patient(models.Model):
    """Patient model for storing patient information"""
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age = models.PositiveIntegerField(editable=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate patient ID if new
        if not self.patient_id:
            year = timezone.now().year
            month = timezone.now().month
            # Get count of patients created this month + 1
            count = Patient.objects.filter(
                created_at__year=year,
                created_at__month=month
            ).count() + 1
            self.patient_id = f"P{year}{month:02d}{count:04d}"
        
        # Calculate age from date of birth
        today = date.today()
        born = self.date_of_birth
        self.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.patient_id})"
    
    class Meta:
        ordering = ['-created_at']


class XRay(models.Model):
    """X-ray model for storing X-ray images and analysis results"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('analyzed', 'Analyzed'),
        ('reported', 'Reported'),
    )
    
    RESULT_CHOICES = (
        ('positive', 'Pneumonia Detected'),
        ('negative', 'Normal'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_xray_upload_path)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    ai_result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    analyzed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='analyzed_xrays')
    analyzed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"X-ray for {self.patient.name} - {self.upload_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-upload_date']


class Report(models.Model):
    """Medical report model for storing doctor's diagnosis and recommendations"""
    xray = models.OneToOneField(XRay, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    diagnosis = models.TextField()
    recommendations = models.TextField()
    severity = models.CharField(max_length=20, choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(upload_to=get_report_upload_path, blank=True, null=True)
    
    def __str__(self):
        return f"Report for {self.xray.patient.name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']


class Notification(models.Model):
    """Notification model for system notifications"""
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_xray = models.ForeignKey(XRay, on_delete=models.SET_NULL, blank=True, null=True)
    related_patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    related_xray = models.ForeignKey('XRay', on_delete=models.CASCADE, null=True, blank=True)
    related_patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title} for {self.user.username}"