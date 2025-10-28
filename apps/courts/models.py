from django.db import models
from django.utils import timezone
from apps.users.models import User

class Country(models.Model):
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=5,unique=True)
    phone_code=models.CharField(max_length=10,blank=True)

    class Meta:
        db_table='countries'
        verbose_name_plural='Countries'
        ordering=['name']   
    def __str__(self):
        return self.name
class State(models.Model):
    country=models.ForeignKey(Country,on_delete=models.CASCADE,related_name='states') 
    name=models.CharField(max_length=100)     
    code=models.CharField(max_length=10)
    class Meta:
        db_table='states'
        ordering=['name']
    def __str__(self):
        return f"{self.name} - {self.country.code}"

class City(models.Model):
    state=models.ForeignKey(State,on_delete=models.CASCADE,related_name='cities') 
    name=models.CharField(max_length=100)
    class Meta:
        db_table='cities'
        verbose_name_plural='Cities'
        ordering=['name']
        
    def __str__(self):
        return f"{self.name} - {self.state.name}"

class Court(models.Model):
    COURT_TYPES = [
        ('supreme', 'Supreme Court'),
        ('high', 'High Court'),
        ('district', 'District Court'),
        ('magistrate', 'Magistrate Court'),
        ('tribunal', 'Tribunal'),
        ('other', 'Other'),
    ]
    name=models.CharField(max_length=255)
    court_type=models.CharField(max_length=20,choices=COURT_TYPES)
    address=models.TextField()
    country=models.ForeignKey(Country,on_delete=models.SET_NULL,null=True)
    state=models.ForeignKey(State,on_delete=models.SET_NULL,null=True)
    city=models.ForeignKey(City,on_delete=models.SET_NULL,null=True)

    phone=models.CharField(max_length=20,blank=True)
    email=models.EmailField(blank=True)
    website=models.URLField(blank=True)
    manager=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='managed_courts')
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(default=timezone.now)

    class Meta:
        db_table='courts'
        ordering=['name']
    def __str__(self):
        return self.name

class Judge(models.Model):
    name = models.CharField(max_length=200)
    bar_id = models.CharField(max_length=50, unique=True)
    court = models.ForeignKey(Court, on_delete=models.SET_NULL, null=True, related_name='judges')
    
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    
    specialization = models.CharField(max_length=100, blank=True)
    appointment_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'judges'
        ordering = ['name']
    
    def __str__(self):
        return f"Judge {self.name}"        
