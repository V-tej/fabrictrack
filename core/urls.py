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
    path('embroidery/', views.embroidery_report_view, name='embroidery_report'),
    path('printing/', views.printing_report_view, name='printing_report'),
    path('singleneedle/', views.singleneedle_report_view, name='singleneedle_report'),
    path('sewing/', views.sewing_report_view, name='sewing_report'),
    path('finishing-report/', views.finishing_report_view, name='finishing_report'),
    path('users-reports/', views.users_reports_view, name='users_reports'),
    path('submissions/', views.submission_list_view, name='submission_list'),
    path('export/options/', views.export_options_view, name='export_options'),
    path('export/excel/', views.export_excel_view, name='export_excel'),
    path('import/job-cards/', views.import_job_cards_view, name='import_job_cards'),
    path('download-sample-excel/', views.download_sample_excel_view, name='download_sample_excel'),
    path('download-database/', views.download_database, name='download_database'),
    path('db-image/<str:model_name>/<int:photo_id>/', views.serve_db_image, name='serve_db_image'),
    path('reset-database/', views.reset_database_view, name='reset_database'),
    path('job-card/<int:pk>/', views.job_card_detail_view, name='job_card_detail'),
    path('job-card/<int:pk>/print/', views.job_card_print_view, name='job_card_print'),

    # Ledger & Payment Routes
    path('ledger/unlock/', views.ledger_unlock_view, name='ledger_unlock'),
    path('ledger/lock/', views.ledger_lock_view, name='ledger_lock'),
    path('ledger/', views.master_ledger_list_view, name='master_ledger_list'),
    path('ledger/<int:pk>/', views.master_ledger_detail_view, name='master_ledger_detail'),
    path('ledger/payment/new/', views.record_payment_view, name='record_payment'),
    path('ledger/payment/<int:pk>/new/', views.record_payment_view, name='record_payment_for_master'),
    path('ledger/payment/delete/<int:pk>/', views.delete_payment_view, name='delete_payment'),
    path('api/master-outstanding/', views.get_master_outstanding_api, name='master_outstanding_api'),
    path('my-statement/', views.my_statement_view, name='my_statement'),
    path('my-statement/unlock/', views.my_statement_unlock_view, name='my_statement_unlock'),
    path('my-statement/lock/', views.my_statement_lock_view, name='my_statement_lock'),

    # Edit Routes
    path('master-entry/<int:pk>/edit/', views.edit_master_entry, name='edit_master_entry'),
    path('cutting-report/<int:pk>/edit/', views.edit_cutting_report, name='edit_cutting_report'),
    path('stitching-miya-ji/<int:pk>/edit/', views.edit_stitching_report, name='edit_stitching_report'),
    path('job-work/<int:pk>/edit/', views.edit_jobwork_report, name='edit_jobwork_report'),
    path('embroidery/<int:pk>/edit/', views.edit_embroidery_report, name='edit_embroidery_report'),
    path('printing/<int:pk>/edit/', views.edit_printing_report, name='edit_printing_report'),
    path('singleneedle/<int:pk>/edit/', views.edit_singleneedle_report, name='edit_singleneedle_report'),
    path('sewing/<int:pk>/edit/', views.edit_sewing_report, name='edit_sewing_report'),
    path('finishing-report/<int:pk>/edit/', views.edit_finishing_report, name='edit_finishing_report'),

    # Delete Routes
    path('master-entry/<int:pk>/delete/', views.delete_master_entry, name='delete_master_entry'),
    path('cutting-report/<int:pk>/delete/', views.delete_cutting_report, name='delete_cutting_report'),
    path('stitching-miya-ji/<int:pk>/delete/', views.delete_stitching_report, name='delete_stitching_report'),
    path('job-work/<int:pk>/delete/', views.delete_jobwork_report, name='delete_jobwork_report'),
    path('embroidery/<int:pk>/delete/', views.delete_embroidery_report, name='delete_embroidery_report'),
    path('printing/<int:pk>/delete/', views.delete_printing_report, name='delete_printing_report'),
    path('singleneedle/<int:pk>/delete/', views.delete_singleneedle_report, name='delete_singleneedle_report'),
    path('sewing/<int:pk>/delete/', views.delete_sewing_report, name='delete_sewing_report'),
    path('finishing-report/<int:pk>/delete/', views.delete_finishing_report, name='delete_finishing_report'),
    path('pending-task/<int:pk>/delete/', views.delete_pending_task, name='delete_pending_task'),

    # User Management Routes
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/add/', views.add_user, name='add_user'),
    path('manage-users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('manage-users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('manage-users/<int:user_id>/update-role/', views.update_user_role, name='update_user_role'),

    # Accessories Routes
    path('accessories/', views.accessories_view, name='accessories'),
    path('accessories/add-item/', views.accessories_add_item_view, name='accessories_add_item'),
    path('accessories-item/<int:pk>/delete/', views.accessories_delete_item_view, name='accessories_delete_item'),
    path('accessories/<str:job_card_no>/', views.accessories_detail_view, name='accessories_detail'),
    path('accessories/<str:job_card_no>/print/', views.accessories_print_view, name='accessories_print'),
    path('accessories-cell-photo/<int:entry_id>/<str:col>/', views.serve_accessories_cell_photo, name='serve_accessories_cell_photo'),
    path('vendor-photo/<int:vendor_id>/', views.serve_vendor_photo, name='serve_vendor_photo'),
    path('vendor-report/', views.vendor_report_view, name='vendor_report'),



    # Miscellaneous Report Routes
    path('miscellaneous/', views.miscellaneous_report_view, name='miscellaneous_report'),
    path('miscellaneous/list/', views.miscellaneous_report_list_view, name='miscellaneous_report_list'),
    path('miscellaneous/file/<int:file_id>/', views.serve_misc_file, name='serve_misc_file'),
    path('miscellaneous/<int:pk>/edit/', views.edit_miscellaneous_report, name='edit_miscellaneous_report'),
    path('miscellaneous/<int:pk>/delete/', views.delete_miscellaneous_report, name='delete_miscellaneous_report'),

    # P11 — Job Work 1
    path('job-work-1/', views.jobwork1_report_view, name='jobwork1_report'),
    path('job-work-1/<int:pk>/edit/', views.edit_jobwork1_report, name='edit_jobwork1_report'),
    path('job-work-1/<int:pk>/delete/', views.delete_jobwork1_report, name='delete_jobwork1_report'),
    
    # P12 — Sewing 1
    path('sewing-1/', views.sewing1_report_view, name='sewing1_report'),
    path('sewing-1/<int:pk>/edit/', views.edit_sewing1_report, name='edit_sewing1_report'),
    path('sewing-1/<int:pk>/delete/', views.delete_sewing1_report, name='delete_sewing1_report'),

    # Activity Log
    path('activity-log/', views.activity_log_view, name='activity_log'),

    # Progress Tracker (Admin)
    path('progress/', views.progress_tracker_view, name='progress_tracker'),

    # Print Report Route
    path('report/<str:report_type>/<int:pk>/print/', views.print_report_view, name='print_report'),

    # Team Chat (SlackTask-style)
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/bootstrap/', views.chat_bootstrap_api, name='chat_bootstrap_api'),
    path('api/chat/<int:channel_id>/messages/', views.chat_messages_api, name='chat_messages_api'),
    path('api/chat/<int:channel_id>/send/', views.chat_send_api, name='chat_send_api'),
    path('api/chat/message/<int:message_id>/to-task/', views.chat_message_to_task_api, name='chat_message_to_task'),
    path('api/chat/message/<int:message_id>/react/', views.chat_react_api, name='chat_react'),
    path('api/chat/message/<int:message_id>/bookmark/', views.chat_bookmark_api, name='chat_bookmark'),
    path('api/chat/message/<int:message_id>/pin/', views.chat_pin_api, name='chat_pin'),
    path('api/chat/message/<int:message_id>/edit/', views.chat_edit_api, name='chat_edit'),
    path('api/chat/message/<int:message_id>/delete/', views.chat_message_delete_api, name='chat_message_delete'),
    path('api/chat/message/<int:message_id>/image/', views.chat_message_image_api, name='chat_message_image'),
    path('api/chat/tasks/', views.chat_tasks_api, name='chat_tasks_api'),
    path('api/chat/tasks/<int:task_id>/toggle/', views.chat_task_toggle_api, name='chat_task_toggle'),
    path('api/chat/tasks/<int:task_id>/delete/', views.chat_task_delete_api, name='chat_task_delete'),
    path('api/chat/tasks/<int:task_id>/edit/', views.chat_task_edit_api, name='chat_task_edit'),
    path('api/chat/tasks/<int:task_id>/labels/', views.chat_task_labels_api, name='chat_task_labels'),
    path('api/chat/labels/', views.chat_labels_api, name='chat_labels'),
    path('api/chat/dm/open/', views.chat_open_dm_api, name='chat_open_dm'),
    path('api/chat/saved/', views.chat_saved_api, name='chat_saved_api'),
    path('api/chat/labels/<int:label_id>/delete/', views.chat_label_delete_api, name='chat_label_delete'),
    path('api/chat/jobcard-lookup/', views.chat_jobcard_lookup_api, name='chat_jobcard_lookup'),
]
