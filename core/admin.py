from django.contrib import admin
from .models import UserProfile, MasterEntry, CuttingReport, CuttingReportPhoto, Person4Report, Person5Report, Person6Report, Person6ReportPhoto


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
        'master_entry', 'item_name', 'cutting_master_name',
        'total_pcs', 'total_colours', 'created_by', 'created_at'
    ]
    list_filter = ['master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no', 'cutting_master_name']
    inlines = [CuttingReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(CuttingReportPhoto)
class CuttingReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['cutting_report', 'photo_name', 'uploaded_at']



@admin.register(Person4Report)
class Person4ReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'item_name', 'job_card_no',
        'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'created_by']
    search_fields = ['item_name', 'job_card_no']
    readonly_fields = ['created_at']


@admin.register(Person5Report)
class Person5ReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'jobworker', 'job_work_type',
        'job_card_no', 'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'job_work_type', 'created_by']
    search_fields = ['jobworker', 'job_card_no', 'purpose']
    readonly_fields = ['created_at']


class Person6ReportPhotoInline(admin.TabularInline):
    model = Person6ReportPhoto
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Person6Report)
class Person6ReportAdmin(admin.ModelAdmin):
    list_display = [
        'cutting_report', 'lot_no', 'date',
        'total_pcs', 'created_by', 'created_at'
    ]
    list_filter = ['cutting_report__master_entry__date', 'date', 'created_by']
    search_fields = ['lot_no']
    inlines = [Person6ReportPhotoInline]
    readonly_fields = ['created_at']


@admin.register(Person6ReportPhoto)
class Person6ReportPhotoAdmin(admin.ModelAdmin):
    list_display = ['person6_report', 'photo_name', 'uploaded_at']
