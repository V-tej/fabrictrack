import os
from pathlib import Path
from django.conf import settings
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import MasterEntry, CuttingReport

def get_exports_dir():
    exports_dir = Path(settings.BASE_DIR) / 'exports'
    exports_dir.mkdir(exist_ok=True)
    return exports_dir


def export_to_excel(since_date=None):
    """Generate/update the main FabricTrack Excel file with all data."""
    exports_dir = get_exports_dir()
    filepath = exports_dir / 'FabricTrack_Data.xlsx'

    wb = openpyxl.Workbook()

    # ── Sheet 1: Master Entries ─────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = 'Master Entries'
    _style_sheet(ws1)

    headers1 = ['#', 'Date', 'Job Card Number', 'Created By', 'Created At']
    _write_header_row(ws1, headers1)

    me_qs = MasterEntry.objects.all()
    if since_date:
        me_qs = me_qs.filter(created_at__gt=since_date)
    for i, entry in enumerate(me_qs.order_by('-date'), start=1):
        ws1.append([
            i,
            entry.date.strftime('%d-%b-%Y'),
            entry.job_card_number,
            entry.created_by.username if entry.created_by else '—',
            entry.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws1)

    # ── Sheet 2: Consolidated Cutting Reports ───────────────────────────────
    ws2 = wb.create_sheet('Cutting Reports')
    _style_sheet(ws2)

    headers2 = [
        '#', 'Date', 'Report Type', 'Job Card Number', 'Cutting Master Name', 'Cutting Rate',
        'Fabric Type & Quality', 'Item Name', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', 'Grand Total',
        'Submitted By', 'Submitted At',
        'Jobworker', 'Job Work In / Out', 'Purpose', 'Job Work Date', 'Total Pcs short', 'Total Pcs', 'Any other Problem',
        'Line in Date', 'Line out Date', 'Total Pcs', 'Darji Rate', 'Folding Rate', 'Overlock Rate', 'Total Rate', 'Option 1',
        'Finishing Date', 'Finishing Total Pcs', 'Finishing Pcs Short', 'Finishing Pcs Packed', 'Finishing Green Tape', 'Finishing Red Tape', 'Finishing Blue Tape', 'Finishing Total Tape'
    ]
    _write_header_row(ws2, headers2)

    
    all_reports = CuttingReport.objects.select_related('master_entry', 'created_by').prefetch_related('photos', 'color_details').all()
    if since_date:
        all_reports = all_reports.filter(created_at__gt=since_date)
        
    all_reports = list(all_reports.order_by('-created_at'))

    for i, report in enumerate(all_reports, start=1):
        r_type_val = report.report_type
        
        if r_type_val == 'P2':
            r_type = 'CR Lakshay (P2)'
        elif r_type_val == 'P3':
            r_type = 'CR Rahul (P3)'
        else:
            r_type = 'Cutting Report (P1)'

        date_val = report.master_entry.date
        job_work = report.person5_reports.first()
        stitching = report.person4_reports.first()
        finishing = report.person6_reports.first()
            
        if job_work:
            jw_data = [
                job_work.jobworker,
                job_work.job_work_type,
                job_work.purpose,
                job_work.date.strftime('%d-%b-%Y') if job_work.date else '—',
                job_work.total_pcs_short if job_work.total_pcs_short is not None else '—',
                report.total_pcs if report.total_pcs is not None else '—',
                job_work.any_other_problem,
            ]
        else:
            jw_data = ['—', '—', '—', '—', '—', '—', '—']
            
        if stitching:
            stitch_data = [
                stitching.line_in_date.strftime('%d-%b-%Y') if stitching.line_in_date else '—',
                stitching.line_out_date.strftime('%d-%b-%Y') if stitching.line_out_date else '—',
                stitching.total_pcs if stitching.total_pcs is not None else '—',
                float(stitching.darji_rate) if stitching.darji_rate else '—',
                float(stitching.folding_rate) if stitching.folding_rate else '—',
                float(stitching.overlock_rate) if stitching.overlock_rate else '—',
                float(stitching.total_rate) if stitching.total_rate else '—',
                stitching.option_1 or '—',
            ]
        else:
            stitch_data = ['—'] * 8

        if finishing:
            finish_data = [
                finishing.date.strftime('%d-%b-%Y') if finishing.date else '—',
                finishing.total_pcs if finishing.total_pcs is not None else '—',
                finishing.total_pcs_short if finishing.total_pcs_short is not None else '—',
                finishing.total_pcs_packed if finishing.total_pcs_packed is not None else '—',
                finishing.green_tape if finishing.green_tape is not None else '—',
                finishing.red_tape if finishing.red_tape is not None else '—',
                finishing.blue_tape if finishing.blue_tape is not None else '—',
                finishing.total_tape if finishing.total_tape is not None else '—',
            ]
        else:
            finish_data = ['—'] * 8

        ws2.append([
            i,
            date_val.strftime('%d-%b-%Y'),
            r_type,
            report.job_card_no,
            report.cutting_master_name or '—',
            float(report.cutting_rate) if report.cutting_rate else '—',
            report.fabric_type_quality,
            report.item_name,
            report.size_s,
            report.size_m,
            report.size_l,
            report.size_xl,
            report.size_2xl,
            report.size_3xl,
            report.size_4xl,
            report.total_pcs,
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ] + jw_data + stitch_data + finish_data)

    _auto_width_and_style(ws2)

    # ── Sheet 5: Stitching Miya Ji ────────────────────────────────────────────
    ws5 = wb.create_sheet('Stitching Miya Ji')
    _style_sheet(ws5)

    headers5 = [
        '#', 'P1 Date', 'Job Card Number', 'Item Name', 'Line In Date', 'Line Out Date',
        'Total Pcs', 'Darji Rate', 'Folding Rate', 'Overlock Rate', 'Total Rate', 'Option 1',
        'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws5, headers5)

    from .models import Person4Report
    p4_qs = Person4Report.objects.select_related('cutting_report__master_entry', 'created_by').all()
    if since_date:
        p4_qs = p4_qs.filter(created_at__gt=since_date)
    for i, report in enumerate(p4_qs.order_by('-created_at'), start=1):
        ws5.append([
            i,
            report.cutting_report.master_entry.date.strftime('%d-%b-%Y'),
            report.job_card_no,
            report.item_name,
            report.line_in_date.strftime('%d-%b-%Y') if report.line_in_date else '—',
            report.line_out_date.strftime('%d-%b-%Y') if report.line_out_date else '—',
            report.total_pcs if report.total_pcs is not None else '—',
            float(report.darji_rate) if report.darji_rate else '—',
            float(report.folding_rate) if report.folding_rate else '—',
            float(report.overlock_rate) if report.overlock_rate else '—',
            float(report.total_rate) if report.total_rate else '—',
            report.option_1 or '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws5)

    # ── Sheet 6: Job Work ────────────────────────────────────────────
    ws6 = wb.create_sheet('Job Work')
    _style_sheet(ws6)

    headers6 = [
        '#', 'P1 Date', 'Job Card Number', 'Jobworker', 'Job Work In/Out', 'Purpose',
        'Date', 'Any other Problem', 'Total Pcs short', 'Total Pcs',
        'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws6, headers6)

    from .models import Person5Report
    p5_qs = Person5Report.objects.select_related('cutting_report__master_entry', 'created_by').all()
    if since_date:
        p5_qs = p5_qs.filter(created_at__gt=since_date)
    for i, report in enumerate(p5_qs.order_by('-created_at'), start=1):
        ws6.append([
            i,
            report.cutting_report.master_entry.date.strftime('%d-%b-%Y'),
            report.job_card_no,
            report.jobworker,
            report.job_work_type,
            report.purpose,
            report.date.strftime('%d-%b-%Y') if report.date else '—',
            report.any_other_problem,
            report.total_pcs_short if report.total_pcs_short is not None else '—',
            report.total_pcs if report.total_pcs is not None else '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws6)

    # ── Sheet 7: Finishing Report ────────────────────────────────────────────
    ws7 = wb.create_sheet('Finishing Report')
    _style_sheet(ws7)

    headers7 = [
        '#', 'P1 Date', 'Lot No', 'Date', 'Total Pcs', 'Total Pcs Short',
        'Total Pcs Packed', 'Green Tape', 'Red Tape', 'Blue Tape', 'Total Tape',
        'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws7, headers7)

    from .models import Person6Report
    p6_qs = Person6Report.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').all()
    if since_date:
        p6_qs = p6_qs.filter(created_at__gt=since_date)
    for i, report in enumerate(p6_qs.order_by('-created_at'), start=1):
        ws7.append([
            i,
            report.cutting_report.master_entry.date.strftime('%d-%b-%Y'),
            report.lot_no,
            report.date.strftime('%d-%b-%Y') if report.date else '—',
            report.total_pcs if report.total_pcs is not None else '—',
            report.total_pcs_short if report.total_pcs_short is not None else '—',
            report.total_pcs_packed if report.total_pcs_packed is not None else '—',
            report.green_tape if report.green_tape is not None else '—',
            report.red_tape if report.red_tape is not None else '—',
            report.blue_tape if report.blue_tape is not None else '—',
            report.total_tape if report.total_tape is not None else '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws7)

    wb.save(filepath)
    return filepath


# ── Helpers ─────────────────────────────────────────────────────────────────

HEADER_FILL = PatternFill(start_color='1E3A5F', end_color='1E3A5F', fill_type='solid')
HEADER_FONT = Font(bold=True, color='FFFFFF', name='Calibri', size=11)
HEADER_ALIGN = Alignment(horizontal='center', vertical='center', wrap_text=True)
DATA_ALIGN = Alignment(horizontal='center', vertical='center', wrap_text=True)
THIN_BORDER = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC'),
)


def _write_header_row(ws, headers):
    ws.append(headers)
    for col_num, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
    ws.row_dimensions[1].height = 30


def _style_sheet(ws):
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'A2'


def _auto_width_and_style(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for i, cell in enumerate(col):
            # Apply borders and alignment to ALL cells
            cell.border = THIN_BORDER
            # We don't overwrite header alignment which is set explicitly
            if i > 0:
                cell.alignment = DATA_ALIGN
            
            try:
                if cell.value:
                    # Calculate max length for auto-width, split by newline if present
                    lines = str(cell.value).split('\n')
                    for line in lines:
                        max_len = max(max_len, len(line))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 4, 50)
