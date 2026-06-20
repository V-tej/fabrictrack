import os
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.views.decorators.http import require_POST
import json

from .models import MasterEntry, CuttingReport, CuttingReportPhoto, CuttingReportColorDetail, Person4Report, Person5Report, Person6Report, Person6ReportPhoto, UserProfile, SystemSetting
from .forms import MasterEntryForm, CuttingReportForm, Person4ReportForm, Person5ReportForm, Person6ReportForm
from .utils import export_to_excel


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
    if person_type == 'P1' or person_type == 'ADMIN' or request.user.is_superuser:
        context['recent_reports'] = CuttingReport.objects.select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P2':
        context['recent_reports'] = CuttingReport.objects.filter(created_by=request.user).select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P3':
        context['recent_reports'] = CuttingReport.objects.filter(created_by=request.user).select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P4':
        context['recent_reports'] = Person4Report.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = Person4Report.objects.filter(created_by=request.user).count()

    elif person_type == 'P5':
        context['recent_reports'] = Person5Report.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = Person5Report.objects.filter(created_by=request.user).count()

    elif person_type == 'P6':
        context['recent_reports'] = Person6Report.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related('photos')[:5]
        context['user_submissions_count'] = Person6Report.objects.filter(created_by=request.user).count()

    if person_type == 'ADMIN' or request.user.is_superuser:
        context['master_form'] = MasterEntryForm()

    return render(request, 'dashboard.html', context)


# ── Master Entry (Admin) ─────────────────────────────────────────────────────

@login_required
def create_master_entry(request):
    if request.method == 'POST':
        form = MasterEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = request.user
            entry.save()
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

            # Auto-fill cutting_master_name if empty
            if not report.cutting_master_name:
                if report.report_type == 'P1':
                    report.cutting_master_name = 'Cutting Master'
                elif report.report_type == 'P2':
                    report.cutting_master_name = 'CR Lakshay'
                elif report.report_type == 'P3':
                    report.cutting_master_name = 'CR Rahul'
            
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
                    c_weight = request.POST.get(f'color_weight_{i}') or None
                    c_unit = request.POST.get(f'color_unit_{i}') or 'Weight'
                    CuttingReportColorDetail.objects.create(
                        cutting_report=report, color_name=c_name,
                        size_s=c_s, size_m=c_m, size_l=c_l, size_xl=c_xl,
                        size_2xl=c_2xl, size_3xl=c_3xl, size_4xl=c_4xl,
                        total_weight_meter=c_weight, unit=c_unit
                    )

            # Save each photo
            for photo_file in photos:
                CuttingReportPhoto.objects.create(
                    cutting_report=report,
                    photo=photo_file,
                )

            # Update Excel export
            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

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


# ── P4: Stitching Miya Ji Report ───────────────────────────────────────────────

@login_required
def person4_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(person4_reports__isnull=True).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = Person4ReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            messages.success(request, 'Stitching Miya Ji submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = Person4ReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'person4_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'is_admin': is_admin,
    })


# ── P5: Job Work Report ───────────────────────────────────────────────

@login_required
def person5_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(person5_reports__isnull=True).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = Person5ReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            messages.success(request, 'Job Work submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = Person5ReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'person5_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'is_admin': is_admin,
    })


# ── P6: Finishing Report ───────────────────────────────────────────────

@login_required
def person6_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(person6_reports__isnull=True).select_related('master_entry').order_by('-created_at')

    # Build JSON map for auto-fill based on Cutting Report selection
    # We want to fill Date (from master_entry) and Lot No (from master_entry.job_card_number or cutting_report.job_card_no)
    # Since the user requested it comes from the cutting report, we'll map both:
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'date': cr.master_entry.date.strftime('%Y-%m-%d'),
            'lot_no': cr.job_card_no,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    if request.method == 'POST':
        form = Person6ReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) > 5:
            messages.error(request, 'You can upload a maximum of 5 photos.')
            return render(request, 'person6_form.html', {
                'form': form,
                'cutting_reports': cutting_reports_qs,
                'cutting_reports_json': cutting_reports_json,
                'is_admin': is_admin,
            })

        if len(photos) == 0:
            messages.error(request, 'Please upload at least one Job Card Photo.')
            return render(request, 'person6_form.html', {
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
                Person6ReportPhoto.objects.create(
                    person6_report=report,
                    photo=photo_file,
                )

            try:
                export_to_excel()
            except Exception as e:
                messages.warning(request, f'Report saved but Excel export failed: {e}')

            messages.success(request, 'Finishing Report submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = Person6ReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'person6_form.html', {
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
        p4_reports = Person4Report.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
    elif person_type == 'P5' and not request.user.is_superuser:
        p5_reports = Person5Report.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
    elif person_type == 'P6' and not request.user.is_superuser:
        p6_reports = Person6Report.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related('photos').order_by('-created_at')
    else:
        reports = CuttingReport.objects.select_related(
            'master_entry', 'created_by'
        ).prefetch_related('photos').order_by('-created_at')
        p4_reports = Person4Report.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p5_reports = Person5Report.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p6_reports = Person6Report.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related('photos').order_by('-created_at')

    filter_param = request.GET.get('filter')
    return render(request, 'submission_list.html', {
        'reports': reports,
        'p4_reports': p4_reports,
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

    p4_qs = Person4Report.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p5_qs = Person5Report.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p6_qs = Person6Report.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at')

    if query:
        p4_qs = p4_qs.filter(job_card_no__icontains=query)
        p5_qs = p5_qs.filter(job_card_no__icontains=query)
        p6_qs = p6_qs.filter(cutting_report__job_card_no__icontains=query)
        limit = 50
    else:
        limit = 5

    context = {
        'search_query': query,
        'person1_reports_count': CuttingReport.objects.filter(report_type='P1').count(),
        'person2_reports_count': CuttingReport.objects.filter(report_type='P2').count(),
        'person3_reports_count': CuttingReport.objects.filter(report_type='P3').count(),
        'person4_reports_count': Person4Report.objects.count(),
        'person5_reports_count': Person5Report.objects.count(),
        'person6_reports_count': Person6Report.objects.count(),
        'recent_person4_reports': p4_qs[:limit],
        'recent_person5_reports': p5_qs[:limit],
        'recent_person6_reports': p6_qs[:limit],
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
    person4_report = base_cutting.person4_reports.first() if (base_cutting and (show_all or report_type == 'P4')) else None
    person5_report = base_cutting.person5_reports.first() if (base_cutting and (show_all or report_type == 'P5')) else None
    person6_report = base_cutting.person6_reports.first() if (base_cutting and (show_all or report_type == 'P6')) else None

    return render(request, 'job_card_detail.html', {
        'master_entry': master_entry,
        'cutting_report': p1_report,
        'person2_report': p2_report,
        'person3_report': p3_report,
        'person4_report': person4_report,
        'person5_report': person5_report,
        'person6_report': person6_report,
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

# ── Edit and Delete Views ───────────────────────────────────────────────────

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
            form.save()
            messages.success(request, 'Master entry updated.')
            export_to_excel()
            return redirect('dashboard')
    else:
        form = MasterEntryForm(instance=entry)
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
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    master_entries_qs = MasterEntry.objects.filter(Q(cutting_reports__isnull=True) | Q(id=report.master_entry_id)).distinct().order_by('-date')
    master_entries_json = json.dumps({str(e.id): e.job_card_number for e in master_entries_qs})
    colors_qs = report.color_details.order_by('id')
    colors_json = json.dumps([
        {
            'color_name': c.color_name,
            'size_s': c.size_s, 'size_m': c.size_m, 'size_l': c.size_l, 'size_xl': c.size_xl,
            'size_2xl': c.size_2xl, 'size_3xl': c.size_3xl, 'size_4xl': c.size_4xl,
            'total_weight_meter': float(c.total_weight_meter) if c.total_weight_meter is not None else None,
            'unit': c.unit
        } for c in colors_qs
    ])
    
    if request.method == 'POST':
        form = CuttingReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            
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
                    c_weight = request.POST.get(f'color_weight_{i}') or None
                    c_unit = request.POST.get(f'color_unit_{i}') or 'Weight'
                    CuttingReportColorDetail.objects.create(
                        cutting_report=report, color_name=c_name,
                        size_s=c_s, size_m=c_m, size_l=c_l, size_xl=c_xl,
                        size_2xl=c_2xl, size_3xl=c_3xl, size_4xl=c_4xl,
                        total_weight_meter=c_weight, unit=c_unit
                    )
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    CuttingReportPhoto.objects.create(cutting_report=report, photo=photo_file)
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
def edit_person4_report(request, pk):
    report = get_object_or_404(Person4Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(person4_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    if request.method == 'POST':
        form = Person4ReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            form.save()
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    Person4ReportPhoto.objects.create(person4_report=report, photo=photo_file)
            messages.success(request, 'Stitching Miya Ji updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = Person4ReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'person4_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_person4_report(request, pk):
    report = get_object_or_404(Person4Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Stitching Miya Ji deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_person5_report(request, pk):
    report = get_object_or_404(Person5Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(person5_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    if request.method == 'POST':
        form = Person5ReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            form.save()
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    Person5ReportPhoto.objects.create(person5_report=report, photo=photo_file)
            messages.success(request, 'Job Work updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = Person5ReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'person5_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_person5_report(request, pk):
    report = get_object_or_404(Person5Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Job Work deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_person6_report(request, pk):
    report = get_object_or_404(Person6Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(person6_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'date': cr.master_entry.date.strftime('%Y-%m-%d'),
            'lot_no': cr.job_card_no,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    if request.method == 'POST':
        form = Person6ReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            form.save()
            photos = request.FILES.getlist('photos')
            for photo_file in photos:
                if report.photos.count() < 5:
                    Person6ReportPhoto.objects.create(person6_report=report, photo=photo_file)
            messages.success(request, 'Finishing Report updated.')
            export_to_excel()
            return redirect('submission_list')
    else:
        form = Person6ReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'person6_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_person6_report(request, pk):
    report = get_object_or_404(Person6Report, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Finishing Report deleted.')
        export_to_excel()
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

import os
from django.conf import settings
from django.http import FileResponse

@login_required
def download_database(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can download the database backup.")
    
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        response = FileResponse(open(db_path, 'rb'), as_attachment=True, filename='fabrictrack_backup.sqlite3')
        return response
    else:
        messages.error(request, 'Database file not found.')
        return redirect('dashboard')
