from django.db import models
from django.contrib.auth.models import AbstractUser









from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    role = models.CharField(
        max_length=10, 
        choices=[('admin', 'Admin'), ('technicien', 'Technicien'), ('patient', 'Patient')], 
        default='admin'
    )  # Set a default role for users
    phone_number = models.CharField(max_length=10, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)  # Add last_login field

    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']  # Only email is required for user creation, remove 'username'

    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Unique related_name to avoid conflicts
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    # Override the default related_name for user_permissions to avoid conflicts
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        # Set the role to 'admin' for superusers if role is not set
        if self.is_superuser and not self.role:
            self.role = 'admin'
        super().save(*args, **kwargs)

    

# User model
#class User(AbstractUser):
 #   email = models.EmailField(unique=True)
  #password = models.CharField(max_length=128)
   # role = models.CharField(max_length=50)  #patient , technicien , admin 

# Technician model
class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    specialite = models.CharField(max_length=100)
    outils = models.JSONField()  # List des tools comme chaine de car

# Patient model
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    date_naissance = models.DateField()
    adresse = models.TextField()
    tel = models.CharField(max_length=15)
    mutuelle = models.CharField(max_length=100, blank=True, null=True)
    medecin_traitant = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, related_name='patients')
    personne_a_contacter = models.CharField(max_length=100)
    
    nss = models.CharField(max_length=20) 




# Ordonnance model
class Ordonnance(models.Model):
    date = models.DateField()
    
    validation = models.BooleanField(default=False)   # is validated 

class DossierPatient(models.Model):
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier')
    qr = models.TextField()  # QR 

# SoinInfermier model
class SoinInfermier(models.Model):
    date = models.DateField()
    infirmier = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='soins_infirmiers',null=True)
    
    observation = models.TextField()
    soin_realise = models.TextField()
    dossier = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='soins_infirmiers')

# Medicament model
class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    dose = models.CharField(max_length=50)
    frequence = models.CharField(max_length=50)
    duree = models.CharField(max_length=50)
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name='medicaments')
    soin = models.ForeignKey(SoinInfermier, on_delete=models.CASCADE, related_name='medicaments')


    



class Consultation(models.Model):
    date = models.DateField()
    medecin = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, related_name='consultations')
    diagnostic = models.TextField()
    resume = models.TextField()
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.SET_NULL, null=True, related_name='consultations')
   
    dossier = models.ForeignKey(DossierPatient , on_delete=models.CASCADE, related_name='consultations')  # New field





# Hopital model
class Hopital(models.Model):
    nom = models.CharField(max_length=100)
    lieu = models.TextField()


# Certificat model
class Certificat(models.Model):
    date = models.DateField()
    medecin = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='certificats',null=True)
    contenu = models.TextField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='certificats')


class ExamenRadiologique(models.Model):
    date = models.DateField()
    technicien = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='examens_radiologiques',null=True)
    image = models.ImageField(upload_to='radiology_images/')
    compte_rendu = models.TextField()
    description = models.TextField()
    dossier_patient = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='examens_radiologiques')


class ExamenBiologique(models.Model):
    date = models.DateField()
    technicien = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='examens_biologiques',null=True)
    description = models.TextField()
    dossier_patient = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='examens_biologiques')


# ResultatExamen model
class ResultatExamen(models.Model):
    parametre = models.CharField(max_length=100)
    valeur = models.CharField(max_length=100)
    unite = models.CharField(max_length=50)
    commentaire = models.TextField()

    examen_biologique = models.ForeignKey(ExamenBiologique, on_delete=models.CASCADE, related_name='resultats')

    class Meta:
        unique_together = ('parametre', 'examen_biologique')



#class ExamenBiologiqueResultat(models.Model):
 #   examen_biologique = models.ForeignKey(ExamenBiologique, on_delete=models.CASCADE)
 #   resultat_examen = models.ForeignKey(ResultatExamen, on_delete=models.CASCADE)


# changes 