"""
Management command: backfill_in_progress

Scans all existing submitted reports and updates the JobCardRequirement
in_progress / done flags based on whether the In date and Out date are filled.

Run once after deploying the in-progress feature:
    python manage.py backfill_in_progress
"""
from django.core.management.base import BaseCommand
from core.models import (
    JobCardRequirement,
    JobWorkReport, EmbroideryReport, PrintingReport,
    StitchingReport, SingleneedleReport, SewingReport,
)


class Command(BaseCommand):
    help = 'Backfill is_*_in_progress and is_*_done flags for all existing reports.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting backfill...'))
        total = 0

        # ── JobWork (jobwork_in / jobwork_out) ──────────────────────────────
        for report in JobWorkReport.objects.select_related('cutting_report').all():
            job_card_no = report.cutting_report.job_card_no
            if report.jobwork_out:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_done=True, is_jobwork_in_progress=False
                )
            elif report.jobwork_in:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_jobwork_in_progress=True, is_jobwork_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  JobWork  {job_card_no}: {"Done" if report.jobwork_out else "In Progress"}')

        # ── Embroidery (embroidery_in / embroidery_out) ─────────────────────
        for report in EmbroideryReport.objects.select_related('cutting_report').all():
            job_card_no = report.cutting_report.job_card_no
            if report.embroidery_out:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_done=True, is_embroidery_in_progress=False
                )
            elif report.embroidery_in:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_embroidery_in_progress=True, is_embroidery_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  Embroidery  {job_card_no}: {"Done" if report.embroidery_out else "In Progress"}')

        # ── Printing (printing_in / printing_out) ───────────────────────────
        for report in PrintingReport.objects.select_related('cutting_report').all():
            job_card_no = report.cutting_report.job_card_no
            if report.printing_out:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_done=True, is_printing_in_progress=False
                )
            elif report.printing_in:
                updated = JobCardRequirement.objects.filter(job_card_no=job_card_no).update(
                    is_printing_in_progress=True, is_printing_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  Printing  {job_card_no}: {"Done" if report.printing_out else "In Progress"}')

        # ── Stitching (line_in_date / line_out_date) ────────────────────────
        for report in StitchingReport.objects.all():
            if report.line_out_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_done=True, is_stitching_in_progress=False
                )
            elif report.line_in_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_stitching_in_progress=True, is_stitching_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  Stitching  {report.job_card_no}: {"Done" if report.line_out_date else "In Progress"}')

        # ── Singleneedle (line_in_date / line_out_date) ─────────────────────
        for report in SingleneedleReport.objects.all():
            if report.line_out_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_done=True, is_singleneedle_in_progress=False
                )
            elif report.line_in_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_singleneedle_in_progress=True, is_singleneedle_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  Singleneedle  {report.job_card_no}: {"Done" if report.line_out_date else "In Progress"}')

        # ── Sewing (line_in_date / line_out_date) ───────────────────────────
        for report in SewingReport.objects.all():
            if report.line_out_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_done=True, is_sewing_in_progress=False
                )
            elif report.line_in_date:
                updated = JobCardRequirement.objects.filter(job_card_no=report.job_card_no).update(
                    is_sewing_in_progress=True, is_sewing_done=False
                )
            else:
                updated = 0
            if updated:
                total += updated
                self.stdout.write(f'  Sewing  {report.job_card_no}: {"Done" if report.line_out_date else "In Progress"}')

        self.stdout.write(self.style.SUCCESS(
            f'\nBackfill complete. Updated {total} JobCardRequirement record(s).'
        ))
