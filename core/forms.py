from django import forms
from .models import MasterEntry, CuttingReport, MasterName, StitchingReport, JobWorkReport, FinishingReport, EmbroideryReport, PrintingReport, SingleneedleReport, SewingReport


class MasterEntryForm(forms.ModelForm):
    YES_NO_CHOICES = [('True', 'Yes'), ('False', 'No')]
    requires_cutting = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_jobwork = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_stitching = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_finishing = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_embroidery = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_printing = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_singleneedle = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))
    requires_sewing = forms.TypedChoiceField(choices=YES_NO_CHOICES, coerce=lambda x: x == 'True', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = MasterEntry
        fields = ['date', 'job_card_number']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'job_card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. JC-4523'}),
        }


class CuttingReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Cutting Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Cutting')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['cutting_master_name'].required = False
        self.fields['rate_definition'].required = True
        self.fields['rate_definition'].empty_label = "Select Rate..."
    class Meta:
        model = CuttingReport
        fields = [
            'report_type',
            'master_entry',
            'master_name',
            'cutting_master_name',
            'rate_definition',
            'cutting_rate',
            'fabric_type_quality',
            'item_name',
            'job_card_no',
            'size_s',
            'size_m',
            'size_l',
            'size_xl',
            'size_2xl',
            'size_3xl',
            'size_4xl',
            'total_pcs',
            'total_colours',
            'total_weight',
            'total_meters',
            'avg_per_pcs',
            'signature',
        ]
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_report_type'}),
            'master_entry': forms.Select(attrs={'class': 'form-control', 'id': 'id_master_entry'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'cutting_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_cutting_rate', 'readonly': 'readonly', 'placeholder': 'Auto-populated', 'step': '0.01'}),
            'fabric_type_quality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cotton Poplin 40x40'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card Number'}),
            'size_s': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_m': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_l': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_xl': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_2xl': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_3xl': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'size_4xl': forms.NumberInput(attrs={'class': 'form-control size-input', 'min': '0', 'readonly': 'readonly'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_pcs', 'placeholder': '0', 'readonly': 'readonly'}),
            'total_colours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_weight': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_weight', 'placeholder': '0.000', 'step': '0.001'}),
            'total_meters': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_meters', 'placeholder': '0.000', 'step': '0.001'}),
            'avg_per_pcs': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_avg_per_pcs', 'placeholder': 'Auto-calculated', 'step': '0.001'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
        }
        labels = {
            'report_type': 'Report Type (Who is this for?)',
            'master_entry': 'Date & Lot No.',
            'master_name': 'Select Master Name',
            'cutting_master_name': 'Or enter manually',
            'rate_definition': 'Rate',
            'cutting_rate': 'Cutting Rate',
            'fabric_type_quality': 'Fabric Type and Quality',
            'item_name': 'Item Name',
            'job_card_no': 'Job Card No.',
            'total_pcs': 'Total Pcs',
            'total_colours': 'Total No. of Colours',
            'total_weight': 'Total Weight (kg)',
            'total_meters': 'Total Meters (m)',
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




class StitchingReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Stitching Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Stitching')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['stitching_master_name'].required = False
        self.fields['line_out_date'].required = False
        self.fields['rate_definition'].required = True
        self.fields['rate_definition'].empty_label = "Select Rate..."

    class Meta:
        model = StitchingReport
        fields = [
            'master_name',
            'stitching_master_name',
            'cutting_report',
            'job_card_no',
            'line_in_date',
            'total_pcs',
            'line_out_date',
            'item_name',
            'rate_definition',
            'total_rate',
            'option_1',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'line_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'line_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-populated', 'readonly': 'readonly', 'id': 'id_total_rate'}),
            'option_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'job_card_no': 'Job Card Number',
            'line_in_date': 'Line In Date',
            'total_pcs': 'Total Pcs',
            'line_out_date': 'Line Out Date',
            'item_name': 'Item Name',
            'rate_definition': 'Rate',
            'total_rate': 'Total Rate',
            'option_1': 'Option 1',
        }

    def clean(self):
        cleaned_data = super().clean()
        line_in_date = cleaned_data.get('line_in_date')
        line_out_date = cleaned_data.get('line_out_date')

        if line_in_date and line_out_date and line_in_date == line_out_date:
            self.add_error('line_out_date', "Line Out Date cannot be the same as Line In Date.")

        return cleaned_data

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2


class SingleneedleReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Singleneedle Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Singleneedle')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['singleneedle_master_name'].required = False
        self.fields['line_out_date'].required = False
        self.fields['rate_definition'].required = True
        self.fields['rate_definition'].empty_label = "Select Rate..."

    class Meta:
        model = SingleneedleReport
        fields = [
            'master_name',
            'singleneedle_master_name',
            'cutting_report',
            'job_card_no',
            'line_in_date',
            'total_pcs',
            'line_out_date',
            'item_name',
            'rate_definition',
            'total_rate',
            'option_1',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'line_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'line_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-populated', 'readonly': 'readonly', 'id': 'id_total_rate'}),
            'option_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'job_card_no': 'Job Card Number',
            'line_in_date': 'Line In Date',
            'total_pcs': 'Total Pcs',
            'line_out_date': 'Line Out Date',
            'item_name': 'Item Name',
            'rate_definition': 'Rate',
            'total_rate': 'Total Rate',
            'option_1': 'Option 1',
        }

    def clean(self):
        cleaned_data = super().clean()
        line_in_date = cleaned_data.get('line_in_date')
        line_out_date = cleaned_data.get('line_out_date')

        if line_in_date and line_out_date and line_in_date == line_out_date:
            self.add_error('line_out_date', "Line Out Date cannot be the same as Line In Date.")

        return cleaned_data

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2


class SewingReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Sewing Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Sewing')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['sewing_master_name'].required = False
        self.fields['line_out_date'].required = False
        self.fields['rate_definition'].required = True
        self.fields['rate_definition'].empty_label = "Select Rate..."

    class Meta:
        model = SewingReport
        fields = [
            'master_name',
            'sewing_master_name',
            'cutting_report',
            'job_card_no',
            'line_in_date',
            'total_pcs',
            'line_out_date',
            'item_name',
            'rate_definition',
            'total_rate',
            'option_1',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'line_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'line_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-populated', 'readonly': 'readonly', 'id': 'id_total_rate'}),
            'option_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'job_card_no': 'Job Card Number',
            'line_in_date': 'Line In Date',
            'total_pcs': 'Total Pcs',
            'line_out_date': 'Line Out Date',
            'item_name': 'Item Name',
            'rate_definition': 'Rate',
            'total_rate': 'Total Rate',
            'option_1': 'Option 1',
        }

    def clean(self):
        cleaned_data = super().clean()
        line_in_date = cleaned_data.get('line_in_date')
        line_out_date = cleaned_data.get('line_out_date')

        if line_in_date and line_out_date and line_in_date == line_out_date:
            self.add_error('line_out_date', "Line Out Date cannot be the same as Line In Date.")

        return cleaned_data

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2


class JobWorkReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Job Worker')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Job Work')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['jobworker'].required = False
        self.fields['jobwork_out'].required = False
        self.fields['design_jobwork'].required = False
        self.fields['rate_definition'].required = False
        self.fields['total_rate'].required = False
    class Meta:
        model = JobWorkReport
        fields = [
            'cutting_report',
            'master_name',
            'jobworker',
            'purpose',
            'job_card_no',
            'jobwork_in',
            'jobwork_out',
            'any_other_problem',
            'total_pcs_short',
            'total_pcs',
            'design_jobwork',
            'rate_definition',
            'total_rate',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'jobwork_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jobwork_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'any_other_problem': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any other problem...', 'rows': 3}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'design_jobwork': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Design Jobwork'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_rate', 'step': '0.01', 'placeholder': '0.00'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'jobworker': 'Jobworker',
            'purpose': 'Purpose',
            'job_card_no': 'Job Card No.',
            'jobwork_in': 'Jobwork In Date',
            'jobwork_out': 'Jobwork Out Date',
            'any_other_problem': 'Any other Problem',
            'total_pcs_short': 'Total Pcs short',
            'total_pcs': 'Total Pcs',
            'design_jobwork': 'Design Jobwork',
            'rate_definition': 'Rate Name',
            'total_rate': 'Rate (₹)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2

    def clean(self):
        cleaned_data = super().clean()
        jobwork_in = cleaned_data.get('jobwork_in')
        jobwork_out = cleaned_data.get('jobwork_out')
        if jobwork_in and jobwork_out and jobwork_in >= jobwork_out:
            if jobwork_in == jobwork_out:
                self.add_error('jobwork_out', "Job Work Out Date cannot be the same as Job Work In Date.")
            else:
                self.add_error('jobwork_out', "Job Work Out Date cannot be before Job Work In Date.")
        return cleaned_data

class FinishingReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Finishing Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Finishing')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['finishing_master_name'].required = False
        self.fields['rate_definition'].required = False
        self.fields['total_rate'].required = False
    class Meta:
        model = FinishingReport
        fields = [
            'master_name',
            'finishing_master_name',
            'cutting_report',
            'date',
            'lot_no',
            'total_pcs',
            'total_pcs_short',
            'total_pcs_packed',
            'green_tape',
            'red_tape',
            'blue_tape',
            'total_tape',
            'rate_definition',
            'total_rate',
            'signature',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_date'}),
            'lot_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lot No.', 'id': 'id_lot_no'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_total_pcs_short'}),
            'total_pcs_packed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_total_pcs_packed', 'readonly': 'readonly'}),
            'green_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_green_tape'}),
            'red_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_red_tape'}),
            'blue_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_blue_tape'}),
            'total_tape': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'id': 'id_total_tape', 'readonly': 'readonly'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_rate', 'step': '0.01', 'placeholder': '0.00'}),
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
            'total_tape': 'Total Tape',
            'rate_definition': 'Rate Name',
            'total_rate': 'Rate',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature


class EmbroideryReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Embroidery Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Embroidery')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['embroidery_worker'].required = False
        self.fields['embroidery_out'].required = False
        self.fields['design_embroidery'].required = False
        self.fields['rate_definition'].required = False
        self.fields['total_rate'].required = False
    class Meta:
        model = EmbroideryReport
        fields = [
            'cutting_report',
            'master_name',
            'embroidery_worker',
            'purpose',
            'job_card_no',
            'embroidery_in',
            'embroidery_out',
            'any_other_problem',
            'total_pcs_short',
            'total_pcs',
            'design_embroidery',
            'rate_definition',
            'total_rate',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'embroidery_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'embroidery_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'any_other_problem': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any other problem...', 'rows': 3}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'design_embroidery': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Design Embroidery'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_rate', 'step': '0.01', 'placeholder': '0.00'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'embroidery_worker': 'Embroidery Worker',
            'purpose': 'Purpose',
            'job_card_no': 'Job Card No.',
            'embroidery_in': 'Embroidery In Date',
            'embroidery_out': 'Embroidery Out Date',
            'any_other_problem': 'Any other Problem',
            'total_pcs_short': 'Total Pcs short',
            'total_pcs': 'Total Pcs',
            'design_embroidery': 'Design Embroidery',
            'rate_definition': 'Rate Name',
            'total_rate': 'Rate (₹)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2

    def clean(self):
        cleaned_data = super().clean()
        embroidery_in = cleaned_data.get('embroidery_in')
        embroidery_out = cleaned_data.get('embroidery_out')
        if embroidery_in and embroidery_out and embroidery_in >= embroidery_out:
            if embroidery_in == embroidery_out:
                self.add_error('embroidery_out', "Embroidery Out Date cannot be the same as Embroidery In Date.")
            else:
                self.add_error('embroidery_out', "Embroidery Out Date cannot be before Embroidery In Date.")
        return cleaned_data


class PrintingReportForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [('', 'Select Printing Master')]
        try:
            choices += [(m.name, m.name) for m in MasterName.objects.filter(department='Printing')]
        except Exception:
            pass
        self.fields['master_name'] = forms.ChoiceField(choices=choices, required=False, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_master_name'}))
        self.fields['printing_worker'].required = False
        self.fields['printing_out'].required = False
        self.fields['design_printing'].required = False
        self.fields['rate_definition'].required = False
        self.fields['total_rate'].required = False
    class Meta:
        model = PrintingReport
        fields = [
            'cutting_report',
            'master_name',
            'printing_worker',
            'purpose',
            'job_card_no',
            'printing_in',
            'printing_out',
            'any_other_problem',
            'total_pcs_short',
            'total_pcs',
            'design_printing',
            'rate_definition',
            'total_rate',
            'signature',
            'signature_2',
        ]
        widgets = {
            'cutting_report': forms.Select(attrs={'class': 'form-control', 'id': 'id_cutting_report'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose'}),
            'job_card_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Card No.', 'id': 'id_job_card_no'}),
            'printing_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'printing_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'any_other_problem': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any other problem...', 'rows': 3}),
            'total_pcs_short': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'total_pcs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Auto-filled', 'readonly': 'readonly', 'id': 'id_total_pcs'}),
            'design_printing': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Design Printing'}),
            'rate_definition': forms.Select(attrs={'class': 'form-control', 'id': 'id_rate_definition'}),
            'total_rate': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_total_rate', 'step': '0.01', 'placeholder': '0.00'}),
            'signature': forms.HiddenInput(attrs={'id': 'id_signature'}),
            'signature_2': forms.HiddenInput(attrs={'id': 'id_signature_2'}),
        }
        labels = {
            'cutting_report': 'Select Cutting Report',
            'printing_worker': 'Printing Worker',
            'purpose': 'Purpose',
            'job_card_no': 'Job Card No.',
            'printing_in': 'Printing In Date',
            'printing_out': 'Printing Out Date',
            'any_other_problem': 'Any other Problem',
            'total_pcs_short': 'Total Pcs short',
            'total_pcs': 'Total Pcs',
            'design_printing': 'Design Printing',
            'rate_definition': 'Rate Name',
            'total_rate': 'Rate (₹)',
        }

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if not signature:
            raise forms.ValidationError("Please provide a signature.")
        return signature

    def clean_signature_2(self):
        signature_2 = self.cleaned_data.get('signature_2')
        if not signature_2:
            raise forms.ValidationError("Please provide a second signature.")
        return signature_2

    def clean(self):
        cleaned_data = super().clean()
        printing_in = cleaned_data.get('printing_in')
        printing_out = cleaned_data.get('printing_out')
        if printing_in and printing_out and printing_in >= printing_out:
            if printing_in == printing_out:
                self.add_error('printing_out', "Printing Out Date cannot be the same as Printing In Date.")
            else:
                self.add_error('printing_out', "Printing Out Date cannot be before Printing In Date.")
        return cleaned_data
