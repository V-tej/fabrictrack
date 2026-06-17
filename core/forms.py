from django import forms
from .models import MasterEntry, CuttingReport, Person2Report, Person3Report, Person4Report, Person5Report, Person6Report


class MasterEntryForm(forms.ModelForm):
    class Meta:
        model = MasterEntry
        fields = ['date', 'job_card_number']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'job_card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. JC-4523'}),
        }


class CuttingReportForm(forms.ModelForm):
    class Meta:
        model = CuttingReport
        fields = [
            'master_entry',
            'cutting_master_name',
            'cutting_rate',
            'fabric_type_quality',
            'item_name',
            'job_card_no',
            'total_pcs',
            'total_colours',
            'total_weight_meter',
            'avg_per_pcs',
            'signature',
        ]
        widgets = {
            'master_entry': forms.Select(attrs={'class': 'form-control', 'id': 'id_master_entry'}),
            'cutting_master_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cutting Master Name (optional)'}),
            'cutting_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'fabric_type_quality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cotton Poplin 40x40'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card Number'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_pcs', 'placeholder': '0'}),
            'total_colours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_weight_meter': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_weight', 'placeholder': '0.000', 'step': '0.001'}),
            'avg_per_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_avg_per_pcs', 'placeholder': 'Auto-calculated', 'step': '0.001'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'master_entry': 'Date & Lot No.',
            'cutting_master_name': 'Cutting Master Name',
            'cutting_rate': 'Cutting Rate',
            'fabric_type_quality': 'Fabric Type and Quality',
            'item_name': 'Item Name',
            'job_card_no': 'Job Card No.',
            'total_pcs': 'Total Pcs',
            'total_colours': 'Total No. of Colours',
            'total_weight_meter': 'Total Weight / Meter',
            'avg_per_pcs': 'Average per Pcs (Weight / Meter)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    # NOTE: Photo upload is handled as a raw HTML <input type="file" multiple>
    # in the template and via request.FILES.getlist('photos') in the view.
    # Django 5 does not allow multiple=True on any built-in FileInput widget.


class Person2ReportForm(forms.ModelForm):
    class Meta:
        model = Person2Report
        fields = [
            'cutting_report',
            'cutting_master_name',
            'cutting_rate',
            'fabric_type_quality',
            'item_name',
            'job_card_no',
            'total_pcs',
            'total_colours',
            'total_weight_meter',
            'avg_per_pcs',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'cutting_master_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cutting Master Name (optional)'}),
            'cutting_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'fabric_type_quality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cotton Poplin 40x40'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card Number'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_pcs', 'placeholder': '0'}),
            'total_colours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_weight_meter': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_weight', 'placeholder': '0.000', 'step': '0.001'}),
            'avg_per_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_avg_per_pcs', 'placeholder': 'Auto-calculated', 'step': '0.001'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'cutting_report': 'Select P1 Cutting Report',
            'cutting_master_name': 'Cutting Master Name',
            'cutting_rate': 'Cutting Rate',
            'fabric_type_quality': 'Fabric Type and Quality',
            'item_name': 'Item Name',
            'job_card_no': 'Job Card No.',
            'total_pcs': 'Total Pcs',
            'total_colours': 'Total No. of Colours',
            'total_weight_meter': 'Total Weight / Meter',
            'avg_per_pcs': 'Average per Pcs (Weight / Meter)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

class Person3ReportForm(forms.ModelForm):
    class Meta:
        model = Person3Report
        fields = [
            'cutting_report',
            'cutting_master_name',
            'cutting_rate',
            'fabric_type_quality',
            'item_name',
            'job_card_no',
            'total_pcs',
            'total_colours',
            'total_weight_meter',
            'avg_per_pcs',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'cutting_master_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cutting Master Name (optional)'}),
            'cutting_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'fabric_type_quality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cotton Poplin 40x40'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card Number'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_pcs', 'placeholder': '0'}),
            'total_colours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_weight_meter': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_weight', 'placeholder': '0.000', 'step': '0.001'}),
            'avg_per_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_avg_per_pcs', 'placeholder': 'Auto-calculated', 'step': '0.001'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'cutting_report': 'Select P1 Cutting Report',
            'cutting_master_name': 'CR Rahul Master Name',
            'cutting_rate': 'CR Rahul Rate',
            'fabric_type_quality': 'Fabric Type and Quality',
            'item_name': 'Item Name',
            'job_card_no': 'Job Card No.',
            'total_pcs': 'Total Pcs',
            'total_colours': 'Total No. of Colours',
            'total_weight_meter': 'Total Weight / Meter',
            'avg_per_pcs': 'Average per Pcs (Weight / Meter)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

class Person4ReportForm(forms.ModelForm):
    class Meta:
        model = Person4Report
        fields = [
            'cutting_report',
            'job_card_no',
            'line_in_date',
            'total_pcs',
            'line_out_date',
            'item_name',
            'darji_rate',
            'folding_rate',
            'overlock_rate',
            'total_rate',
            'option_1',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'line_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'line_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'darji_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'id': 'id_darji_rate'}),
            'folding_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'id': 'id_folding_rate'}),
            'overlock_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'id': 'id_overlock_rate'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-calculated', 'step': '0.01', 'id': 'id_total_rate'}),
            'option_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'job_card_no': 'Job Card Number',
            'line_in_date': 'Line In Date',
            'total_pcs': 'Total Pcs',
            'line_out_date': 'Line Out Date',
            'item_name': 'Item Name',
            'darji_rate': 'Darji Rate',
            'folding_rate': 'Folding Rate',
            'overlock_rate': 'Overlock Rate',
            'total_rate': 'Total Rate',
            'option_1': 'Option 1',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

class Person5ReportForm(forms.ModelForm):
    class Meta:
        model = Person5Report
        fields = [
            'cutting_report',
            'jobworker',
            'job_work_type',
            'purpose',
            'job_card_no',
            'date',
            'any_other_problem',
            'total_pcs_short',
            'total_pcs',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'jobworker': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jobworker Name'}),
            'job_work_type': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'any_other_problem': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any other problem...', 'rows': 3}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'jobworker': 'Jobworker',
            'job_work_type': 'Job Work In / Out',
            'purpose': 'Purpose',
            'job_card_no': 'Job Card No.',
            'date': 'Date',
            'any_other_problem': 'Any other Problem',
            'total_pcs_short': 'Total Pcs short',
            'total_pcs': 'Total Pcs',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

class Person6ReportForm(forms.ModelForm):
    class Meta:
        model = Person6Report
        fields = [
            'cutting_report',
            'date',
            'lot_no',
            'total_pcs',
            'total_pcs_short',
            'total_pcs_packed',
            'green_tape',
            'red_tape',
            'blue_tape',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date'}),
            'lot_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lot No.', 'id': 'id_lot_no'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs_packed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'green_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'red_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'blue_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'date': 'Date',
            'lot_no': 'Lot No',
            'total_pcs': 'Total pcs',
            'total_pcs_short': 'Total Pcs Short',
            'total_pcs_packed': 'Total Pcs Packed',
            'green_tape': 'Green Tape',
            'red_tape': 'Red Tape',
            'blue_tape': 'Blue Tape',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature
