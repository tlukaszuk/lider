from django.forms import ModelForm, TextInput, HiddenInput
from django import forms
from .models import ApplicationRate, Farmer, GrowingField, Order


class ApplicationRateForm(ModelForm):
    class Meta:
        model = ApplicationRate
        fields = [
            'farmer', 'growing_field',
            'pha_crop_type', 'pha_soil_agronomic_category', 'pha_soil_ph_H2O', 'pha_lider_ca_application_rate_per_hectare', 'pha_lider_ca_application_rate_per_field',
            'cn_crop_kind', 'cn_expected_yield', 'cn_lider_mg_application_rate_per_hectare', 'cn_lider_mg_application_rate_per_field',
            'date_of_calculation'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('pha_lider_ca_application_rate_per_hectare', 'pha_lider_ca_application_rate_per_field', 'cn_lider_mg_application_rate_per_hectare', 'cn_lider_mg_application_rate_per_field'):
            self.fields[field_name].widget = TextInput(attrs={'readonly': 'readonly'})
        self.fields['growing_field'].choices = [('','---------'),]



class FarmerForm(ModelForm):
    class Meta:
        model = Farmer
        fields = ['name', 'location', 'comments']


class GrowingFieldForm(ModelForm):
    class Meta:
        model = GrowingField
        fields = ['field_number', 'area', 'description', 'parcel_number', 'farmer']


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['farmer', 'client', 'growing_fields', 'lider_ca_weight', 'lider_mg_weight', 'lider_ca_price', 'lider_mg_price', 'packing_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('farmer', 'client', 'growing_fields', 'lider_ca_weight', 'lider_mg_weight'):
            self.fields[field_name].widget = HiddenInput()
        self.fields['packing_type'].choices = self.fields['packing_type'].choices[1:]


class SelectFarmerForm(forms.Form):
    farmer = forms.ModelChoiceField(label="Wybierz rolnika", queryset=Farmer.objects.all())

