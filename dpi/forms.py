from django import forms

class DossierPatientForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
  
    nom = forms.CharField(max_length=100, label="Nom")
    prenom = forms.CharField(max_length=100, label="Prénom")
    adresse = forms.CharField(max_length=255, label="Adresse")
    date_naissance = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), label="Date de naissance")
    tel = forms.CharField(max_length=15, label="Numéro de téléphone")
    mutuelle = forms.CharField(max_length=100, label="Mutuelle")
    medecin_traitant = forms.IntegerField(label="Medecin traitant ID", min_value=1)
    personne_a_contacter = forms.CharField(max_length=100, label="Personne à contacter")
    nss = forms.CharField(max_length=100, label="Numéro de sécurité sociale")
    
    
   
