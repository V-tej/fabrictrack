from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('master-entry/new/', views.create_master_entry, name='create_master_entry'),
    path('manage-masters/', views.manage_masters, name='manage_masters'),
    path('cutting-report/', views.cutting_report_view, name='cutting_report'),
    path('stitching-miya-ji/', views.stitching_report_view, name='stitching_report'),
    path('job-work/', views.jobwork_report_view, name='jobwork_report'),
    path('finishing-report/', views.finishing_report_view, name='finishing_report'),
    path('users-reports/', views.users_reports_view, name='users_reports'),
    path('submissions/', views.submission_list_view, name='submission_list'),
    path('export/options/', views.export_options_view, name='export_options'),
    path('export/excel/', views.export_excel_view, name='export_excel'),
    path('import/job-cards/', views.import_job_cards_view, name='import_job_cards'),
    path('download-database/', views.download_database, name='download_database'),
    path('db-image/<str:model_name>/<int:photo_id>/', views.serve_db_image, name='serve_db_image'),
    path('reset-database/', views.reset_database_view, name='reset_database'),
    path('job-card/<int:pk>/', views.job_card_detail_view, name='job_card_detail'),
    path('job-card/<int:pk>/print/', views.job_card_print_view, name='job_card_print'),

    # Edit Routes
    path('master-entry/<int:pk>/edit/', views.edit_master_entry, name='edit_master_entry'),
    path('cutting-report/<int:pk>/edit/', views.edit_cutting_report, name='edit_cutting_report'),
    path('stitching-miya-ji/<int:pk>/edit/', views.edit_stitching_report, name='edit_stitching_report'),
    path('job-work/<int:pk>/edit/', views.edit_jobwork_report, name='edit_jobwork_report'),
    path('finishing-report/<int:pk>/edit/', views.edit_finishing_report, name='edit_finishing_report'),

    # Delete Routes
    path('master-entry/<int:pk>/delete/', views.delete_master_entry, name='delete_master_entry'),
    path('cutting-report/<int:pk>/delete/', views.delete_cutting_report, name='delete_cutting_report'),
    path('stitching-miya-ji/<int:pk>/delete/', views.delete_stitching_report, name='delete_stitching_report'),
    path('job-work/<int:pk>/delete/', views.delete_jobwork_report, name='delete_jobwork_report'),
    path('finishing-report/<int:pk>/delete/', views.delete_finishing_report, name='delete_finishing_report'),
    path('pending-task/<int:pk>/delete/', views.delete_pending_task, name='delete_pending_task'),
]
