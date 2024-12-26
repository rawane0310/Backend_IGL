from django import forms

class DossierPatientForm(forms.Form):
    patient_id = forms.IntegerField(label="ID du Patient", min_value=1)
   
