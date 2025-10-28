from django.db import models
from apps.users.models import User

class Notification(models.Model):
    """In-app notification model"""
    NOTIFICATION_TYPES = [
        ('case_assigned', 'Case Assigned'),
        ('case_update', 'Case Update'),
        ('hearing_scheduled', 'Hearing Scheduled'),
        ('hearing_reminder', 'Hearing Reminder'),
        ('document_uploaded', 'Document Uploaded'),
        ('message', 'Message'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional reference to related object
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class EmailLog(models.Model):
    """Log of all emails sent"""
    to_email = models.EmailField()
    subject = models.CharField(max_length=200)
    template_name = models.CharField(max_length=100)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'email_logs'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.to_email} - {self.subject}"

