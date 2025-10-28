from django.db import models
from apps.users.models import User
from apps.courts.models import Court

class PermissionSet(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True)
    permissions=models.JSONField(default=dict)  
    class Meta:
        db_table = 'permission_sets'
    
    def __str__(self):
        return self.name
class Employee(models.Model):
    DESIGNATION_CHOICES = [
        ('lawyer', 'Lawyer'),
        ('paralegal', 'Paralegal'),
        ('clerk', 'Clerk'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    employee_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    
    bar_registration_number = models.CharField(max_length=100, blank=True)
    date_of_joining = models.DateField()
    date_of_leaving = models.DateField(null=True, blank=True)
    
    permission_set = models.ForeignKey(PermissionSet, on_delete=models.SET_NULL, null=True, blank=True)
    custom_permissions = models.JSONField(default=dict, blank=True)
    
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.designation}" 

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('resume', 'Resume/CV'),
            ('certificate', 'Certificate'),
            ('id_proof', 'ID Proof'),
            ('agreement', 'Agreement'),
            ('other', 'Other'),
        ]
    )
    file = models.FileField(upload_to='employee_documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'employee_documents'       