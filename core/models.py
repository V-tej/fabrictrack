from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


PERSON_CHOICES = [
    ('ADMIN', 'Admin / Master'),
    ('P1', 'Person 1 — Cutting Report'),
    ('P2', 'CR Lakshay'),
    ('P3', 'CR Rahul'),
    ('P4', 'Stitching'),
    ('P5', 'Job Work'),
    ('P6', 'Finishing Report'),
    ('P7', 'Embroidery'),
    ('P8', 'Printing'),
    ('P9', 'Singleneedle'),
    ('P10', 'Sewing'),
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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Master Entry'
        verbose_name_plural = 'Master Entries'
        unique_together = ('date', 'job_card_number')

    def __str__(self):
        return f"{self.date.strftime('%d-%b-%Y')} — {self.job_card_number}"

class MasterName(models.Model):
    DEPARTMENT_CHOICES = [
        ('Cutting', 'Cutting'),
        ('Stitching', 'Stitching'),
        ('Job Work', 'Job Work'),
        ('Finishing', 'Finishing'),
        ('Embroidery', 'Embroidery'),
        ('Printing', 'Printing'),
        ('Singleneedle', 'Singleneedle'),
        ('Sewing', 'Sewing'),
    ]
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="UPI ID / VPA")

    class Meta:
        ordering = ['department', 'name']
        unique_together = ('name', 'department')

    def __str__(self):
        return f"{self.name} ({self.department})"


class MasterPayment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('UPI', 'UPI / NetBanking'),
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Other', 'Other'),
    ]
    master = models.ForeignKey(MasterName, on_delete=models.CASCADE, related_name='payments')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='UPI')
    reference_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ref No / UPI ID")
    remarks = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Master Payment'
        verbose_name_plural = 'Master Payments'

    def __str__(self):
        return f"Payment of ₹{self.amount} to {self.master.name} on {self.date}"


class RateDefinition(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Rate Name (e.g. R1)")
    description = models.CharField(max_length=300, verbose_name="Description")
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Rate")

    class Meta:
        ordering = ['name']
        verbose_name = "Rate Definition"
        verbose_name_plural = "Rate Definitions"

    def __str__(self):
        return f"{self.name} - {self.description} (₹{self.total_rate})"



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
    master_name = models.CharField(max_length=200, blank=True, null=True)
    cutting_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    rate_name = models.CharField(max_length=50, blank=True, null=True)
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
    total_weight = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    total_meters = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    avg_per_pcs = models.DecimalField(max_digits=10, decimal_places=3)
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_pcs = (
            self.size_s + self.size_m + self.size_l + 
            self.size_xl + self.size_2xl + self.size_3xl + self.size_4xl
        )
        super().save(*args, **kwargs)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    total_weight = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    total_meters = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
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
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.cutting_report}"



class StitchingReport(models.Model):
    """Stitching — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='stitching_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    stitching_master_name = models.CharField(max_length=200, blank=True, null=True)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    job_card_no = models.CharField(max_length=100)
    line_in_date = models.DateField(null=True, blank=True)
    total_pcs = models.PositiveIntegerField(null=True, blank=True)
    line_out_date = models.DateField(null=True, blank=True)
    item_name = models.CharField(max_length=200)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    rate_name = models.CharField(max_length=50, blank=True, null=True)
    rate_description = models.CharField(max_length=300, blank=True, null=True)
    darji_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    folding_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    overlock_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    option_1 = models.CharField(max_length=200, blank=True)
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stitching'
        verbose_name_plural = 'Stitching'

    def __str__(self):
        return f"Stitching — {self.cutting_report.master_entry} — {self.item_name}"


class StitchingReportPhoto(models.Model):
    """Up to 5 job card photos per StitchingReport."""
    stitching_report = models.ForeignKey(
        StitchingReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.stitching_report}"


class JobWorkReport(models.Model):
    """Job Work — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='jobwork_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    jobworker = models.CharField(max_length=200)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    purpose = models.CharField(max_length=300)
    job_card_no = models.CharField(max_length=100)
    jobwork_in = models.DateField(null=True, blank=True)
    jobwork_out = models.DateField(null=True, blank=True)
    any_other_problem = models.TextField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs = models.PositiveIntegerField()
    
    # New fields: Design and Rates
    design_jobwork = models.CharField(max_length=200, blank=True, null=True)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Work'
        verbose_name_plural = 'Job Work'

    def __str__(self):
        return f"Job Work — {self.jobworker} — {self.job_card_no}"


class JobWorkReportPhoto(models.Model):
    """Up to 5 job card photos per JobWorkReport."""
    job_work_report = models.ForeignKey(
        JobWorkReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.job_work_report}"


class EmbroideryReport(models.Model):
    """Embroidery — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='embroidery_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    embroidery_worker = models.CharField(max_length=200)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    purpose = models.CharField(max_length=300)
    job_card_no = models.CharField(max_length=100)
    embroidery_in = models.DateField(null=True, blank=True)
    embroidery_out = models.DateField(null=True, blank=True)
    any_other_problem = models.TextField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs = models.PositiveIntegerField()
    
    # New fields: Design and Rates
    design_embroidery = models.CharField(max_length=200, blank=True, null=True)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Embroidery'
        verbose_name_plural = 'Embroidery'

    def __str__(self):
        return f"Embroidery — {self.embroidery_worker} — {self.job_card_no}"


class EmbroideryReportPhoto(models.Model):
    """Up to 5 job card photos per EmbroideryReport."""
    embroidery_report = models.ForeignKey(
        EmbroideryReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.embroidery_report}"


class PrintingReport(models.Model):
    """Printing — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='printing_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    printing_worker = models.CharField(max_length=200)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    purpose = models.CharField(max_length=300)
    job_card_no = models.CharField(max_length=100)
    printing_in = models.DateField(null=True, blank=True)
    printing_out = models.DateField(null=True, blank=True)
    any_other_problem = models.TextField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs = models.PositiveIntegerField()
    
    # New fields: Design and Rates
    design_printing = models.CharField(max_length=200, blank=True, null=True)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Printing'
        verbose_name_plural = 'Printing'

    def __str__(self):
        return f"Printing — {self.printing_worker} — {self.job_card_no}"


class PrintingReportPhoto(models.Model):
    """Up to 5 job card photos per PrintingReport."""
    printing_report = models.ForeignKey(
        PrintingReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.printing_report}"


class SingleneedleReport(models.Model):
    """Singleneedle — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='singleneedle_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    singleneedle_master_name = models.CharField(max_length=200, blank=True, null=True)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    job_card_no = models.CharField(max_length=100)
    line_in_date = models.DateField(null=True, blank=True)
    total_pcs = models.PositiveIntegerField(null=True, blank=True)
    line_out_date = models.DateField(null=True, blank=True)
    item_name = models.CharField(max_length=200)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    rate_name = models.CharField(max_length=50, blank=True, null=True)
    rate_description = models.CharField(max_length=300, blank=True, null=True)
    darji_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    folding_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    overlock_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    option_1 = models.CharField(max_length=200, blank=True)
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Singleneedle'
        verbose_name_plural = 'Singleneedle'

    def __str__(self):
        return f"Singleneedle — {self.cutting_report.master_entry} — {self.item_name}"


class SingleneedleReportPhoto(models.Model):
    """Up to 5 job card photos per SingleneedleReport."""
    singleneedle_report = models.ForeignKey(
        SingleneedleReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.singleneedle_report}"


class SewingReport(models.Model):
    """Sewing — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='sewing_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sewing_master_name = models.CharField(max_length=200, blank=True, null=True)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    job_card_no = models.CharField(max_length=100)
    line_in_date = models.DateField(null=True, blank=True)
    total_pcs = models.PositiveIntegerField(null=True, blank=True)
    line_out_date = models.DateField(null=True, blank=True)
    item_name = models.CharField(max_length=200)
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    rate_name = models.CharField(max_length=50, blank=True, null=True)
    rate_description = models.CharField(max_length=300, blank=True, null=True)
    darji_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    folding_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    overlock_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)
    option_1 = models.CharField(max_length=200, blank=True)
    signature = models.TextField(blank=True, null=True)
    signature_2 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sewing'
        verbose_name_plural = 'Sewing'

    def __str__(self):
        return f"Sewing — {self.cutting_report.master_entry} — {self.item_name}"


class SewingReportPhoto(models.Model):
    """Up to 5 job card photos per SewingReport."""
    sewing_report = models.ForeignKey(
        SewingReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.sewing_report}"


class FinishingReport(models.Model):
    """Finishing Report — Form based on P1's Cutting Report."""
    cutting_report = models.ForeignKey(
        CuttingReport,
        on_delete=models.CASCADE,
        related_name='finishing_reports'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    finishing_master_name = models.CharField(max_length=200, blank=True, null=True)
    master_name = models.CharField(max_length=200, blank=True, null=True)
    
    date = models.DateField()
    lot_no = models.CharField(max_length=100)
    total_pcs = models.PositiveIntegerField()
    total_pcs_short = models.PositiveIntegerField()
    total_pcs_packed = models.PositiveIntegerField()
    
    green_tape = models.PositiveIntegerField()
    red_tape = models.PositiveIntegerField()
    blue_tape = models.PositiveIntegerField()
    total_tape = models.PositiveIntegerField()
    
    # Rates logic
    rate_definition = models.ForeignKey('RateDefinition', on_delete=models.SET_NULL, null=True, blank=True)
    total_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Finishing Report'
        verbose_name_plural = 'Finishing Reports'

    def __str__(self):
        return f"Finishing Report — {self.lot_no} — {self.date}"

class FinishingReportPhoto(models.Model):
    """Up to 5 photos per FinishingReport."""
    finishing_report = models.ForeignKey(
        FinishingReport,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.finishing_report}"


class JobCardRequirement(models.Model):
    """Tracks required and completed jobs for a given Job Card from Excel Import."""
    job_card_no = models.CharField(max_length=100, unique=True)
    date = models.DateField(default=timezone.now)
    
    # Requirements: 0 = Not required, 1-8 = sequence order
    requires_cutting = models.IntegerField(default=0)
    requires_jobwork = models.IntegerField(default=0)
    requires_stitching = models.IntegerField(default=0)
    requires_finishing = models.IntegerField(default=0)
    requires_embroidery = models.IntegerField(default=0)
    requires_printing = models.IntegerField(default=0)
    requires_singleneedle = models.IntegerField(default=0)
    requires_sewing = models.IntegerField(default=0)
    
    # Status (Updated when reports are submitted)
    is_cutting_done = models.BooleanField(default=False)
    is_jobwork_done = models.BooleanField(default=False)
    is_stitching_done = models.BooleanField(default=False)
    is_finishing_done = models.BooleanField(default=False)
    is_embroidery_done = models.BooleanField(default=False)
    is_printing_done = models.BooleanField(default=False)
    is_singleneedle_done = models.BooleanField(default=False)
    is_sewing_done = models.BooleanField(default=False)

    # In-Progress: In date submitted but Out date not yet filled
    is_jobwork_in_progress = models.BooleanField(default=False)
    is_embroidery_in_progress = models.BooleanField(default=False)
    is_printing_in_progress = models.BooleanField(default=False)
    is_stitching_in_progress = models.BooleanField(default=False)
    is_singleneedle_in_progress = models.BooleanField(default=False)
    is_sewing_in_progress = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Requirement: {self.job_card_no}"

    def is_step_enabled(self, step_seq, step_done_attr):
        """A step is enabled if all required steps with a lower sequence number are done."""
        if step_seq == 0:
            return False  # not required
        # Build dict of {seq: done_status} for all required steps
        steps = [
            (self.requires_cutting,     self.is_cutting_done),
            (self.requires_jobwork,     self.is_jobwork_done),
            (self.requires_stitching,   self.is_stitching_done),
            (self.requires_finishing,   self.is_finishing_done),
            (self.requires_embroidery,  self.is_embroidery_done),
            (self.requires_printing,    self.is_printing_done),
            (self.requires_singleneedle,self.is_singleneedle_done),
            (self.requires_sewing,      self.is_sewing_done),
        ]
        for seq, done in steps:
            if seq > 0 and seq < step_seq and not done:
                return False  # a predecessor step is not yet done
        return True

    @property
    def is_cutting_enabled(self):
        return self.is_step_enabled(self.requires_cutting, self.is_cutting_done)

    @property
    def is_jobwork_enabled(self):
        return self.is_step_enabled(self.requires_jobwork, self.is_jobwork_done)

    @property
    def is_stitching_enabled(self):
        return self.is_step_enabled(self.requires_stitching, self.is_stitching_done)

    @property
    def is_finishing_enabled(self):
        return self.is_step_enabled(self.requires_finishing, self.is_finishing_done)

    @property
    def is_embroidery_enabled(self):
        return self.is_step_enabled(self.requires_embroidery, self.is_embroidery_done)

    @property
    def is_printing_enabled(self):
        return self.is_step_enabled(self.requires_printing, self.is_printing_done)

    @property
    def is_singleneedle_enabled(self):
        return self.is_step_enabled(self.requires_singleneedle, self.is_singleneedle_done)

    @property
    def is_sewing_enabled(self):
        return self.is_step_enabled(self.requires_sewing, self.is_sewing_done)

    @property
    def master_entry_id(self):
        from .models import MasterEntry # ensure no circular import if needed, though they are in same file
        me = MasterEntry.objects.filter(job_card_number=self.job_card_no).first()
        return me.id if me else None

    @property
    def stitching_report_id(self):
        from .models import StitchingReport
        r = StitchingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def jobwork_report_id(self):
        from .models import JobWorkReport
        r = JobWorkReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def embroidery_report_id(self):
        from .models import EmbroideryReport
        r = EmbroideryReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def printing_report_id(self):
        from .models import PrintingReport
        r = PrintingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def singleneedle_report_id(self):
        from .models import SingleneedleReport
        r = SingleneedleReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def sewing_report_id(self):
        from .models import SewingReport
        r = SewingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def finishing_report_id(self):
        from .models import FinishingReport
        r = FinishingReport.objects.filter(lot_no=self.job_card_no).first()
        return r.id if r else None

    @property
    def stitching_created_by(self):
        from .models import StitchingReport
        r = StitchingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None

    @property
    def jobwork_created_by(self):
        from .models import JobWorkReport
        r = JobWorkReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None

    @property
    def embroidery_created_by(self):
        from .models import EmbroideryReport
        r = EmbroideryReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None

    @property
    def printing_created_by(self):
        from .models import PrintingReport
        r = PrintingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None

    @property
    def singleneedle_created_by(self):
        from .models import SingleneedleReport
        r = SingleneedleReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None

    @property
    def sewing_created_by(self):
        from .models import SewingReport
        r = SewingReport.objects.filter(job_card_no=self.job_card_no).first()
        return r.created_by if r else None


# ── Accessories ──────────────────────────────────────────────────────────────

ACCESSORIES_ITEMS = [
    'MAIN CUM SIZE LABEL', 'LOOP LABEL', 'THREAD', 'ZIPPER', 'FUSING',
    'BUTTONS', 'HANGTAG', 'POLYBAG', 'BRANDING', 'CARTONS',
    'KIMBAL', 'HEAT TRANSFER', 'BAR CODES', 'DRAW CORD', 'ELASTIC',
]


class AccessoriesRecord(models.Model):
    """One record per job card — stores total_pcs from cutting report."""
    job_card_no = models.CharField(max_length=100, unique=True)
    total_pcs   = models.PositiveIntegerField(default=0)
    notes       = models.TextField(blank=True, null=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Accessories Record'

    def __str__(self):
        return f"Accessories — {self.job_card_no}"

    @property
    def is_started(self):
        for e in self.entries.all():
            if (e.qty_a is not None and e.qty_a > 0) or \
               (e.qty_b is not None and e.qty_b > 0) or \
               (e.qty_c is not None and e.qty_c > 0) or \
               (e.qty_d is not None and e.qty_d > 0) or \
               e.status_a in ['green', 'red'] or \
               e.status_b in ['green', 'red'] or \
               e.status_c in ['green', 'red'] or \
               e.status_d in ['green', 'red']:
                return True
        return False

    @property
    def is_complete(self):
        if not self.is_started:
            return False
        for e in self.entries.all():
            # Check A
            if e.qty_a and e.qty_a > 0:
                if e.status_a != 'green':
                    return False
            elif e.status_a == 'red':
                return False
            
            # Check B
            if e.qty_b and e.qty_b > 0:
                if e.status_b != 'green':
                    return False
            elif e.status_b == 'red':
                return False

            # Check C
            if e.qty_c and e.qty_c > 0:
                if e.status_c != 'green':
                    return False
            elif e.status_c == 'red':
                return False

            # Check D
            if e.qty_d and e.qty_d > 0:
                if e.status_d != 'green':
                    return False
            elif e.status_d == 'red':
                return False
        return True


class AccessoriesItemEntry(models.Model):
    """One row in the accessories table — one item per job card."""
    STATUS_CHOICES = [('green', 'Green'), ('red', 'Red'), ('', 'Not Set')]

    record    = models.ForeignKey(AccessoriesRecord, on_delete=models.CASCADE, related_name='entries')
    sr_no     = models.PositiveIntegerField()
    item_name = models.CharField(max_length=150)
    qty_a     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qty_b     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qty_c     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qty_d     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status_a  = models.CharField(max_length=10, choices=STATUS_CHOICES, default='', blank=True)
    status_b  = models.CharField(max_length=10, choices=STATUS_CHOICES, default='', blank=True)
    status_c  = models.CharField(max_length=10, choices=STATUS_CHOICES, default='', blank=True)
    status_d  = models.CharField(max_length=10, choices=STATUS_CHOICES, default='', blank=True)

    class Meta:
        ordering = ['sr_no']
        unique_together = ('record', 'sr_no')

    def __str__(self):
        return f"{self.record.job_card_no} — {self.item_name}"

    @property
    def total_a(self):
        if self.qty_a is not None and self.record.total_pcs:
            return int(self.record.total_pcs * self.qty_a)
        return None

    @property
    def total_b(self):
        if self.qty_b is not None and self.record.total_pcs:
            return int(self.record.total_pcs * self.qty_b)
        return None

    @property
    def total_c(self):
        if self.qty_c is not None and self.record.total_pcs:
            return int(self.record.total_pcs * self.qty_c)
        return None

    @property
    def total_d(self):
        if self.qty_d is not None and self.record.total_pcs:
            return int(self.record.total_pcs * self.qty_d)
        return None

    @property
    def grand_total(self):
        t = 0
        if self.total_a: t += self.total_a
        if self.total_b: t += self.total_b
        if self.total_c: t += self.total_c
        if self.total_d: t += self.total_d
        return t if t > 0 else None


class AccessoryCustomName(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


class AccessoriesPhoto(models.Model):
    """Up to 5 job card photos per AccessoriesRecord."""
    accessories_record = models.ForeignKey(
        AccessoriesRecord,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    photo_data = models.BinaryField()
    photo_name = models.CharField(max_length=255, default='photo.jpg')
    photo_content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.accessories_record}"


