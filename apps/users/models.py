from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin
from django.utils import timezone
from django.core.signing import Signer

class UserManager(BaseUserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractUser,PermissionsMixin):
    email=models.EmailField(unique=True,db_index=True)
    mobile=models.CharField(max_length=15,blank=True,null=True,db_index=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_separated=models.BooleanField(default=False)
    storage_quota = models.BigIntegerField(default=5368709120) 
    storage_used = models.BigIntegerField(default=0)

    date_joined=models.DateTimeField(default=timezone.now)
    last_login=models.DateTimeField(blank=True,null=True)
    objects=UserManager()
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['first_name','last_name']
    class Meta:
        db_table='users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def storage_available(self):
        return self.storage_quota - self.storage_used

class OTPLogin(models.Model):
    mobile = models.CharField(max_length=15, db_index=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otp_logins'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_verified and timezone.now() < self.expires_at

class PasswordResetCode(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    code=models.CharField(max_length=100,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_used=models.BooleanField(default=False)
    expires_at=models.DateTimeField()
    class Meta:
        db_table='password_reset_codes'

    def save(self,*args,**kwargs):
        if not self.code:
            signer=Signer()
            self.code=signer.sign(f"{self.user.id}-{timezone.now().timestamp()}")
        if not self.expires_at:
            self.expires_at=timezone.now()+timezone.timedelta(hours=24) 
        super().save(*args,**kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at    
    

