from django.contrib import admin
from .models import Patient, XRay, Report, Notification, UserProfile

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'name', 'age', 'gender', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'patient_id', 'phone', 'email')
    readonly_fields = ('patient_id', 'age')
    fieldsets = (
        ('Personal Information', {
            'fields': ('patient_id', 'name', 'date_of_birth', 'age', 'gender')
        }),
        ('Contact Information', {
            'fields': ('guardian_name', 'phone', 'email', 'address')
        }),
        ('Medical Information', {
            'fields': ('medical_history',)
        }),
    )


@admin.register(XRay)
class XRayAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'upload_date', 'status', 'ai_result', 'confidence_score')
    list_filter = ('status', 'ai_result', 'upload_date')
    search_fields = ('patient__name', 'patient__patient_id', 'notes')
    readonly_fields = ('upload_date', 'analyzed_at')
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('X-ray Information', {
            'fields': ('image', 'upload_date', 'notes')
        }),
        ('Analysis Results', {
            'fields': ('status', 'ai_result', 'confidence_score', 'analyzed_by', 'analyzed_at')
        }),
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'xray', 'doctor', 'severity', 'created_at')
    list_filter = ('severity', 'created_at')
    search_fields = ('xray__patient__name', 'doctor__username', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Report Information', {
            'fields': ('xray', 'doctor', 'created_at', 'updated_at')
        }),
        ('Medical Assessment', {
            'fields': ('diagnosis', 'recommendations', 'severity')
        }),
        ('Files', {
            'fields': ('pdf_file',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'specialty')
    search_fields = ('user__username', 'user__email', 'phone', 'specialty')
