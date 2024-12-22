from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user manager that supports user creation with only email, password, and role.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # Remove the default username field
    email = models.EmailField(max_length=100, unique=True,default="email@example.com")
    role = models.CharField(
        max_length=20, 
        choices=[('admin', 'Admin'), ('technicien', 'Technicien'), ('patient', 'Patient'),('administratif','Administratif')], 
        default='admin'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Only email is required for user creation

    # Add unique related_name for groups and permissions to avoid conflicts
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

    objects = CustomUserManager()  # Link to custom manager

    def __str__(self):
        return self.email
# User model
#class User(AbstractUser):
 #   email = models.EmailField(unique=True)
  #password = models.CharField(max_length=128)
   # role = models.CharField(max_length=50)  #patient , technicien , admin 


#Admin model
class Admin(models.Model):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')  # Corrected ForeignKey relationship


#Administratif model
class Administratif(models.Model):
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='administratif')  # Corrected ForeignKey relationship


# Technician model
class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician')
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    role = models.CharField(max_length=50)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    outils = models.JSONField(blank=True, null=True)  # List des tools comme chaine de car

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
    
    validation = models.BooleanField(default=False)   

class DossierPatient(models.Model):
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='dossier')
    qr = models.TextField()  # QR 

# SoinInfermier model
class SoinInfermier(models.Model):
    date = models.DateField()
    infirmier = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='soins_infirmiers',null=True)
    
    observation = models.TextField(blank=True, null=True)
    soin_realise = models.TextField()
    dossier = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='soins_infirmiers')

# Medicament model
class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    dose = models.CharField(max_length=50)
    frequence = models.CharField(max_length=50,null=True, blank=True)
    duree = models.CharField(max_length=50,null=True, blank=True)
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name='medicaments',null=True, blank=True)
    soin = models.ForeignKey(SoinInfermier, on_delete=models.CASCADE, related_name='medicaments',null=True, blank=True)


    

class Resume(models.Model):
    diagnostic = models.TextField(blank=True, null=True)
    symptomes = models.TextField(blank=True, null=True)
    mesures_prises = models.TextField( blank=True, null=True)
    date_prochaine_consultation = models.DateField( blank=True, null=True)
    


class Consultation(models.Model):
    date = models.DateField()
    medecin = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, related_name='consultations')

    diagnosticStatut = models.BooleanField(default=False) 

    resume = models.OneToOneField(Resume, on_delete=models.SET_NULL, null=True,blank=True, related_name='consultations')
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.SET_NULL, null=True,blank=True, related_name='consultations')
   
    dossier = models.ForeignKey(DossierPatient , on_delete=models.CASCADE, related_name='consultations') 





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
    image = models.ImageField(upload_to='radiology_images/',blank=True, null=True)
    compte_rendu = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    dossier_patient = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='examens_radiologiques')


class ExamenBiologique(models.Model):
    date = models.DateField()

    technicien = models.ForeignKey(Technician, on_delete=models.SET_NULL, related_name='examens_biologiques',null=True)   

    description = models.TextField(blank=True, null=True)
    dossier_patient = models.ForeignKey(DossierPatient, on_delete=models.CASCADE, related_name='examens_biologiques')


# ResultatExamen model
class ResultatExamen(models.Model):
    parametre = models.CharField(max_length=100)
    valeur = models.CharField(max_length=100)
    unite = models.CharField(max_length=50)
    commentaire = models.TextField(blank=True, null=True)

    examen_biologique = models.ForeignKey(ExamenBiologique, on_delete=models.CASCADE, related_name='resultats')


    



#class ExamenBiologiqueResultat(models.Model):
 #   examen_biologique = models.ForeignKey(ExamenBiologique, on_delete=models.CASCADE)
 #   resultat_examen = models.ForeignKey(ResultatExamen, on_delete=models.CASCADE)


# changes 
