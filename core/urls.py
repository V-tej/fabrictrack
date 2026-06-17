from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('master-entry/new/', views.create_master_entry, name='create_master_entry'),
    path('cutting-report/', views.cutting_report_view, name='cutting_report'),
    path('cr-lakshay/', views.person2_report_view, name='person2_report'),
    path('cr-rahul/', views.person3_report_view, name='person3_report'),
    path('stitching-miya-ji/', views.person4_report_view, name='person4_report'),
    path('job-work/', views.person5_report_view, name='person5_report'),
    path('finishing-report/', views.person6_report_view, name='person6_report'),
    path('users-reports/', views.users_reports_view, name='users_reports'),
    path('submissions/', views.submission_list_view, name='submission_list'),
    path('export/excel/', views.export_excel_view, name='export_excel'),
    path('job-card/<int:pk>/', views.job_card_detail_view, name='job_card_detail'),
    path('job-card/<int:pk>/print/', views.job_card_print_view, name='job_card_print'),

    # Edit Routes
    path('master-entry/<int:pk>/edit/', views.edit_master_entry, name='edit_master_entry'),
    path('cutting-report/<int:pk>/edit/', views.edit_cutting_report, name='edit_cutting_report'),
    path('cr-lakshay/<int:pk>/edit/', views.edit_person2_report, name='edit_person2_report'),
    path('cr-rahul/<int:pk>/edit/', views.edit_person3_report, name='edit_person3_report'),
    path('stitching-miya-ji/<int:pk>/edit/', views.edit_person4_report, name='edit_person4_report'),
    path('job-work/<int:pk>/edit/', views.edit_person5_report, name='edit_person5_report'),
    path('finishing-report/<int:pk>/edit/', views.edit_person6_report, name='edit_person6_report'),

    # Delete Routes
    path('master-entry/<int:pk>/delete/', views.delete_master_entry, name='delete_master_entry'),
    path('cutting-report/<int:pk>/delete/', views.delete_cutting_report, name='delete_cutting_report'),
    path('cr-lakshay/<int:pk>/delete/', views.delete_person2_report, name='delete_person2_report'),
    path('cr-rahul/<int:pk>/delete/', views.delete_person3_report, name='delete_person3_report'),
    path('stitching-miya-ji/<int:pk>/delete/', views.delete_person4_report, name='delete_person4_report'),
    path('job-work/<int:pk>/delete/', views.delete_person5_report, name='delete_person5_report'),
    path('finishing-report/<int:pk>/delete/', views.delete_person6_report, name='delete_person6_report'),
]
