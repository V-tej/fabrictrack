import os
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
import json

from .models import MasterEntry, CuttingReport, CuttingReportPhoto, CuttingReportColorDetail, StitchingReport, StitchingReportPhoto, JobWorkReport, FinishingReport, FinishingReportPhoto, UserProfile, SystemSetting, JobCardRequirement
from .forms import MasterEntryForm, CuttingReportForm, StitchingReportForm, JobWorkReportForm, FinishingReportForm
from .utils import export_to_excel, generate_backup_zip


# ── Auth Views ──────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Dashboard ───────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    person_type = profile.person_type if profile else 'P1'

    context = {
        'person_type': person_type,
        'master_entries_count': MasterEntry.objects.count(),
        'cutting_reports_count': CuttingReport.objects.count(),
    }

    # Fetch recent reports based on role
    if person_type == 'ADMIN' or request.user.is_superuser:
        context['recent_reports'] = CuttingReport.objects.select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type in ['P1', 'P2', 'P3']:
        context['recent_reports'] = CuttingReport.objects.filter(created_by=request.user).select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P4':
        context['recent_reports'] = StitchingReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = StitchingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P5':
        context['recent_reports'] = JobWorkReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = JobWorkReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P6':
        context['recent_reports'] = FinishingReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = FinishingReport.objects.filter(created_by=request.user).count()

    # Fetch pending tasks
    if person_type == 'ADMIN' or request.user.is_superuser:
        context['pending_tasks'] = JobCardRequirement.objects.filter(
            Q(requires_cutting=True, is_cutting_done=False) |
            Q(requires_jobwork=True, is_jobwork_done=False) |
            Q(requires_stitching=True, is_stitching_done=False) |
            Q(requires_finishing=True, is_finishing_done=False)
        )
    elif person_type in ['P1', 'P2', 'P3']:
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_cutting=True, is_cutting_done=False)
    elif person_type == 'P4':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_stitching=True, is_stitching_done=False)
    elif person_type == 'P5':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_jobwork=True, is_jobwork_done=False)
    elif person_type == 'P6':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_finishing=True, is_finishing_done=False)
    else:
        context['pending_tasks'] = []

    if person_type == 'ADMIN' or request.user.is_superuser:
        context['master_form'] = MasterEntryForm()

    return render(request, 'dashboard.html', context)



# ── Manage Masters (Admin Only) ──────────────────────────────────────────────

@login_required
def manage_masters(request):
    try:
        person_type = request.user.profile.person_type
    except Exception:
        person_type = 'ADMIN'
        
    if person_type != 'ADMIN' and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')

    if request.method == 'POST':
        if 'add_master' in request.POST:
            name = request.POST.get('name')
            department = request.POST.get('department')
            if name and department:
                from .models import MasterName
                MasterName.objects.get_or_create(name=name.strip(), department=department)
                messages.success(request, f'Successfully added {name} to {department}!')
            return redirect('manage_masters')
            
        elif 'delete_master' in request.POST:
            master_id = request.POST.get('master_id')
            if master_id:
                from .models import MasterName
                master = MasterName.objects.filter(id=master_id).first()
                if master:
                    master.delete()
                    messages.success(request, 'Master name deleted successfully.')
            return redirect('manage_masters')

    from .models import MasterName
    masters = MasterName.objects.all().order_by('department', 'name')
    context = {
        'masters': masters,
        'person_type': person_type
    }
    return render(request, 'manage_masters.html', context)

# ── Master Entry (Admin) ─────────────────────────────────────────────────────

@login_required
def create_master_entry(request):
    if request.method == 'POST':
        form = MasterEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()

            # Also create/update JobCardRequirement based on the new boolean fields
            JobCardRequirement.objects.update_or_create(
                job_card_no=entry.job_card_number,
                defaults={
                    'date': entry.date,
                    'requires_cutting': form.cleaned_data.get('requires_cutting', True),
                    'requires_jobwork': form.cleaned_data.get('requires_jobwork', True),
                    'requires_stitching': form.cleaned_data.get('requires_stitching', True),
                    'requires_finishing': form.cleaned_data.get('requires_finishing', True),
                }
            )

            messages.success(request, f'Master entry "{entry}" created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = MasterEntryForm()
    return render(request, 'master_entry_form.html', {'form': form})

# ── Cutting Report (P1) ───────────────────────────────────────────────────────
@login_required
def cutting_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )
    is_p1 = hasattr(request.user, 'profile') and request.user.profile.person_type == 'P1'
    is_p2 = hasattr(request.user, 'profile') and request.user.profile.person_type == 'P2'
    is_p3 = hasattr(request.user, 'profile') and request.user.profile.person_type == 'P3'
    
    if not (is_admin or is_p1 or is_p2 or is_p3):
        raise PermissionDenied

    # A Job Card should only ever have ONE cutting report (by any master).
    # Once cut, it should disappear from the "New Report" dropdown for EVERYONE.
    master_entries_qs = MasterEntry.objects.filter(
        cutting_reports__isnull=True
    ).order_by('-date')

    # Build a JSON map: { entry_id: job_card_number } for JS auto-fill
    master_entries_json = json.dumps({
        str(e.id): e.job_card_number for e in master_entries_qs
    })

    if request.method == 'POST':
        form = CuttingReportForm(request.POST, request.FILES)
        form.fields['master_entry'].queryset = master_entries_qs
        photos = request.FILES.getlist('photos')

        # Validate photo count
        if len(photos) > 5:
            messages.error(request, 'You can upload a maximum of 5 photos.')
            return render(request, 'person1_form.html', {
                'form': form,
                'master_entries': master_entries_qs,
                'master_entries_json': master_entries_json,
                'is_admin': is_admin,
            })

        if len(photos) == 0:
            messages.error(request, 'Please upload at least one Job Card Photo.')
            return render(request, 'person1_form.html', {
                'form': form,
                'master_entries': master_entries_qs,
                'master_entries_json': master_entries_json,
                'is_admin': is_admin,
            })

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            
            # If the user is NOT an admin, forcefully override report_type based on their profile
            if not is_admin and hasattr(request.user, 'profile'):
                ptype = request.user.profile.person_type
                if ptype in ['P1', 'P2', 'P3']:
                    report.report_type = ptype

            
            
            report.save()

            # Save dynamic color size breakdown
            num_colors = report.total_colours
            if num_colors > 0:
                for i in range(1, num_colors + 1):
                    c_name = request.POST.get(f'color_name_{i}', f'C{i}')
                    c_s = int(request.POST.get(f'color_s_{i}') or 0)
                    c_m = int(request.POST.get(f'color_m_{i}') or 0)
                    c_l = int(request.POST.get(f'color_l_{i}') or 0)
                    c_xl = int(request.POST.get(f'color_xl_{i}') or 0)
                    c_2xl = int(request.POST.get(f'color_2xl_{i}') or 0)
                    c_3xl = int(request.POST.get(f'color_3xl_{i}') or 0)
                    c_4xl = int(request.POST.get(f'color_4xl_{i}') or 0)
                    c_weight = request.POST.get(f'color_weight_{i}') or 0.0
                    c_meters = request.POST.get(f'color_meters_{i}') or 0.0
                    CuttingReportColorDetail.objects.create(
                        cutting_report=report, color_name=c_name,
                        size_s=c_s, size_m=c_m, size_l=c_l, size_xl=c_xl,
                        size_2xl=c_2xl, size_3xl=c_3xl, size_4xl=c_4xl,
                        total_weight=c_weight, total_meters=c_meters
                    )

            # Save each photo to database
            for photo_file in photos:
                CuttingReportPhoto.objects.create(
                    cutting_report=report,
                    photo_data=photo_file.read(),
                    photo_name=photo_file.name,
                    photo_content_type=photo_file.content_type
                )

            # Update Excel export
            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            # Mark pending task as done
            JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(is_cutting_done=True)

            messages.success(request, 'Cutting Report submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CuttingReportForm()
        form.fields['master_entry'].queryset = master_entries_qs

    return render(request, 'person1_form.html', {
        'form': form,
        'master_entries': master_entries_qs,
        'master_entries_json': master_entries_json,
        'is_admin': is_admin,
    })


# ── P4: Stitching Report ───────────────────────────────────────────────

@login_required
def stitching_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        stitching_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_stitching=True).values('job_card_no')
    ).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = StitchingReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            photos = request.FILES.getlist('photos')
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return redirect('stitching_report')

            report = form.save(commit=False)
            report.created_by = request.user
            report.save()

            for p in photos[:5]:
                StitchingReportPhoto.objects.create(
                    stitching_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            # Mark pending task as done
            JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(is_stitching_done=True)

            messages.success(request, 'Stitching submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = StitchingReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'stitching_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'is_admin': is_admin,
    })


# ── P5: Job Work Report ───────────────────────────────────────────────

@login_required
def jobwork_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        jobwork_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_jobwork=True).values('job_card_no')
    ).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = JobWorkReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            # Mark pending task as done
            JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(is_jobwork_done=True)

            messages.success(request, 'Job Work submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobWorkReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'jobwork_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'is_admin': is_admin,
    })


# ── P6: Finishing Report ───────────────────────────────────────────────

@login_required
def finishing_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        finishing_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_finishing=True).values('job_card_no')
    ).select_related('master_entry').order_by('-created_at')

    # Build JSON map for auto-fill based on Cutting Report selection
    # We want to fill Date (from master_entry) and Lot No (from master_entry.job_card_number or cutting_report.job_card_no)
    # Since the user requested it comes from the cutting report, we'll map both:
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'date': cr.master_entry.date.strftime('%Y-%m-%d'),
            'lot_no': cr.job_card_no,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = FinishingReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) > 5:
            messages.error(request, 'You can upload a maximum of 5 photos.')
            return render(request, 'finishing_form.html', {
                'form': form,
                'cutting_reports': cutting_reports_qs,
                'cutting_reports_json': cutting_reports_json,
                'is_admin': is_admin,
            })

        if len(photos) == 0:
            messages.error(request, 'Please upload at least one Job Card Photo.')
            return render(request, 'finishing_form.html', {
                'form': form,
                'cutting_reports': cutting_reports_qs,
                'cutting_reports_json': cutting_reports_json,
                'is_admin': is_admin,
            })

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()

            for photo_file in photos:
                FinishingReportPhoto.objects.create(
                    finishing_report=report,
                    photo_data=photo_file.read(),
                    photo_name=photo_file.name,
                    photo_content_type=photo_file.content_type
                )

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            # Mark pending task as done
            JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(is_finishing_done=True)

            messages.success(request, 'Finishing Report submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = FinishingReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'finishing_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'is_admin': is_admin,
    })


# ── Submissions List ──────────────────────────────────────────────────────────

@login_required
def submission_list_view(request):
    profile = getattr(request.user, 'profile', None)
    person_type = profile.person_type if profile else 'P1'

    reports = []
    p4_reports = []
    p5_reports = []
    p6_reports = []

    if person_type in ['P1', 'P2', 'P3'] and not request.user.is_superuser:
        reports = CuttingReport.objects.filter(
            created_by=request.user
        ).select_related('master_entry').prefetch_related('photos').order_by('-created_at')
    elif person_type == 'P4' and not request.user.is_superuser:
        p4_reports = StitchingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
    elif person_type == 'P5' and not request.user.is_superuser:
        p5_reports = JobWorkReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
    elif person_type == 'P6' and not request.user.is_superuser:
        p6_reports = FinishingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related('photos').order_by('-created_at')
    else:
        reports = CuttingReport.objects.select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos').order_by('-created_at')
        p4_reports = StitchingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p5_reports = JobWorkReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p6_reports = FinishingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related('photos').order_by('-created_at')

    filter_param = request.GET.get('filter')
    
    # Split P4 reports into in_progress and completed
    p4_in_progress = [r for r in p4_reports if not r.line_out_date]
    p4_completed = [r for r in p4_reports if r.line_out_date]

    return render(request, 'submission_list.html', {
        'reports': reports,
        'p4_in_progress': p4_in_progress,
        'p4_completed': p4_completed,
        'p5_reports': p5_reports,
        'p6_reports': p6_reports,
        'person_type': person_type,
        'filter_param': filter_param,
        'show_p1': not filter_param or filter_param == 'p1',
        'show_p2': not filter_param or filter_param == 'p2',
        'show_p3': not filter_param or filter_param == 'p3',
        'show_p4': not filter_param or filter_param == 'p4',
        'show_p5': not filter_param or filter_param == 'p5',
        'show_p6': not filter_param or filter_param == 'p6',
    })


from django.core.exceptions import PermissionDenied

@login_required
def users_reports_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')):
        raise PermissionDenied

    query = request.GET.get('q', '').strip()

    p4_qs = StitchingReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at')
    p5_qs = JobWorkReport.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p6_qs = FinishingReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at')

    if query:
        p4_qs = p4_qs.filter(job_card_no__icontains=query)
        p5_qs = p5_qs.filter(job_card_no__icontains=query)
        p6_qs = p6_qs.filter(cutting_report__job_card_no__icontains=query)
        limit = 50
    else:
        limit = 5

    # Split P4 reports
    p4_in_progress = [r for r in p4_qs if not r.line_out_date][:limit]
    p4_completed = [r for r in p4_qs if r.line_out_date][:limit]

    context = {
        'search_query': query,
        'person1_reports_count': CuttingReport.objects.filter(report_type='P1').count(),
        'person2_reports_count': CuttingReport.objects.filter(report_type='P2').count(),
        'person3_reports_count': CuttingReport.objects.filter(report_type='P3').count(),
        'stitching_reports_count': StitchingReport.objects.count(),
        'jobwork_reports_count': JobWorkReport.objects.count(),
        'finishing_reports_count': FinishingReport.objects.count(),
        'recent_p4_in_progress': p4_in_progress,
        'recent_p4_completed': p4_completed,
        'recent_jobwork_reports': p5_qs[:limit],
        'recent_finishing_reports': p6_qs[:limit],
    }
    return render(request, 'users_reports.html', context)

# ── QR Code & Detail Views ──────────────────────────────────────────────────

def job_card_detail_view(request, pk):
    """Publicly accessible view for scanned QR codes"""
    master_entry = get_object_or_404(MasterEntry, pk=pk)
    report_type = request.GET.get('type', None)  # e.g. P1, P2, P3, P4, P5, P6

    # Get all cutting reports grouped by type
    all_cutting = master_entry.cutting_reports.prefetch_related('color_details', 'photos').all()

    # Resolve which reports to show based on ?type= param
    show_all = report_type is None or report_type == 'ADMIN'

    p1_report = all_cutting.filter(report_type='P1').first() if (show_all or report_type == 'P1') else None
    p2_report = all_cutting.filter(report_type='P2').first() if (show_all or report_type == 'P2') else None
    p3_report = all_cutting.filter(report_type='P3').first() if (show_all or report_type == 'P3') else None

    # Link subsequent reports (P4, P5, P6) to whatever cutting report was submitted
    base_cutting = all_cutting.first()
    stitching_report = base_cutting.stitching_reports.first() if (base_cutting and (show_all or report_type == 'P4')) else None
    jobwork_report = base_cutting.jobwork_reports.first() if (base_cutting and (show_all or report_type == 'P5')) else None
    finishing_report = base_cutting.finishing_reports.first() if (base_cutting and (show_all or report_type == 'P6')) else None

    return render(request, 'job_card_detail.html', {
        'master_entry': master_entry,
        'cutting_report': p1_report,
        'person2_report': p2_report,
        'person3_report': p3_report,
        'stitching_report': stitching_report,
        'jobwork_report': jobwork_report,
        'finishing_report': finishing_report,
        'report_type': report_type,
    })

@login_required
def job_card_print_view(request, pk):
    """View to generate and print the QR code — embeds user's person_type in URL"""
    master_entry = get_object_or_404(MasterEntry, pk=pk)

    # Determine the person type of the current user
    try:
        person_type = request.user.profile.person_type
    except Exception:
        person_type = None

    # Build URL with type filter so QR only shows that user's report
    base_url = request.build_absolute_uri(f'/job-card/{pk}/')
    if person_type and person_type != 'ADMIN':
        qr_url = f"{base_url}?type={person_type}"
    else:
        qr_url = base_url  # Admins see all

    return render(request, 'job_card_print.html', {
        'master_entry': master_entry,
        'qr_url': qr_url,
    })

# ── Excel Download ────────────────────────────────────────────────────────────

from django.utils import timezone

@login_required
def export_options_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    settings = SystemSetting.get_settings()
    
    return render(request, 'export_options.html', {
        'last_download_at': settings.last_excel_download_at
    })

@login_required
def export_excel_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied
        
    export_type = request.GET.get('type', 'all')
    settings = SystemSetting.get_settings()
    
    since_date = None
    if export_type == 'new' and settings.last_excel_download_at:
        since_date = settings.last_excel_download_at
        
    try:
        filepath = export_to_excel(since_date=since_date)
        if os.path.exists(filepath):
            # Update last downloaded time
            settings.last_excel_download_at = timezone.now()
            settings.save()
            
            response = FileResponse(
                open(filepath, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="FabricTrack_Data.xlsx"'
            return response
        raise Http404("Export file not found.")
    except Exception as e:
        messages.error(request, f'Export failed: {e}')
        return redirect('dashboard')

import openpyxl
from datetime import datetime

@login_required
def import_job_cards_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Assuming headers in row 1: Date, Jobcard number, Cutting, Jobworker, Stiching, Finishing
            # We will find the column indices dynamically to be safe
            headers = [cell.value for cell in sheet[1]]
            header_map = {str(h).strip().lower(): idx for idx, h in enumerate(headers) if h}
            
            # Check required columns
            required_cols = ['jobcard number']
            if not all(col in header_map for col in required_cols):
                messages.error(request, f"Missing required columns. Found headers: {', '.join([str(h) for h in headers if h])}")
                return redirect('create_master_entry')
            
            created_count = 0
            updated_count = 0
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                job_card_no = str(row[header_map.get('jobcard number', -1)]).strip()
                if not job_card_no or job_card_no == 'None': continue
                
                def get_val(key1, key2=None):
                    idx = header_map.get(key1)
                    if idx is None and key2:
                        idx = header_map.get(key2)
                    if idx is not None and idx < len(row):
                        return row[idx]
                    return None
                
                def is_yes(val):
                    return str(val).strip().lower() == 'yes' if val else False
                
                cutting_req = is_yes(get_val('cutting'))
                jobwork_req = is_yes(get_val('jobwork', 'jobworker'))
                stitching_req = is_yes(get_val('stitching', 'stiching'))
                finishing_req = is_yes(get_val('finishing'))
                
                # Parse date if possible
                date_val = row[header_map.get('date', -1)]
                if isinstance(date_val, datetime):
                    date_obj = date_val.date()
                elif date_val:
                    try:
                        date_obj = datetime.strptime(str(date_val).strip(), '%m/%d/%Y').date()
                    except ValueError:
                        date_obj = timezone.now().date()
                else:
                    date_obj = timezone.now().date()

                obj, created = JobCardRequirement.objects.update_or_create(
                    job_card_no=job_card_no,
                    defaults={
                        'date': date_obj,
                        'requires_cutting': cutting_req,
                        'requires_jobwork': jobwork_req,
                        'requires_stitching': stitching_req,
                        'requires_finishing': finishing_req,
                    }
                )

                # Create MasterEntry if it doesn't exist
                MasterEntry.objects.get_or_create(
                    job_card_number=job_card_no,
                    defaults={
                        'date': date_obj,
                        'created_by': request.user
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            messages.success(request, f"Successfully imported! Created {created_count} new tasks, updated {updated_count} existing tasks.")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            
        return redirect('create_master_entry')
        
    return redirect('create_master_entry')

# ── Edit and Delete Views ───────────────────────────────────────────────────

@login_required
@require_POST
def delete_pending_task(request, pk):
    if not request.user.is_superuser and getattr(request.user, 'profile', None) and request.user.profile.person_type != 'ADMIN':
        raise PermissionDenied
    task = get_object_or_404(JobCardRequirement, pk=pk)
    task.delete()
    messages.success(request, f"Pending task for {task.job_card_no} deleted.")
    return redirect('dashboard')


from django.core.exceptions import PermissionDenied

def check_edit_permission(request, obj):
    if request.user.is_superuser: return True
    if hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN': return True
    if getattr(obj, 'created_by', None) == request.user: return True
    return False

@login_required
def edit_master_entry(request, pk):
    entry = get_object_or_404(MasterEntry, pk=pk)
    if not check_edit_permission(request, entry): raise PermissionDenied
    if request.method == 'POST':
        form = MasterEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_at = timezone.now()
            entry.save()
            
            # Update the JobCardRequirement as well
            JobCardRequirement.objects.update_or_create(
                job_card_no=entry.job_card_number,
                defaults={
                    'date': entry.date,
                    'requires_cutting': form.cleaned_data.get('requires_cutting', True),
                    'requires_jobwork': form.cleaned_data.get('requires_jobwork', True),
                    'requires_stitching': form.cleaned_data.get('requires_stitching', True),
                    'requires_finishing': form.cleaned_data.get('requires_finishing', True),
                }
            )
            
            messages.success(request, 'Master entry updated.')
            export_to_excel()
            return redirect('dashboard')
    else:
        # Pre-fill form with existing JobCardRequirement values
        req = JobCardRequirement.objects.filter(job_card_no=entry.job_card_number).first()
        initial_data = {}
        if req:
            initial_data = {
                'requires_cutting': 'True' if req.requires_cutting else 'False',
                'requires_jobwork': 'True' if req.requires_jobwork else 'False',
                'requires_stitching': 'True' if req.requires_stitching else 'False',
                'requires_finishing': 'True' if req.requires_finishing else 'False',
            }
        form = MasterEntryForm(instance=entry, initial=initial_data)
    return render(request, 'master_entry_form.html', {'form': form, 'is_edit': True})

@login_required
def delete_master_entry(request, pk):
    entry = get_object_or_404(MasterEntry, pk=pk)
    if not check_edit_permission(request, entry): raise PermissionDenied
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Master entry deleted.')
        export_to_excel()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': entry, 'cancel_url': 'dashboard'})

@login_required
def edit_cutting_report(request, pk):
    report = get_object_or_404(CuttingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    
    # Handle photo deletion if requested via URL param
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(CuttingReportPhoto, pk=delete_photo_id, cutting_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect(request.path)

    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    master_entries_qs = MasterEntry.objects.filter(Q(cutting_reports__isnull=True) | Q(id=report.master_entry_id)).distinct().order_by('-date')
    master_entries_json = json.dumps({str(e.id): e.job_card_number for e in master_entries_qs})
    colors_qs = report.color_details.order_by('id')
    colors_json = json.dumps([
        {
            'color_name': c.color_name,
            'size_s': c.size_s, 'size_m': c.size_m, 'size_l': c.size_l, 'size_xl': c.size_xl,
            'size_2xl': c.size_2xl, 'size_3xl': c.size_3xl, 'size_4xl': c.size_4xl,
            'total_weight': float(c.total_weight) if c.total_weight is not None else 0.0,
            'total_meters': float(c.total_meters) if c.total_meters is not None else 0.0,
        } for c in colors_qs
    ])
    
    if request.method == 'POST':
        form = CuttingReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            report.save()
            
            # Re-save dynamic color size breakdown
            report.color_details.all().delete()
            num_colors = report.total_colours
            if num_colors > 0:
                for i in range(1, num_colors + 1):
                    c_name = request.POST.get(f'color_name_{i}', f'C{i}')
                    c_s = int(request.POST.get(f'color_s_{i}') or 0)
                    c_m = int(request.POST.get(f'color_m_{i}') or 0)
                    c_l = int(request.POST.get(f'color_l_{i}') or 0)
                    c_xl = int(request.POST.get(f'color_xl_{i}') or 0)
                    c_2xl = int(request.POST.get(f'color_2xl_{i}') or 0)
                    c_3xl = int(request.POST.get(f'color_3xl_{i}') or 0)
                    c_4xl = int(request.POST.get(f'color_4xl_{i}') or 0)
                    c_weight = request.POST.get(f'color_weight_{i}') or 0.0
                    c_meters = request.POST.get(f'color_meters_{i}') or 0.0
                    CuttingReportColorDetail.objects.create(
                        cutting_report=report, color_name=c_name,
                        size_s=c_s, size_m=c_m, size_l=c_l, size_xl=c_xl,
                        size_2xl=c_2xl, size_3xl=c_3xl, size_4xl=c_4xl,
                        total_weight=c_weight, total_meters=c_meters
                    )
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    CuttingReportPhoto.objects.create(
                        cutting_report=report,
                        photo_data=photo_file.read(),
                        photo_name=photo_file.name,
                        photo_content_type=photo_file.content_type
                    )
            messages.success(request, 'Cutting Report updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = CuttingReportForm(instance=report)
    return render(request, 'person1_form.html', {
        'form': form, 'master_entries': master_entries_qs,
        'master_entries_json': master_entries_json, 'is_admin': is_admin, 'is_edit': True, 'report': report,
        'colors_json': colors_json
    })

@login_required
def delete_cutting_report(request, pk):
    report = get_object_or_404(CuttingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Cutting Report deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_stitching_report(request, pk):
    report = get_object_or_404(StitchingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(stitching_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(StitchingReportPhoto, pk=delete_photo_id, stitching_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_stitching_report', pk=report.id)

    if request.method == 'POST':
        form = StitchingReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return redirect('edit_stitching_report', pk=report.id)

        if form.is_valid():
            report = form.save(commit=False)
            report.save()

            for p in photos:
                StitchingReportPhoto.objects.create(
                    stitching_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            messages.success(request, 'Stitching updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = StitchingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'stitching_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_stitching_report(request, pk):
    report = get_object_or_404(StitchingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Stitching deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_jobwork_report(request, pk):
    report = get_object_or_404(JobWorkReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(jobwork_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    if request.method == 'POST':
        form = JobWorkReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            report.save()
            messages.success(request, 'Job Work updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = JobWorkReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'jobwork_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_jobwork_report(request, pk):
    report = get_object_or_404(JobWorkReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Job Work deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_finishing_report(request, pk):
    report = get_object_or_404(FinishingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    
    # Handle photo deletion if requested via URL param
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(FinishingReportPhoto, pk=delete_photo_id, finishing_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect(request.path)

    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(finishing_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'date': cr.master_entry.date.strftime('%Y-%m-%d'),
            'lot_no': cr.job_card_no,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    if request.method == 'POST':
        form = FinishingReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            report.save()
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    FinishingReportPhoto.objects.create(
                        finishing_report=report,
                        photo_data=photo_file.read(),
                        photo_name=photo_file.name,
                        photo_content_type=photo_file.content_type
                    )
            messages.success(request, 'Finishing Report updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = FinishingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'finishing_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_finishing_report(request, pk):
    report = get_object_or_404(FinishingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Finishing Report deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

from django.utils import timezone

@login_required
def download_database(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can download the database backup.")
    
    try:
        zip_buffer = generate_backup_zip()
        
        # Update last downloaded time
        system_settings = SystemSetting.get_settings()
        system_settings.last_excel_download_at = timezone.now()
        system_settings.save()
        
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="FabricTrack_Backup.zip"'
        return response
    except Exception as e:
        messages.error(request, f'Backup failed: {e}')
        return redirect('dashboard')


def serve_db_image(request, model_name, photo_id):
    if model_name == 'cutting':
        photo = get_object_or_404(CuttingReportPhoto, pk=photo_id)
    elif model_name == 'finishing':
        photo = get_object_or_404(FinishingReportPhoto, pk=photo_id)
    elif model_name == 'p4':
        photo = get_object_or_404(StitchingReportPhoto, pk=photo_id)
    else:
        raise Http404("Invalid photo model")
    
    response = HttpResponse(photo.photo_data, content_type=photo.photo_content_type)
    response['Content-Disposition'] = f'inline; filename="{photo.photo_name}"'
    return response


@login_required
def reset_database_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can reset the database.")
    
    if request.method == 'POST':
        # Delete MasterEntry (cascades to all other data including reports, colors, photos)
        MasterEntry.objects.all().delete()
        
        # Reset last downloaded time
        system_settings = SystemSetting.get_settings()
        system_settings.last_excel_download_at = None
        system_settings.save()
        
        try:
            export_to_excel()
        except Exception:
            pass
            
        messages.success(request, 'Database successfully reset! All master entries, reports, and photos have been permanently deleted.')
        return redirect('dashboard')
        
    return render(request, 'confirm_reset.html')
