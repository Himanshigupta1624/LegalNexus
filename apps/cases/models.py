from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.courts.models import Court, Judge
from apps.customers.models import Customer


class CaseCategory(models.Model):
    """Categories like Civil, Criminal, Family, Corporate, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'case_categories'
        verbose_name_plural = 'Case Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CaseStatus(models.Model):
    """Case statuses: Filed, Pending, Hearing Scheduled, Closed, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#000000')  # Hex color
    order = models.IntegerField(default=0)  # For ordering in UI
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'case_statuses'
        verbose_name_plural = 'Case Statuses'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class CasePriority(models.Model):
    """Priority levels: Low, Medium, High, Urgent"""
    name = models.CharField(max_length=50, unique=True)
    level = models.IntegerField(unique=True)  # 1=Low, 2=Medium, 3=High, 4=Urgent
    color_code = models.CharField(max_length=7, default='#000000')
    
    class Meta:
        db_table = 'case_priorities'
        verbose_name_plural = 'Case Priorities'
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"


class Case(models.Model):
    """Main Case model - represents a legal case"""
    # Basic Information
    case_number = models.CharField(max_length=100, unique=True, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Classification
    category = models.ForeignKey(CaseCategory, on_delete=models.PROTECT, related_name='cases')
    status = models.ForeignKey(CaseStatus, on_delete=models.PROTECT, related_name='cases')
    priority = models.ForeignKey(CasePriority, on_delete=models.PROTECT, related_name='cases')
    
    # Parties
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cases')
    opposing_party = models.CharField(max_length=300, blank=True)
    opposing_lawyer = models.CharField(max_length=300, blank=True)
    
    # Court Details
    court = models.ForeignKey(Court, on_delete=models.PROTECT, related_name='cases')
    judge = models.ForeignKey(Judge, on_delete=models.SET_NULL, null=True, blank=True, related_name='cases')
    
    # Assigned Team
    assigned_lawyer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='assigned_cases',
        help_text="Primary lawyer handling the case"
    )
    team_members = models.ManyToManyField(
        User, 
        related_name='team_cases',
        blank=True,
        help_text="Additional team members"
    )
    
    # Dates
    filing_date = models.DateField()
    hearing_date = models.DateField(null=True, blank=True)
    next_hearing_date = models.DateField(null=True, blank=True, db_index=True)
    expected_closure_date = models.DateField(null=True, blank=True)
    actual_closure_date = models.DateField(null=True, blank=True)
    
    # Financial
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fees_charged = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fees_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cases_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    internal_notes = models.TextField(blank=True, help_text="Internal notes - not visible to customer")
    
    class Meta:
        db_table = 'cases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['case_number']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['next_hearing_date']),
            models.Index(fields=['customer', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.case_number} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if case is overdue based on expected closure date"""
        if self.expected_closure_date and not self.actual_closure_date:
            return timezone.now().date() > self.expected_closure_date
        return False
    
    @property
    def days_pending(self):
        """Calculate days since filing"""
        if self.actual_closure_date:
            return (self.actual_closure_date - self.filing_date).days
        return (timezone.now().date() - self.filing_date).days
    
    @property
    def outstanding_fees(self):
        """Calculate outstanding fees"""
        return self.fees_charged - self.fees_paid


class CaseUpdate(models.Model):
    """Timeline/activity log for each case"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=300)
    description = models.TextField()
    update_type = models.CharField(
        max_length=50,
        choices=[
            ('hearing', 'Hearing'),
            ('document', 'Document Filed'),
            ('judgment', 'Judgment'),
            ('motion', 'Motion Filed'),
            ('note', 'General Note'),
            ('status_change', 'Status Change'),
        ],
        default='note'
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible_to_customer = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'case_updates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.case.case_number} - {self.title}"


class Hearing(models.Model):
    """Scheduled hearings for cases"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='hearings')
    hearing_date = models.DateTimeField()
    hearing_type = models.CharField(
        max_length=100,
        choices=[
            ('first_hearing', 'First Hearing'),
            ('evidence', 'Evidence Hearing'),
            ('arguments', 'Arguments'),
            ('final', 'Final Hearing'),
            ('misc', 'Miscellaneous'),
        ],
        default='misc'
    )
    
    location = models.CharField(max_length=300, blank=True)
    judge = models.ForeignKey(Judge, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Preparation
    agenda = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Notes taken during hearing")
    outcome = models.TextField(blank=True)
    next_hearing_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=50,
        choices=[
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('postponed', 'Postponed'),
            ('cancelled', 'Cancelled'),
        ],
        default='scheduled'
    )
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hearings'
        ordering = ['hearing_date']
        indexes = [
            models.Index(fields=['hearing_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.case.case_number} - {self.hearing_date.strftime('%Y-%m-%d %H:%M')}"


class CaseDocument(models.Model):
    """Documents related to cases"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case_documents')
    title = models.CharField(max_length=300)
    document_type = models.CharField(
        max_length=100,
        choices=[
            ('petition', 'Petition'),
            ('evidence', 'Evidence'),
            ('affidavit', 'Affidavit'),
            ('order', 'Court Order'),
            ('judgment', 'Judgment'),
            ('notice', 'Notice'),
            ('contract', 'Contract'),
            ('misc', 'Miscellaneous'),
        ],
        default='misc'
    )
    
    file = models.FileField(upload_to='case_documents/%Y/%m/')
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)
    
    description = models.TextField(blank=True)
    filing_date = models.DateField(null=True, blank=True)
    
    # Access Control
    is_confidential = models.BooleanField(default=False)
    is_visible_to_customer = models.BooleanField(default=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'case_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.case.case_number} - {self.title}"


class CaseTag(models.Model):
    """Tags for categorizing and searching cases"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    class Meta:
        db_table = 'case_tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CaseTagRelation(models.Model):
    """Many-to-many relationship between cases and tags"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(CaseTag, on_delete=models.CASCADE, related_name='case_relations')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'case_tag_relations'
        unique_together = ['case', 'tag']