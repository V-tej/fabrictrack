import os
from pathlib import Path
from django.conf import settings
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from .models import MasterEntry, CuttingReport, Person2Report


def get_exports_dir():
    exports_dir = Path(settings.BASE_DIR) / 'exports'
    exports_dir.mkdir(exist_ok=True)
    return exports_dir


def export_to_excel():
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

    for i, entry in enumerate(MasterEntry.objects.all().order_by('-date'), start=1):
        ws1.append([
            i,
            entry.date.strftime('%d-%b-%Y'),
            entry.job_card_number,
            entry.created_by.username if entry.created_by else '—',
            entry.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws1)

    # ── Sheet 2: Cutting Reports ────────────────────────────────────────────
    ws2 = wb.create_sheet('Cutting Reports')
    _style_sheet(ws2)

    headers2 = [
        '#', 'Date', 'Job Card Number', 'Cutting Master Name', 'Cutting Rate',
        'Fabric Type & Quality', 'Item Name', 'Job Card No.',
        'Total Pcs', 'Total Colours', 'Total Weight/Meter',
        'Avg per Pcs', 'Photos', 'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws2, headers2)

    for i, report in enumerate(CuttingReport.objects.select_related('master_entry', 'created_by').prefetch_related('photos').order_by('-created_at'), start=1):
        photo_names = ' | '.join(
            os.path.basename(p.photo.name) for p in report.photos.all()
        )
        ws2.append([
            i,
            report.master_entry.date.strftime('%d-%b-%Y'),
            report.master_entry.job_card_number,
            report.cutting_master_name or '—',
            float(report.cutting_rate) if report.cutting_rate else '—',
            report.fabric_type_quality,
            report.item_name,
            report.job_card_no,
            report.total_pcs,
            report.total_colours,
            float(report.total_weight_meter),
            float(report.avg_per_pcs),
            photo_names or '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws2)

    # ── Sheet 3: CR Lakshay ────────────────────────────────────────────
    ws3 = wb.create_sheet('CR Lakshay')
    _style_sheet(ws3)

    headers3 = [
        '#', 'Date', 'Job Card Number', 'P1 Cutting Master', 'CR Lakshay Master Name', 'CR Lakshay Rate',
        'Fabric Type & Quality', 'Item Name', 'Job Card No.',
        'Total Pcs', 'Total Colours', 'Total Weight/Meter',
        'Avg per Pcs', 'Photos', 'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws3, headers3)

    for i, report in enumerate(Person2Report.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at'), start=1):
        photo_names = ' | '.join(
            os.path.basename(p.photo.name) for p in report.photos.all()
        )
        ws3.append([
            i,
            report.cutting_report.master_entry.date.strftime('%d-%b-%Y'),
            report.cutting_report.master_entry.job_card_number,
            report.cutting_report.cutting_master_name or '—',
            report.cutting_master_name or '—',
            float(report.cutting_rate) if report.cutting_rate else '—',
            report.fabric_type_quality,
            report.item_name,
            report.job_card_no,
            report.total_pcs,
            report.total_colours,
            float(report.total_weight_meter),
            float(report.avg_per_pcs),
            photo_names or '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws3)

    # ── Sheet 4: CR Rahul ────────────────────────────────────────────
    ws4 = wb.create_sheet('CR Rahul')
    _style_sheet(ws4)

    headers4 = [
        '#', 'Date', 'Job Card Number', 'P1 Cutting Master', 'CR Rahul Master Name', 'CR Rahul Rate',
        'Fabric Type & Quality', 'Item Name', 'Job Card No.',
        'Total Pcs', 'Total Colours', 'Total Weight/Meter',
        'Avg per Pcs', 'Photos', 'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws4, headers4)

    from .models import Person3Report
    for i, report in enumerate(Person3Report.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at'), start=1):
        photo_names = ' | '.join(
            os.path.basename(p.photo.name) for p in report.photos.all()
        )
        ws4.append([
            i,
            report.cutting_report.master_entry.date.strftime('%d-%b-%Y'),
            report.cutting_report.master_entry.job_card_number,
            report.cutting_report.cutting_master_name or '—',
            report.cutting_master_name or '—',
            float(report.cutting_rate) if report.cutting_rate else '—',
            report.fabric_type_quality,
            report.item_name,
            report.job_card_no,
            report.total_pcs,
            report.total_colours,
            float(report.total_weight_meter),
            float(report.avg_per_pcs),
            photo_names or '—',
            report.created_by.username if report.created_by else '—',
            report.created_at.strftime('%d-%b-%Y %H:%M'),
        ])

    _auto_width_and_style(ws4)

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
    for i, report in enumerate(Person4Report.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at'), start=1):
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
    for i, report in enumerate(Person5Report.objects.select_related('cutting_report__master_entry', 'created_by').order_by('-created_at'), start=1):
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
        'Total Pcs Packed', 'Green Tape', 'Red Tape', 'Blue Tape',
        'Photos', 'Submitted By', 'Submitted At'
    ]
    _write_header_row(ws7, headers7)

    from .models import Person6Report
    for i, report in enumerate(Person6Report.objects.select_related('cutting_report__master_entry', 'created_by').prefetch_related('photos').order_by('-created_at'), start=1):
        photo_names = ' | '.join(
            os.path.basename(p.photo.name) for p in report.photos.all()
        )
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
            photo_names or '—',
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
