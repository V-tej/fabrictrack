import os
from django.db.models import Q, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import json

from .models import MasterEntry, CuttingReport, CuttingReportPhoto, CuttingReportColorDetail, StitchingReport, StitchingReportPhoto, JobWorkReport, JobWorkReportPhoto, FinishingReport, FinishingReportPhoto, UserProfile, SystemSetting, JobCardRequirement, EmbroideryReport, PrintingReport, EmbroideryReportPhoto, PrintingReportPhoto, SingleneedleReport, SewingReport, SingleneedleReportPhoto, SewingReportPhoto, RateDefinition
from .forms import MasterEntryForm, CuttingReportForm, StitchingReportForm, JobWorkReportForm, FinishingReportForm, EmbroideryReportForm, PrintingReportForm, SingleneedleReportForm, SewingReportForm
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
        ).prefetch_related(
            Prefetch('photos', queryset=CuttingReportPhoto.objects.defer('photo_data'))
        )[:5]
        context['user_submissions_count'] = CuttingReport.objects.filter(created_by=request.user).count()

    elif person_type in ['P1', 'P2', 'P3']:
        context['recent_reports'] = CuttingReport.objects.filter(created_by=request.user).select_related(
            'master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=CuttingReportPhoto.objects.defer('photo_data'))
        )[:5]
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
        ).prefetch_related(
            Prefetch('photos', queryset=FinishingReportPhoto.objects.defer('photo_data'))
        )[:5]
        context['user_submissions_count'] = FinishingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P7':
        context['recent_reports'] = EmbroideryReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = EmbroideryReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P8':
        context['recent_reports'] = PrintingReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        )[:5]
        context['user_submissions_count'] = PrintingReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P9':
        context['recent_reports'] = SingleneedleReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=SingleneedleReportPhoto.objects.defer('photo_data'))
        )[:5]
        context['user_submissions_count'] = SingleneedleReport.objects.filter(created_by=request.user).count()

    elif person_type == 'P10':
        context['recent_reports'] = SewingReport.objects.filter(created_by=request.user).select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=SewingReportPhoto.objects.defer('photo_data'))
        )[:5]
        context['user_submissions_count'] = SewingReport.objects.filter(created_by=request.user).count()

    # Fetch pending tasks
    if person_type == 'ADMIN' or request.user.is_superuser:
        context['pending_tasks'] = JobCardRequirement.objects.filter(
            Q(requires_cutting=True, is_cutting_done=False) |
            Q(requires_jobwork=True, is_jobwork_done=False) |
            Q(requires_stitching=True, is_stitching_done=False) |
            Q(requires_finishing=True, is_finishing_done=False) |
            Q(requires_embroidery=True, is_embroidery_done=False) |
            Q(requires_printing=True, is_printing_done=False) |
            Q(requires_singleneedle=True, is_singleneedle_done=False) |
            Q(requires_sewing=True, is_sewing_done=False)
        )
    elif person_type in ['P1', 'P2', 'P3']:
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_cutting=True, is_cutting_done=False)
    elif person_type == 'P4':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_stitching=True, is_stitching_done=False)
    elif person_type == 'P5':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_jobwork=True, is_jobwork_done=False)
    elif person_type == 'P6':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_finishing=True, is_finishing_done=False)
    elif person_type == 'P7':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_embroidery=True, is_embroidery_done=False)
    elif person_type == 'P8':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_printing=True, is_printing_done=False)
    elif person_type == 'P9':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_singleneedle=True, is_singleneedle_done=False)
    elif person_type == 'P10':
        context['pending_tasks'] = JobCardRequirement.objects.filter(requires_sewing=True, is_sewing_done=False)
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
            upi_id = request.POST.get('upi_id', '').strip() or None
            master_id = request.POST.get('master_id')
            if name and department:
                from .models import MasterName
                if master_id:
                    master = MasterName.objects.filter(id=master_id).first()
                    if master:
                        master.name = name.strip()
                        master.department = department
                        master.upi_id = upi_id
                        master.save()
                        messages.success(request, f'Successfully updated master {name}!')
                else:
                    master, created = MasterName.objects.get_or_create(
                        name=name.strip(),
                        department=department,
                        defaults={'upi_id': upi_id}
                    )
                    if not created:
                        master.upi_id = upi_id
                        master.save()
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

        elif 'add_rate' in request.POST:
            name = request.POST.get('rate_name')
            description = request.POST.get('rate_description')
            total_rate = request.POST.get('rate_total')
            rate_id = request.POST.get('rate_id')
            if name and description and total_rate:
                from .models import RateDefinition
                if rate_id:
                    rd = RateDefinition.objects.filter(id=rate_id).first()
                    if rd:
                        rd.name = name.strip()
                        rd.description = description.strip()
                        rd.total_rate = total_rate
                        rd.save()
                        messages.success(request, f'Successfully updated rate {name}!')
                else:
                    rd, created = RateDefinition.objects.get_or_create(
                        name=name.strip(),
                        defaults={'description': description.strip(), 'total_rate': total_rate}
                    )
                    if not created:
                        rd.description = description.strip()
                        rd.total_rate = total_rate
                        rd.save()
                        messages.success(request, f'Successfully updated rate {name}!')
                    else:
                        messages.success(request, f'Successfully added rate {name}!')
            return redirect('manage_masters')

        elif 'delete_rate' in request.POST:
            rate_id = request.POST.get('rate_id')
            if rate_id:
                from .models import RateDefinition
                rate = RateDefinition.objects.filter(id=rate_id).first()
                if rate:
                    rate.delete()
                    messages.success(request, 'Rate definition deleted successfully.')
            return redirect('manage_masters')

    from .models import MasterName, RateDefinition
    masters = MasterName.objects.all().order_by('department', 'name')
    rate_definitions = RateDefinition.objects.all().order_by('name')
    context = {
        'masters': masters,
        'rate_definitions': rate_definitions,
        'person_type': person_type
    }
    return render(request, 'manage_masters.html', context)

# ── Manage Users (Admin Only) ────────────────────────────────────────────────

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')

    from django.contrib.auth.models import User
    users = User.objects.select_related('profile').order_by('username')
    context = {
        'users': users,
        'person_choices': UserProfile.PERSON_CHOICES if hasattr(UserProfile, 'PERSON_CHOICES') else [],
    }
    # Load PERSON_CHOICES from models
    from .models import PERSON_CHOICES
    context['person_choices'] = PERSON_CHOICES
    return render(request, 'manage_users.html', context)


@login_required
def add_user(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        from .models import PERSON_CHOICES
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        person_type = request.POST.get('person_type', 'P1')
        is_superuser = request.POST.get('is_superuser') == 'on'

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('manage_users')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('manage_users')

        user = User.objects.create_user(username=username, password=password)
        user.is_superuser = is_superuser
        user.is_staff = is_superuser
        user.save()

        UserProfile.objects.get_or_create(user=user, defaults={'person_type': person_type})
        messages.success(request, f'User "{username}" created successfully!')
    return redirect('manage_users')


@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    from django.contrib.auth.models import User
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'You cannot delete your own account.')
        else:
            uname = target_user.username
            target_user.delete()
            messages.success(request, f'User "{uname}" deleted successfully.')
    return redirect('manage_users')


@login_required
def reset_user_password(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    from django.contrib.auth.models import User
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        new_password = request.POST.get('new_password', '').strip()
        if not new_password:
            messages.error(request, 'Password cannot be empty.')
        else:
            target_user.set_password(new_password)
            target_user.save()
            messages.success(request, f'Password for "{target_user.username}" reset successfully.')
    return redirect('manage_users')


@login_required
def update_user_role(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission.')
        return redirect('dashboard')

    from django.contrib.auth.models import User
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        person_type = request.POST.get('person_type', 'P1')
        is_superuser = request.POST.get('is_superuser') == 'on'
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.person_type = person_type
        profile.save()
        target_user.is_superuser = is_superuser
        target_user.is_staff = is_superuser
        target_user.save()
        messages.success(request, f'Role for "{target_user.username}" updated successfully.')
    return redirect('manage_users')


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
                    'requires_embroidery': form.cleaned_data.get('requires_embroidery', True),
                    'requires_printing': form.cleaned_data.get('requires_printing', True),
                    'requires_singleneedle': form.cleaned_data.get('requires_singleneedle', True),
                    'requires_sewing': form.cleaned_data.get('requires_sewing', True),
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

    from .models import RateDefinition
    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
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
                'rate_definitions_json': rate_definitions_json,
                'is_admin': is_admin,
            })

        if len(photos) == 0:
            messages.error(request, 'Please upload at least one Job Card Photo.')
            return render(request, 'person1_form.html', {
                'form': form,
                'master_entries': master_entries_qs,
                'master_entries_json': master_entries_json,
                'rate_definitions_json': rate_definitions_json,
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

            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.cutting_rate = report.rate_definition.total_rate
            
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
        'rate_definitions_json': rate_definitions_json,
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

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
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
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                StitchingReportPhoto.objects.create(
                    stitching_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only Line In, done if Line Out also filled
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_done=True, is_stitching_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_in_progress=True, is_stitching_done=False
                )

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
        'rate_definitions_json': rate_definitions_json,
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
            photos = request.FILES.getlist('photos')
            if len(photos) == 0:
                messages.error(request, 'Please upload at least one Job Card Photo.')
                return render(request, 'jobwork_form.html', {
                    'form': form,
                    'cutting_reports': cutting_reports_qs,
                    'cutting_reports_json': cutting_reports_json,
                    'is_admin': is_admin,
                })
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return render(request, 'jobwork_form.html', {
                    'form': form,
                    'cutting_reports': cutting_reports_qs,
                    'cutting_reports_json': cutting_reports_json,
                    'is_admin': is_admin,
                })

            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                JobWorkReportPhoto.objects.create(
                    job_work_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only In date, done if Out date also filled
            job_card_no = report.cutting_report.job_card_no
            if report.jobwork_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_done=True, is_jobwork_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_in_progress=True, is_jobwork_done=False
                )

            messages.success(request, 'Job Work submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobWorkReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    return render(request, 'jobwork_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin,
    })


# ── P7: Embroidery Report ──────────────────────────────────────────────

@login_required
def embroidery_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        embroidery_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_embroidery=True).values('job_card_no')
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
        form = EmbroideryReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            photos = request.FILES.getlist('photos')
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return redirect('embroidery_report')

            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                EmbroideryReportPhoto.objects.create(
                    embroidery_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only In date, done if Out date also filled
            job_card_no = report.cutting_report.job_card_no
            if report.embroidery_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_done=True, is_embroidery_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_in_progress=True, is_embroidery_done=False
                )

            messages.success(request, 'Embroidery submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EmbroideryReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    return render(request, 'embroidery_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin,
    })


# ── P8: Printing Report ────────────────────────────────────────────────

@login_required
def printing_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        printing_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_printing=True).values('job_card_no')
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
        form = PrintingReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            photos = request.FILES.getlist('photos')
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return redirect('printing_report')

            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                PrintingReportPhoto.objects.create(
                    printing_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only In date, done if Out date also filled
            job_card_no = report.cutting_report.job_card_no
            if report.printing_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_done=True, is_printing_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_in_progress=True, is_printing_done=False
                )

            messages.success(request, 'Printing submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = PrintingReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    return render(request, 'printing_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin,
    })


# ── P9: Singleneedle Report ───────────────────────────────────────────

@login_required
def singleneedle_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        singleneedle_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_singleneedle=True).values('job_card_no')
    ).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    if request.method == 'POST':
        form = SingleneedleReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            photos = request.FILES.getlist('photos')
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return redirect('singleneedle_report')

            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                SingleneedleReportPhoto.objects.create(
                    singleneedle_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only Line In, done if Line Out also filled
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_done=True, is_singleneedle_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_in_progress=True, is_singleneedle_done=False
                )

            messages.success(request, 'Singleneedle submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SingleneedleReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'singleneedle_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin,
    })


# ── P10: Sewing Report ───────────────────────────────────────────────────

@login_required
def sewing_report_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )

    cutting_reports_qs = CuttingReport.objects.filter(
        sewing_reports__isnull=True,
        job_card_no__in=JobCardRequirement.objects.filter(requires_sewing=True).values('job_card_no')
    ).select_related('master_entry').order_by('-created_at')

    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    if request.method == 'POST':
        form = SewingReportForm(request.POST, request.FILES)
        form.fields['cutting_report'].queryset = cutting_reports_qs

        if form.is_valid():
            photos = request.FILES.getlist('photos')
            if len(photos) > 5:
                messages.error(request, 'You can upload a maximum of 5 photos.')
                return redirect('sewing_report')

            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos[:5]:
                SewingReportPhoto.objects.create(
                    sewing_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Mark pending task: in-progress if only Line In, done if Line Out also filled
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_done=True, is_sewing_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_in_progress=True, is_sewing_done=False
                )

            messages.success(request, 'Sewing submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SewingReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    return render(request, 'sewing_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
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

        rate_definitions = RateDefinition.objects.all()
        rate_definitions_json = json.dumps({
            str(r.id): {
                'name': r.name,
                'description': r.description,
                'total_rate': str(r.total_rate)
            } for r in rate_definitions
        })

        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for photo_file in photos:
                FinishingReportPhoto.objects.create(
                    finishing_report=report,
                    photo_data=photo_file.read(),
                    photo_name=photo_file.name,
                    photo_content_type=photo_file.content_type
                )



            # Mark pending task as done
            JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(is_finishing_done=True)

            messages.success(request, 'Finishing Report submitted successfully!')
            return redirect('submission_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = FinishingReportForm()
        form.fields['cutting_report'].queryset = cutting_reports_qs

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    return render(request, 'finishing_form.html', {
        'form': form,
        'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin,
    })


# ── Submissions List ──────────────────────────────────────────────────────────

@login_required
def submission_list_view(request):
    profile = getattr(request.user, 'profile', None)
    person_type = profile.person_type if profile else 'P1'
    filter_param = request.GET.get('filter')
    page_number = request.GET.get('page', '1')

    # Base querysets with optimized prefetching to avoid N+1 queries
    if person_type in ['P1', 'P2', 'P3'] and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.filter(
            created_by=request.user
        ).select_related('master_entry').prefetch_related(
            Prefetch('photos', queryset=CuttingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P4' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related(
            Prefetch('photos', queryset=StitchingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P5' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P6' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related(
            Prefetch('photos', queryset=FinishingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P7' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P8' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').order_by('-created_at')
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P9' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related(
            Prefetch('photos', queryset=SingleneedleReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p10_qs = SewingReport.objects.none()
    elif person_type == 'P10' and not request.user.is_superuser:
        reports_qs = CuttingReport.objects.none()
        p4_qs = StitchingReport.objects.none()
        p5_qs = JobWorkReport.objects.none()
        p6_qs = FinishingReport.objects.none()
        p7_qs = EmbroideryReport.objects.none()
        p8_qs = PrintingReport.objects.none()
        p9_qs = SingleneedleReport.objects.none()
        p10_qs = SewingReport.objects.filter(
            created_by=request.user
        ).select_related('cutting_report__master_entry').prefetch_related(
            Prefetch('photos', queryset=SewingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
    else:
        # Admin or Superuser sees all querysets
        reports_qs = CuttingReport.objects.select_related(
            'master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=CuttingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p4_qs = StitchingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=StitchingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p5_qs = JobWorkReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p6_qs = FinishingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=FinishingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p7_qs = EmbroideryReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p8_qs = PrintingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).order_by('-created_at')
        p9_qs = SingleneedleReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=SingleneedleReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')
        p10_qs = SewingReport.objects.select_related(
            'cutting_report__master_entry', 'created_by'
        ).prefetch_related(
            Prefetch('photos', queryset=SewingReportPhoto.objects.defer('photo_data'))
        ).order_by('-created_at')

    # Apply Department-Specific Master/Worker Filters if present
    master_name_cutting = request.GET.get('master_name_cutting')
    master_name_stitching = request.GET.get('master_name_stitching')
    master_name_job_work = request.GET.get('master_name_job_work')
    master_name_finishing = request.GET.get('master_name_finishing')
    master_name_embroidery = request.GET.get('master_name_embroidery')
    master_name_printing = request.GET.get('master_name_printing')
    master_name_singleneedle = request.GET.get('master_name_singleneedle')
    master_name_sewing = request.GET.get('master_name_sewing')

    if master_name_cutting:
        reports_qs = reports_qs.filter(Q(master_name=master_name_cutting) | Q(cutting_master_name=master_name_cutting))
    if master_name_stitching:
        p4_qs = p4_qs.filter(Q(master_name=master_name_stitching) | Q(stitching_master_name=master_name_stitching))
    if master_name_job_work:
        p5_qs = p5_qs.filter(Q(master_name=master_name_job_work) | Q(jobworker=master_name_job_work))
    if master_name_finishing:
        p6_qs = p6_qs.filter(Q(master_name=master_name_finishing) | Q(finishing_master_name=master_name_finishing))
    if master_name_embroidery:
        p7_qs = p7_qs.filter(Q(master_name=master_name_embroidery) | Q(embroidery_worker=master_name_embroidery))
    if master_name_printing:
        p8_qs = p8_qs.filter(Q(master_name=master_name_printing) | Q(printing_worker=master_name_printing))
    if master_name_singleneedle:
        p9_qs = p9_qs.filter(Q(master_name=master_name_singleneedle) | Q(singleneedle_master_name=master_name_singleneedle))
    if master_name_sewing:
        p10_qs = p10_qs.filter(Q(master_name=master_name_sewing) | Q(sewing_master_name=master_name_sewing))

    from core.models import MasterName
    master_names = MasterName.objects.all().order_by('department', 'name')

    reports = []
    p4_in_progress = []
    p4_completed = []
    p5_in_progress = []
    p5_completed = []
    p6_reports = []
    p7_in_progress = []
    p7_completed = []
    p8_in_progress = []
    p8_completed = []
    p9_in_progress = []
    p9_completed = []
    p10_in_progress = []
    p10_completed = []
    is_paginated = False
    page_obj = None

    ITEMS_PER_PAGE = 20
    ITEMS_OVERVIEW = 10

    if filter_param:
        is_paginated = True
        if filter_param in ['p1', 'p2', 'p3']:
            paginator = Paginator(reports_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            reports = page_obj
        elif filter_param == 'p4':
            paginator = Paginator(p4_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p4_in_progress = [r for r in page_obj if not r.line_out_date]
            p4_completed = [r for r in page_obj if r.line_out_date]
        elif filter_param == 'p5':
            paginator = Paginator(p5_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p5_in_progress = [r for r in page_obj if not r.jobwork_out]
            p5_completed = [r for r in page_obj if r.jobwork_out]
        elif filter_param == 'p6':
            paginator = Paginator(p6_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p6_reports = page_obj
        elif filter_param == 'p7':
            paginator = Paginator(p7_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p7_in_progress = [r for r in page_obj if not r.embroidery_out]
            p7_completed = [r for r in page_obj if r.embroidery_out]
        elif filter_param == 'p8':
            paginator = Paginator(p8_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p8_in_progress = [r for r in page_obj if not r.printing_out]
            p8_completed = [r for r in page_obj if r.printing_out]
        elif filter_param == 'p9':
            paginator = Paginator(p9_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p9_in_progress = [r for r in page_obj if not r.line_out_date]
            p9_completed = [r for r in page_obj if r.line_out_date]
        elif filter_param == 'p10':
            paginator = Paginator(p10_qs, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            p10_in_progress = [r for r in page_obj if not r.line_out_date]
            p10_completed = [r for r in page_obj if r.line_out_date]
    else:
        # Overview mode: show latest 10 items for each list to ensure fast rendering
        reports = reports_qs[:ITEMS_OVERVIEW]
        
        p4_in_progress = p4_qs.filter(line_out_date__isnull=True)[:ITEMS_OVERVIEW]
        p4_completed = p4_qs.filter(line_out_date__isnull=False)[:ITEMS_OVERVIEW]
        
        p5_in_progress = p5_qs.filter(jobwork_out__isnull=True)[:ITEMS_OVERVIEW]
        p5_completed = p5_qs.filter(jobwork_out__isnull=False)[:ITEMS_OVERVIEW]
        
        p6_reports = p6_qs[:ITEMS_OVERVIEW]
        
        p7_in_progress = p7_qs.filter(embroidery_out__isnull=True)[:ITEMS_OVERVIEW]
        p7_completed = p7_qs.filter(embroidery_out__isnull=False)[:ITEMS_OVERVIEW]
        
        p8_in_progress = p8_qs.filter(printing_out__isnull=True)[:ITEMS_OVERVIEW]
        p8_completed = p8_qs.filter(printing_out__isnull=False)[:ITEMS_OVERVIEW]
        
        p9_in_progress = p9_qs.filter(line_out_date__isnull=True)[:ITEMS_OVERVIEW]
        p9_completed = p9_qs.filter(line_out_date__isnull=False)[:ITEMS_OVERVIEW]

        p10_in_progress = p10_qs.filter(line_out_date__isnull=True)[:ITEMS_OVERVIEW]
        p10_completed = p10_qs.filter(line_out_date__isnull=False)[:ITEMS_OVERVIEW]

    return render(request, 'submission_list.html', {
        'reports': reports,
        'p4_in_progress': p4_in_progress,
        'p4_completed': p4_completed,
        'p5_in_progress': p5_in_progress,
        'p5_completed': p5_completed,
        'p6_reports': p6_reports,
        'p7_in_progress': p7_in_progress,
        'p7_completed': p7_completed,
        'p8_in_progress': p8_in_progress,
        'p8_completed': p8_completed,
        'p9_in_progress': p9_in_progress,
        'p9_completed': p9_completed,
        'p10_in_progress': p10_in_progress,
        'p10_completed': p10_completed,
        'person_type': person_type,
        'filter_param': filter_param,
        'is_paginated': is_paginated,
        'page_obj': page_obj,
        'show_p1': not filter_param or filter_param in ['p1', 'p2', 'p3'],
        'show_p2': not filter_param or filter_param in ['p1', 'p2', 'p3'],
        'show_p3': not filter_param or filter_param in ['p1', 'p2', 'p3'],
        'show_p4': not filter_param or filter_param == 'p4',
        'show_p5': not filter_param or filter_param == 'p5',
        'show_p6': not filter_param or filter_param == 'p6',
        'show_p7': not filter_param or filter_param == 'p7',
        'show_p8': not filter_param or filter_param == 'p8',
        'show_p9': not filter_param or filter_param == 'p9',
        'show_p10': not filter_param or filter_param == 'p10',
        'master_names': master_names,
        'master_name_cutting': master_name_cutting,
        'master_name_stitching': master_name_stitching,
        'master_name_job_work': master_name_job_work,
        'master_name_finishing': master_name_finishing,
        'master_name_embroidery': master_name_embroidery,
        'master_name_printing': master_name_printing,
        'master_name_singleneedle': master_name_singleneedle,
        'master_name_sewing': master_name_sewing,
    })


from django.core.exceptions import PermissionDenied

@login_required
def users_reports_view(request):
    if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')):
        raise PermissionDenied

    query = request.GET.get('q', '').strip()

    p4_qs = StitchingReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related(
        Prefetch('photos', queryset=StitchingReportPhoto.objects.defer('photo_data'))
    ).order_by('-created_at')
    p5_qs = JobWorkReport.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p6_qs = FinishingReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related(
        Prefetch('photos', queryset=FinishingReportPhoto.objects.defer('photo_data'))
    ).order_by('-created_at')
    p7_qs = EmbroideryReport.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p8_qs = PrintingReport.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at')
    p9_qs = SingleneedleReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related(
        Prefetch('photos', queryset=SingleneedleReportPhoto.objects.defer('photo_data'))
    ).order_by('-created_at')
    p10_qs = SewingReport.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related(
        Prefetch('photos', queryset=SewingReportPhoto.objects.defer('photo_data'))
    ).order_by('-created_at')

    if query:
        p4_qs = p4_qs.filter(job_card_no__icontains=query)
        p5_qs = p5_qs.filter(job_card_no__icontains=query)
        p6_qs = p6_qs.filter(cutting_report__job_card_no__icontains=query)
        p7_qs = p7_qs.filter(job_card_no__icontains=query)
        p8_qs = p8_qs.filter(job_card_no__icontains=query)
        p9_qs = p9_qs.filter(job_card_no__icontains=query)
        p10_qs = p10_qs.filter(job_card_no__icontains=query)
        limit = 50
    else:
        limit = 5

    # Split P4 reports
    p4_in_progress = p4_qs.filter(line_out_date__isnull=True)[:limit]
    p4_completed = p4_qs.filter(line_out_date__isnull=False)[:limit]
    # Split P9 reports
    p9_in_progress = p9_qs.filter(line_out_date__isnull=True)[:limit]
    p9_completed = p9_qs.filter(line_out_date__isnull=False)[:limit]
    # Split P10 reports
    p10_in_progress = p10_qs.filter(line_out_date__isnull=True)[:limit]
    p10_completed = p10_qs.filter(line_out_date__isnull=False)[:limit]

    context = {
        'search_query': query,
        'person1_reports_count': CuttingReport.objects.filter(report_type='P1').count(),
        'person2_reports_count': CuttingReport.objects.filter(report_type='P2').count(),
        'person3_reports_count': CuttingReport.objects.filter(report_type='P3').count(),
        'stitching_reports_count': StitchingReport.objects.count(),
        'jobwork_reports_count': JobWorkReport.objects.count(),
        'finishing_reports_count': FinishingReport.objects.count(),
        'embroidery_reports_count': EmbroideryReport.objects.count(),
        'printing_reports_count': PrintingReport.objects.count(),
        'singleneedle_reports_count': SingleneedleReport.objects.count(),
        'sewing_reports_count': SewingReport.objects.count(),
        'recent_p4_in_progress': p4_in_progress,
        'recent_p4_completed': p4_completed,
        'recent_jobwork_reports': p5_qs[:limit],
        'recent_finishing_reports': p6_qs[:limit],
        'recent_embroidery_reports': p7_qs[:limit],
        'recent_printing_reports': p8_qs[:limit],
        'recent_p9_in_progress': p9_in_progress,
        'recent_p9_completed': p9_completed,
        'recent_p10_in_progress': p10_in_progress,
        'recent_p10_completed': p10_completed,
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

    # Link subsequent reports (P4, P5, P6, P7, P8, P9, P10) to whatever cutting report was submitted
    base_cutting = all_cutting.first()
    stitching_report = base_cutting.stitching_reports.first() if (base_cutting and (show_all or report_type == 'P4')) else None
    jobwork_report = base_cutting.jobwork_reports.first() if (base_cutting and (show_all or report_type == 'P5')) else None
    finishing_report = base_cutting.finishing_reports.first() if (base_cutting and (show_all or report_type == 'P6')) else None
    embroidery_report = base_cutting.embroidery_reports.first() if (base_cutting and (show_all or report_type == 'P7')) else None
    printing_report = base_cutting.printing_reports.first() if (base_cutting and (show_all or report_type == 'P8')) else None
    singleneedle_report = base_cutting.singleneedle_reports.first() if (base_cutting and (show_all or report_type == 'P9')) else None
    sewing_report = base_cutting.sewing_reports.first() if (base_cutting and (show_all or report_type == 'P10')) else None

    return render(request, 'job_card_detail.html', {
        'master_entry': master_entry,
        'cutting_report': p1_report,
        'person2_report': p2_report,
        'person3_report': p3_report,
        'stitching_report': stitching_report,
        'jobwork_report': jobwork_report,
        'finishing_report': finishing_report,
        'embroidery_report': embroidery_report,
        'printing_report': printing_report,
        'singleneedle_report': singleneedle_report,
        'sewing_report': sewing_report,
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
                embroidery_req = is_yes(get_val('embroidery'))
                printing_req = is_yes(get_val('printing'))
                singleneedle_req = is_yes(get_val('singleneedle'))
                sewing_req = is_yes(get_val('sewing'))
                
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
                        'requires_embroidery': embroidery_req,
                        'requires_printing': printing_req,
                        'requires_singleneedle': singleneedle_req,
                        'requires_sewing': sewing_req,
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
                    'requires_embroidery': form.cleaned_data.get('requires_embroidery', True),
                    'requires_printing': form.cleaned_data.get('requires_printing', True),
                    'requires_singleneedle': form.cleaned_data.get('requires_singleneedle', True),
                    'requires_sewing': form.cleaned_data.get('requires_sewing', True),
                }
            )
            
            messages.success(request, 'Master entry updated.')
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
                'requires_embroidery': 'True' if req.requires_embroidery else 'False',
                'requires_printing': 'True' if req.requires_printing else 'False',
                'requires_singleneedle': 'True' if req.requires_singleneedle else 'False',
                'requires_sewing': 'True' if req.requires_sewing else 'False',
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
    
    from .models import RateDefinition
    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })
    
    if request.method == 'POST':
        form = CuttingReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.cutting_rate = report.rate_definition.total_rate
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
            return redirect('submission_list')
    else:
        form = CuttingReportForm(instance=report)
    return render(request, 'person1_form.html', {
        'form': form, 'master_entries': master_entries_qs,
        'master_entries_json': master_entries_json, 'is_admin': is_admin, 'is_edit': True, 'report': report,
        'colors_json': colors_json,
        'rate_definitions_json': rate_definitions_json
    })

@login_required
def delete_cutting_report(request, pk):
    report = get_object_or_404(CuttingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(is_cutting_done=False)
        report.delete()
        messages.success(request, 'Cutting Report deleted.')
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

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
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
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                StitchingReportPhoto.objects.create(
                    stitching_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on Line In/Out dates
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_done=True, is_stitching_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_in_progress=True, is_stitching_done=False
                )

            messages.success(request, 'Stitching updated.')
            return redirect('submission_list')
    else:
        form = StitchingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'stitching_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_stitching_report(request, pk):
    report = get_object_or_404(StitchingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
            is_stitching_done=False, is_stitching_in_progress=False
        )
        report.delete()
        messages.success(request, 'Stitching deleted.')
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_singleneedle_report(request, pk):
    report = get_object_or_404(SingleneedleReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(singleneedle_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(SingleneedleReportPhoto, pk=delete_photo_id, singleneedle_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_singleneedle_report', pk=report.id)

    if request.method == 'POST':
        form = SingleneedleReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return redirect('edit_singleneedle_report', pk=report.id)

        if form.is_valid():
            report = form.save(commit=False)
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                SingleneedleReportPhoto.objects.create(
                    singleneedle_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on Line In/Out dates
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_done=True, is_singleneedle_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_in_progress=True, is_singleneedle_done=False
                )

            messages.success(request, 'Singleneedle updated.')
            return redirect('submission_list')
    else:
        form = SingleneedleReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'singleneedle_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_singleneedle_report(request, pk):
    report = get_object_or_404(SingleneedleReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
            is_singleneedle_done=False, is_singleneedle_in_progress=False
        )
        report.delete()
        messages.success(request, 'Singleneedle deleted.')
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})


@login_required
def edit_sewing_report(request, pk):
    report = get_object_or_404(SewingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(sewing_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(SewingReportPhoto, pk=delete_photo_id, sewing_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_sewing_report', pk=report.id)

    if request.method == 'POST':
        form = SewingReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return redirect('edit_sewing_report', pk=report.id)

        if form.is_valid():
            report = form.save(commit=False)
            if report.rate_definition:
                report.rate_name = report.rate_definition.name
                report.rate_description = report.rate_definition.description
                report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                SewingReportPhoto.objects.create(
                    sewing_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on Line In/Out dates
            if report.line_out_date:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_done=True, is_sewing_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_in_progress=True, is_sewing_done=False
                )

            messages.success(request, 'Sewing updated.')
            return redirect('submission_list')
    else:
        form = SewingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'sewing_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_sewing_report(request, pk):
    report = get_object_or_404(SewingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
            is_sewing_done=False, is_sewing_in_progress=False
        )
        report.delete()
        messages.success(request, 'Sewing deleted.')
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
    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        if report.photos.count() <= 1:
            messages.error(request, 'Cannot delete. At least one Job Card Photo is required.')
        else:
            photo_to_delete = get_object_or_404(JobWorkReportPhoto, pk=delete_photo_id, job_work_report=report)
            photo_to_delete.delete()
            messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_jobwork_report', pk=report.id)

    if request.method == 'POST':
        form = JobWorkReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() == 0:
            messages.error(request, 'At least one Job Card Photo is required.')
            return render(request, 'jobwork_form.html', {
                'form': form, 'cutting_reports': cutting_reports_qs,
                'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
            })

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return render(request, 'jobwork_form.html', {
                'form': form, 'cutting_reports': cutting_reports_qs,
                'cutting_reports_json': cutting_reports_json, 'is_admin': is_admin, 'is_edit': True, 'report': report
            })

        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                JobWorkReportPhoto.objects.create(
                    job_work_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on In/Out dates
            job_card_no = report.cutting_report.job_card_no
            if report.jobwork_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_done=True, is_jobwork_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_in_progress=True, is_jobwork_done=False
                )

            messages.success(request, 'Job Work updated.')
            return redirect('submission_list')
    else:
        form = JobWorkReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'jobwork_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_jobwork_report(request, pk):
    report = get_object_or_404(JobWorkReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(
            is_jobwork_done=False, is_jobwork_in_progress=False
        )
        report.delete()
        messages.success(request, 'Job Work deleted.')
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_embroidery_report(request, pk):
    report = get_object_or_404(EmbroideryReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(embroidery_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(EmbroideryReportPhoto, pk=delete_photo_id, embroidery_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_embroidery_report', pk=report.id)

    if request.method == 'POST':
        form = EmbroideryReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return redirect('edit_embroidery_report', pk=report.id)

        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                EmbroideryReportPhoto.objects.create(
                    embroidery_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on In/Out dates
            job_card_no = report.cutting_report.job_card_no
            if report.embroidery_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_done=True, is_embroidery_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_in_progress=True, is_embroidery_done=False
                )

            messages.success(request, 'Embroidery updated.')
            return redirect('submission_list')
    else:
        form = EmbroideryReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'embroidery_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_embroidery_report(request, pk):
    report = get_object_or_404(EmbroideryReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(
            is_embroidery_done=False, is_embroidery_in_progress=False
        )
        report.delete()
        messages.success(request, 'Embroidery deleted.')
        return redirect('submission_list')
    return render(request, 'confirm_delete.html', {'object': report, 'cancel_url': 'submission_list'})

@login_required
def edit_printing_report(request, pk):
    report = get_object_or_404(PrintingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    is_admin = request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN')
    cutting_reports_qs = CuttingReport.objects.filter(Q(printing_reports__isnull=True) | Q(id=report.cutting_report_id)).distinct().select_related('master_entry').order_by('-created_at')
    cutting_reports_json = json.dumps({
        str(cr.id): {
            'master_entry_id': cr.master_entry_id,
            'job_card_no': cr.job_card_no,
            'item_name': cr.item_name,
            'total_pcs': cr.total_pcs
        } for cr in cutting_reports_qs
    })
    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })
    delete_photo_id = request.GET.get('delete_photo')
    if delete_photo_id:
        photo_to_delete = get_object_or_404(PrintingReportPhoto, pk=delete_photo_id, printing_report=report)
        photo_to_delete.delete()
        messages.success(request, 'Photo deleted successfully.')
        return redirect('edit_printing_report', pk=report.id)

    if request.method == 'POST':
        form = PrintingReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        photos = request.FILES.getlist('photos')

        if len(photos) + report.photos.count() > 5:
            messages.error(request, 'You can upload a maximum of 5 photos total.')
            return redirect('edit_printing_report', pk=report.id)

        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
            report.save()

            for p in photos:
                PrintingReportPhoto.objects.create(
                    printing_report=report,
                    photo_data=p.read(),
                    photo_name=p.name,
                    photo_content_type=p.content_type
                )

            # Update pending task status based on In/Out dates
            job_card_no = report.cutting_report.job_card_no
            if report.printing_out:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_done=True, is_printing_in_progress=False
                )
            else:
                JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_in_progress=True, is_printing_done=False
                )

            messages.success(request, 'Printing updated.')
            return redirect('submission_list')
    else:
        form = PrintingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'printing_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_printing_report(request, pk):
    report = get_object_or_404(PrintingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(
            is_printing_done=False, is_printing_in_progress=False
        )
        report.delete()
        messages.success(request, 'Printing deleted.')
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

    rate_definitions = RateDefinition.objects.all()
    rate_definitions_json = json.dumps({
        str(r.id): {
            'name': r.name,
            'description': r.description,
            'total_rate': str(r.total_rate)
        } for r in rate_definitions
    })

    if request.method == 'POST':
        form = FinishingReportForm(request.POST, request.FILES, instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
        if form.is_valid():
            report = form.save(commit=False)
            report.created_at = timezone.now()
            if report.rate_definition:
                if not report.total_rate:
                    report.total_rate = report.rate_definition.total_rate
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
            return redirect('submission_list')
    else:
        form = FinishingReportForm(instance=report)
        form.fields['cutting_report'].queryset = cutting_reports_qs
    return render(request, 'finishing_form.html', {
        'form': form, 'cutting_reports': cutting_reports_qs,
        'cutting_reports_json': cutting_reports_json,
        'rate_definitions_json': rate_definitions_json,
        'is_admin': is_admin, 'is_edit': True, 'report': report
    })

@login_required
def delete_finishing_report(request, pk):
    report = get_object_or_404(FinishingReport, pk=pk)
    if not check_edit_permission(request, report): raise PermissionDenied
    if request.method == 'POST':
        JobCardRequirement.objects.filter(job_card_no=report.cutting_report.job_card_no).update(is_finishing_done=False)
        report.delete()
        messages.success(request, 'Finishing Report deleted.')
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
    elif model_name == 'jobwork':
        photo = get_object_or_404(JobWorkReportPhoto, pk=photo_id)
    elif model_name == 'embroidery':
        photo = get_object_or_404(EmbroideryReportPhoto, pk=photo_id)
    elif model_name == 'printing':
        photo = get_object_or_404(PrintingReportPhoto, pk=photo_id)
    elif model_name == 'singleneedle':
        photo = get_object_or_404(SingleneedleReportPhoto, pk=photo_id)
    elif model_name == 'sewing':
        photo = get_object_or_404(SewingReportPhoto, pk=photo_id)
    else:
        raise Http404("Invalid photo model")
    
    response = HttpResponse(photo.photo_data, content_type=photo.photo_content_type)
    response['Content-Disposition'] = f'inline; filename="{photo.photo_name}"'
    response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
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
        

            
        messages.success(request, 'Database successfully reset! All master entries, reports, and photos have been permanently deleted.')
        return redirect('dashboard')
        
    return render(request, 'confirm_reset.html')


from django.db.models import Sum
from .forms import MasterPaymentForm
from .models import MasterPayment, MasterName
from .utils import calculate_master_earnings

@login_required
def master_ledger_list_view(request):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )
    if not is_admin:
        raise PermissionDenied("Only administrators can view the ledger.")

    masters = MasterName.objects.all().order_by('department', 'name')
    ledger_data = []

    for master in masters:
        total_earnings = calculate_master_earnings(master.name)
        total_paid = float(master.payments.aggregate(total=Sum('amount'))['total'] or 0.0)
        balance = total_earnings - total_paid
        ledger_data.append({
            'master': master,
            'total_earnings': total_earnings,
            'total_paid': total_paid,
            'balance': balance,
        })

    return render(request, 'master_ledger_list.html', {
        'ledger_data': ledger_data,
        'is_admin': is_admin,
    })


@login_required
def master_ledger_detail_view(request, pk):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )
    if not is_admin:
        raise PermissionDenied("Only administrators can view the ledger.")

    master = get_object_or_404(MasterName, pk=pk)

    from .models import (
        CuttingReport, StitchingReport, JobWorkReport, EmbroideryReport,
        PrintingReport, SingleneedleReport, SewingReport, FinishingReport
    )

    events = []

    # 1. Cutting Report
    for r in CuttingReport.objects.filter(master_name=master.name).select_related('master_entry'):
        rate = float(r.cutting_rate or 0.0)
        pcs = int(r.total_pcs or 0)
        amount = rate * pcs
        if amount > 0:
            events.append({
                'date': r.master_entry.date,
                'created_at': r.created_at,
                'type': 'earning',
                'description': f"Cutting: {pcs} Pcs @ ₹{rate:.2f} (Job Card: {r.job_card_no})",
                'amount': amount
            })

    # Helper for standard reports
    def add_reports(qs, label, date_field, rate_field='total_rate', jc_field='job_card_no'):
        for r in qs:
            rate = float(getattr(r, rate_field) or 0.0)
            pcs = int(r.total_pcs or 0)
            amount = rate * pcs
            if amount > 0:
                d = getattr(r, date_field) or r.created_at.date()
                jc = getattr(r, jc_field, '')
                events.append({
                    'date': d,
                    'created_at': r.created_at,
                    'type': 'earning',
                    'description': f"{label}: {pcs} Pcs @ ₹{rate:.2f} (Job Card/Lot: {jc})",
                    'amount': amount
                })

    add_reports(StitchingReport.objects.filter(master_name=master.name), "Stitching", "line_in_date")
    add_reports(JobWorkReport.objects.filter(master_name=master.name), "Job Work", "jobwork_in")
    add_reports(EmbroideryReport.objects.filter(master_name=master.name), "Embroidery", "embroidery_in")
    add_reports(PrintingReport.objects.filter(master_name=master.name), "Printing", "printing_in")
    add_reports(SingleneedleReport.objects.filter(master_name=master.name), "Singleneedle", "line_in_date")
    add_reports(SewingReport.objects.filter(master_name=master.name), "Sewing", "line_in_date")
    add_reports(FinishingReport.objects.filter(master_name=master.name), "Finishing", "date", jc_field='lot_no')

    # Payments
    for p in MasterPayment.objects.filter(master=master):
        events.append({
            'date': p.date,
            'created_at': p.created_at,
            'type': 'payment',
            'description': f"Paid via {p.get_payment_mode_display()}" + (f" (Ref: {p.reference_no})" if p.reference_no else "") + (f" - {p.remarks}" if p.remarks else ""),
            'amount': float(p.amount),
            'payment_id': p.id
        })

    # Sort chronologically
    events = sorted(events, key=lambda x: (x['date'], x['created_at']))

    running_balance = 0.0
    for e in events:
        if e['type'] == 'earning':
            running_balance += e['amount']
        else:
            running_balance -= e['amount']
        e['balance'] = running_balance

    total_earnings = calculate_master_earnings(master.name)
    total_paid = float(master.payments.aggregate(total=Sum('amount'))['total'] or 0.0)
    current_balance = total_earnings - total_paid

    return render(request, 'master_ledger_detail.html', {
        'master': master,
        'events': reversed(events),  # Show newest first in table
        'total_earnings': total_earnings,
        'total_paid': total_paid,
        'current_balance': current_balance,
        'is_admin': is_admin,
    })


@login_required
def record_payment_view(request, pk=None):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )
    if not is_admin:
        raise PermissionDenied("Only administrators can record payments.")

    initial_data = {}
    master = None
    if pk:
        master = get_object_or_404(MasterName, pk=pk)
        initial_data['master'] = master
        initial_data['date'] = timezone.now().date()
        total_earnings = calculate_master_earnings(master.name)
        total_paid = float(master.payments.aggregate(total=Sum('amount'))['total'] or 0.0)
        initial_data['amount'] = max(0.0, total_earnings - total_paid)

    if request.method == 'POST':
        form = MasterPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            payment.save()
            messages.success(request, f"Successfully recorded payment of ₹{payment.amount} to {payment.master.name}!")
            return redirect('master_ledger_detail', pk=payment.master.pk)
    else:
        form = MasterPaymentForm(initial=initial_data)

    masters_json = json.dumps({
        str(m.id): {
            'name': m.name,
            'upi_id': m.upi_id or '',
            'outstanding': max(0.0, calculate_master_earnings(m.name) - float(m.payments.aggregate(total=Sum('amount'))['total'] or 0.0))
        } for m in MasterName.objects.all()
    })

    return render(request, 'record_payment.html', {
        'form': form,
        'master': master,
        'masters_json': masters_json,
        'is_admin': is_admin,
    })


@login_required
def delete_payment_view(request, pk):
    is_admin = request.user.is_superuser or (
        hasattr(request.user, 'profile') and request.user.profile.person_type == 'ADMIN'
    )
    if not is_admin:
        raise PermissionDenied("Only administrators can delete payments.")

    payment = get_object_or_404(MasterPayment, pk=pk)
    master_pk = payment.master.pk
    if request.method == 'POST':
        payment.delete()
        messages.success(request, "Payment deleted successfully.")
        return redirect('master_ledger_detail', pk=master_pk)
    return render(request, 'confirm_delete.html', {'object': payment, 'cancel_url': 'master_ledger_detail'})

