from django.db import models
from apps.users.models import User
class Customer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    tax_id = models.CharField(max_length=50, blank=True)
    business_type = models.CharField(
        max_length=50,
        choices=[
            ('individual', 'Individual'),
            ('business', 'Business'),
            ('corporate', 'Corporate'),
            ('ngo', 'NGO'),
        ],
        default='individual'
    )
    preferred_language = models.CharField(max_length=20, default='en')
    communication_preference = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('both', 'Both'),
        ],
        default='both'
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Internal notes about customer")
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.customer_id})"
