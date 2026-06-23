from django.contrib import admin
from .models import UserProfile, MasterEntry, CuttingReport, CuttingReportPhoto, StitchingReport, JobWorkReport, FinishingReport, FinishingReportPhoto


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
        'total_pcs', 'total_colours', 'created_by', 'created_at'
    ]
    list_filter = ['master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'cutting_master_name']
    inlines = [CuttingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(CuttingReportPhoto)
class CuttingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['cutting_report', 'photo_name', 'uploaded_at']



@admin.register(StitchingReport)
class StitchingReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'stitching_master_name', 'item_name', 'job_card_no',
        'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'master_name', 'stitching_master_name']
    readonly_fields = ['created_at']


@admin.register(JobWorkReport)
class JobWorkReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'master_name', 'jobworker', 'job_work_type',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['date', 'job_work_type', 'created_by']
    search_fields = ['master_name', 'finishing_master_name', 'job_card_no']
    readonly_fields = ['created_at']


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
