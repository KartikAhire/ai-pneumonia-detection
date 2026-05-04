from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, XRay, Report, Notification

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=XRay)
def notify_on_xray_analysis(sender, instance, **kwargs):
    """Create notifications when an X-ray is analyzed"""
    if instance.status == 'analyzed' and instance.analyzed_at:
        # This would be handled in the analyze_xray view
        pass

@receiver(post_save, sender=Report)
def notify_on_report_creation(sender, instance, created, **kwargs):
    """Create notifications when a new report is created"""
    if created:
        # This would be handled in the create_report view
        pass
