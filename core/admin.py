from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    UserProfile, MasterEntry, CuttingReport, CuttingReportPhoto,
    StitchingReport, StitchingReportPhoto, JobWorkReport, JobWorkReportPhoto,
    FinishingReport, FinishingReportPhoto, EmbroideryReport,
    EmbroideryReportPhoto, PrintingReport, PrintingReportPhoto,
    SingleneedleReport, SingleneedleReportPhoto, SewingReport,
    SewingReportPhoto, MasterName, JobCardRequirement, RateDefinition,
    JobWork1Report, JobWork1ReportPhoto, Sewing1Report, Sewing1ReportPhoto
)


# Inline UserProfile registration under User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'person_type']
    list_editable = ['person_type']
    search_fields = ['user__username']


class CuttingReportPhotoInline(admin.TabularInline):
    model = CuttingReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(MasterEntry)
class MasterEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'job_card_number', 'created_by', 'created_at']
    list_filter = ['date']
    search_fields = ['job_card_number']
    date_hierarchy = 'date'


@admin.register(CuttingReport)
class CuttingReportAdmin(admin.ModelAdmin):
    list_display = [
        'master_entry', 'item_name', 'master_name', 'cutting_master_name',
        'rate_name', 'cutting_rate', 'total_pcs', 'total_colours', 'created_by', 'created_at'
    ]
    list_filter = ['master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'cutting_master_name']
    inlines = [CuttingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(CuttingReportPhoto)
class CuttingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['cutting_report', 'photo_name', 'uploaded_at']



class StitchingReportPhotoInline(admin.TabularInline):
    model = StitchingReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(StitchingReport)
class StitchingReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'stitching_master_name', 'item_name', 'job_card_no',
        'rate_name', 'rate_description', 'total_rate', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'stitching_master_name']
    inlines = [StitchingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(StitchingReportPhoto)
class StitchingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['stitching_report', 'photo_name', 'uploaded_at']


class JobWorkReportPhotoInline(admin.TabularInline):
    model = JobWorkReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(JobWorkReport)
class JobWorkReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'jobworker', 'jobwork_in', 'jobwork_out',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['jobwork_in', 'jobwork_out', 'created_by']
    search_fields = ['master_name', 'finishing_master_name', 'job_card_no']
    inlines = [JobWorkReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(JobWorkReportPhoto)
class JobWorkReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['job_work_report', 'photo_name', 'uploaded_at']


class JobWork1ReportPhotoInline(admin.TabularInline):
    model = JobWork1ReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(JobWork1Report)
class JobWork1ReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'jobworker', 'jobwork_in', 'jobwork_out',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['jobwork_in', 'jobwork_out', 'created_by']
    search_fields = ['master_name', 'job_card_no']
    inlines = [JobWork1ReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(JobWork1ReportPhoto)
class JobWork1ReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['job_work1_report', 'photo_name', 'uploaded_at']



class FinishingReportPhotoInline(admin.TabularInline):
    model = FinishingReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(FinishingReport)
class FinishingReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'finishing_master_name', 'lot_no', 'date',
        'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['date', 'created_by']
    search_fields = ['lot_no', 'master_name', 'finishing_master_name']
    inlines = [FinishingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(FinishingReportPhoto)
class FinishingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['finishing_report', 'photo_name', 'uploaded_at']


class EmbroideryReportPhotoInline(admin.TabularInline):
    model = EmbroideryReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(EmbroideryReport)
class EmbroideryReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'embroidery_worker', 'embroidery_in', 'embroidery_out',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['embroidery_in', 'embroidery_out', 'created_by']
    search_fields = ['master_name', 'embroidery_worker', 'job_card_no']
    inlines = [EmbroideryReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(EmbroideryReportPhoto)
class EmbroideryReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['embroidery_report', 'photo_name', 'uploaded_at']


class PrintingReportPhotoInline(admin.TabularInline):
    model = PrintingReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(PrintingReport)
class PrintingReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'printing_worker', 'printing_in', 'printing_out',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['printing_in', 'printing_out', 'created_by']
    search_fields = ['master_name', 'printing_worker', 'job_card_no']
    inlines = [PrintingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(PrintingReportPhoto)
class PrintingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['printing_report', 'photo_name', 'uploaded_at']


class SingleneedleReportPhotoInline(admin.TabularInline):
    model = SingleneedleReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(SingleneedleReport)
class SingleneedleReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'singleneedle_master_name', 'item_name', 'job_card_no',
        'rate_name', 'rate_description', 'total_rate', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'singleneedle_master_name']
    inlines = [SingleneedleReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(SingleneedleReportPhoto)
class SingleneedleReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['singleneedle_report', 'photo_name', 'uploaded_at']


class SewingReportPhotoInline(admin.TabularInline):
    model = SewingReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(SewingReport)
class SewingReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'sewing_master_name', 'item_name', 'job_card_no',
        'rate_name', 'rate_description', 'total_rate', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'sewing_master_name']
    inlines = [SewingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(SewingReportPhoto)
class SewingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['sewing_report', 'photo_name', 'uploaded_at']


class Sewing1ReportPhotoInline(admin.TabularInline):
    model = Sewing1ReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Sewing1Report)
class Sewing1ReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'sewing_master_name', 'item_name', 'job_card_no',
        'rate_name', 'rate_description', 'total_rate', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'sewing_master_name']
    inlines = [Sewing1ReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(Sewing1ReportPhoto)
class Sewing1ReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['sewing1_report', 'photo_name', 'uploaded_at']



@admin.register(MasterName)
class MasterNameAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']


@admin.register(JobCardRequirement)
class JobCardRequirementAdmin(admin.ModelAdmin):
    list_display = [
        'job_card_no', 'date',
        'requires_cutting', 'is_cutting_done',
        'requires_jobwork', 'is_jobwork_done',
        'requires_stitching', 'is_stitching_done',
        'requires_singleneedle', 'is_singleneedle_done',
        'requires_sewing', 'is_sewing_done',
        'requires_embroidery', 'is_embroidery_done',
        'requires_printing', 'is_printing_done',
        'requires_finishing', 'is_finishing_done',
    ]
    list_filter = ['date']
    search_fields = ['job_card_no']


@admin.register(RateDefinition)
class RateDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'total_rate']
    search_fields = ['name', 'description']


