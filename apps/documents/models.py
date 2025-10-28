from django.db import models
from apps.users.models import User

class UploadedDocument(models.Model):
    uploaded_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    is_public = models.BooleanField(default=False)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'uploaded_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
