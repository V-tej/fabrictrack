from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


PERSON_CHOICES = [
    ('ADMIN', 'Admin / Master'),
    ('P1', 'Person 1 — Cutting Report'),
    ('P2', 'CR Lakshay'),
    ('P3', 'CR Rahul'),
    ('P4', 'Stitching Miya Ji'),
    ('P5', 'Job Work'),
    ('P6', 'Finishing Report'),
    ('P7', 'Person 7'),
    ('P8', 'Person 8'),
    ('P9', 'Person 9'),
    ('P10', 'Person 10'),
    ('P11', 'Person 11'),
    ('P12', 'Person 12'),
    ('P13', 'Person 13'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    person_type = models.CharField(max_length=10, choices=PERSON_CHOICES, default='P1')

    def __str__(self):
        return f"{self.user.username} ({self.get_person_type_display()})"


class SystemSetting(models.Model):
    last_excel_download_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class MasterEntry(models.Model):
    """Created by admin — acts as the Date + Lot No key that all persons link to."""
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    job_card_number = models.CharField(max_length=100, verbose_name='Job Card Number')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Master Entry'
        verbose_name_plural = 'Master Entries'
        unique_together = ('date', 'job_card_number')

    def __str__(self):
        return f"{self.date.strftime('%d-%b-%Y')} — {self.job_card_number}"


class CuttingReport(models.Model):
    """Person 1 — Cutting Report form."""
    REPORT_TYPE_CHOICES = [
        ('P1', 'Cutting Master'),
        ('P2', 'CR Lakshay'),
        ('P3', 'CR Rahul'),
    ]
    report_type = models.CharField(max_length=2, choices=REPORT_TYPE_CHOICES, default='P1')
    master_entry = models.ForeignKey(
        MasterEntry,
        on_delete=models.CASCADE,
        related_name='cutting_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    cutting_master_name = models.CharField(max_length=200, blank=True)
    cutting_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fabric_type_quality = models.CharField(max_length=300)
    item_name = models.CharField(max_length=200)
    job_card_no = models.CharField(max_length=100)
    
    size_s = models.PositiveIntegerField(default=0, verbose_name="S")
    size_m = models.PositiveIntegerField(default=0, verbose_name="M")
    size_l = models.PositiveIntegerField(default=0, verbose_name="L")
    size_xl = models.PositiveIntegerField(default=0, verbose_name="XL")
    size_2xl = models.PositiveIntegerField(default=0, verbose_name="2XL")
    size_3xl = models.PositiveIntegerField(default=0, verbose_name="3XL")
    size_4xl = models.PositiveIntegerField(default=0, verbose_name="4XL")
    
    total_pcs = models.PositiveIntegerField(default=0)
    total_colours = models.PositiveIntegerField()
    UNIT_CHOICES = [
        ('Weight', 'Weight'),
        ('Meters', 'Meters')
    ]
    total_weight_meter = models.DecimalField(max_digits=10, decimal_places=3)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='Weight')
    avg_per_pcs = models.DecimalField(max_digits=10, decimal_places=3)
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_pcs = (
            self.size_s + self.size_m + self.size_l + 
            self.size_xl + self.size_2xl + self.size_3xl + self.size_4xl
        )
        super().save(*args, **kwargs)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cutting Report'
        verbose_name_plural = 'Cutting Reports'

    def __str__(self):
        return f"Cutting Report — {self.master_entry} — {self.item_name}"

class CuttingReportColorDetail(models.Model):
    """Detailed size breakdown per color for a CuttingReport."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='color_details'
    )
    color_name = models.CharField(max_length=50)
    size_s = models.PositiveIntegerField(default=0)
    size_m = models.PositiveIntegerField(default=0)
    size_l = models.PositiveIntegerField(default=0)
    size_xl = models.PositiveIntegerField(default=0)
    size_2xl = models.PositiveIntegerField(default=0)
    size_3xl = models.PositiveIntegerField(default=0)
    size_4xl = models.PositiveIntegerField(default=0)
    
    UNIT_CHOICES = [
        ('Weight', 'Weight'),
        ('Meters', 'Meters')
    ]
    total_weight_meter = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='Weight')
    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.color_name} details for {self.cutting_report.job_card_no}"



class CuttingReportPhoto(models.Model):
    """Up to 5 job card photos per CuttingReport."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo = models.ImageField(upload_to='cutting_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.cutting_report}"



class Person4Report(models.Model):
    """Stitching Miya Ji — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='person4_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    job_card_no = models.CharField(max_length=100)
    line_in_date = models.DateField(null=True, blank=True)
    total_pcs = models.PositiveIntegerField(null=True, blank=True)
    line_out_date = models.DateField(default=timezone.now)
    item_name = models.CharField(max_length=200)
    darji_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    folding_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    overlock_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    option_1 = models.CharField(max_length=200, blank=True)
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stitching Miya Ji'
        verbose_name_plural = 'Stitching Miya Ji'

    def __str__(self):
        return f"Stitching Miya Ji — {self.cutting_report.master_entry} — {self.item_name}"




class Person5Report(models.Model):
    """Job Work — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='person5_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    JOB_WORK_CHOICES = [
        ('Job Work In', 'Job Work In'),
        ('Job work Out', 'Job work Out'),
    ]
    
    jobworker = models.CharField(max_length=200)
    job_work_type = models.CharField(max_length=50, choices=JOB_WORK_CHOICES)
    purpose = models.CharField(max_length=300)
    job_card_no = models.CharField(max_length=100)
    date = models.DateField()
    any_other_problem = models.TextField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs = models.PositiveIntegerField()
    
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Work'
        verbose_name_plural = 'Job Work'

    def __str__(self):
        return f"Job Work — {self.jobworker} — {self.job_work_type}"


class Person6Report(models.Model):
    """Finishing Report — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='person6_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    date = models.DateField()
    lot_no = models.CharField(max_length=100)
    total_pcs = models.PositiveIntegerField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs_packed = models.PositiveIntegerField()
    
    green_tape = models.PositiveIntegerField()
    red_tape = models.PositiveIntegerField()
    blue_tape = models.PositiveIntegerField()
    total_tape = models.PositiveIntegerField()
    
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Finishing Report'
        verbose_name_plural = 'Finishing Reports'

    def __str__(self):
        return f"Finishing Report — {self.lot_no} — {self.date}"

class Person6ReportPhoto(models.Model):
    """Up to 5 photos per Person6Report."""
    person6_report = models.ForeignKey(
        Person6Report,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo = models.ImageField(upload_to='person6_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.person6_report}"
