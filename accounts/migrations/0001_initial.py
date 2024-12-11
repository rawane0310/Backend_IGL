# Generated by Django 5.0.2 on 2024-12-05 15:20

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='DossierPatient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Hopital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('lieu', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Medicament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('dose', models.CharField(max_length=50)),
                ('frequence', models.CharField(max_length=50)),
                ('duree', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Ordonnance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('validation', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('date_naissance', models.DateField()),
                ('adresse', models.TextField()),
                ('tel', models.CharField(max_length=15)),
                ('mutuelle', models.CharField(blank=True, max_length=100, null=True)),
                ('personne_a_contacter', models.CharField(max_length=100)),
                ('qr', models.TextField()),
                ('nss', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('role', models.CharField(max_length=50)),
                ('specialite', models.CharField(max_length=100)),
                ('outils', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='ExamenBiologique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('terminaison', models.TextField()),
                ('dossier_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examens_biologiques', to='accounts.dossierpatient')),
                ('technicien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examens_biologiques', to='accounts.technician')),
            ],
        ),
        migrations.AddField(
            model_name='dossierpatient',
            name='examen_bio',
            field=models.ManyToManyField(blank=True, related_name='dossiers', to='accounts.examenbiologique'),
        ),
        migrations.CreateModel(
            name='ExamenRadiologique',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('image', models.ImageField(upload_to='radiology_images/')),
                ('compte_rendu', models.TextField()),
                ('terminaison', models.BooleanField()),
                ('dossier_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examens_radiologiques', to='accounts.dossierpatient')),
                ('technicien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examens_radiologiques', to='accounts.technician')),
            ],
        ),
        migrations.AddField(
            model_name='dossierpatient',
            name='examen_radio',
            field=models.ManyToManyField(blank=True, related_name='dossiers', to='accounts.examenradiologique'),
        ),
        migrations.CreateModel(
            name='OrdonnanceMedicament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.medicament')),
                ('ordonnance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.ordonnance')),
            ],
        ),
        migrations.AddField(
            model_name='ordonnance',
            name='medicaments',
            field=models.ManyToManyField(through='accounts.OrdonnanceMedicament', to='accounts.medicament'),
        ),
        migrations.AddField(
            model_name='dossierpatient',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dossier', to='accounts.patient'),
        ),
        migrations.CreateModel(
            name='ResultatExamen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parametre', models.CharField(max_length=100)),
                ('valeur', models.CharField(max_length=100)),
                ('unite', models.CharField(max_length=50)),
                ('commentaire', models.TextField()),
                ('examen_biologique', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resultats', to='accounts.examenbiologique')),
            ],
        ),
        migrations.CreateModel(
            name='SoinInfermier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('observation', models.TextField()),
                ('soin_realise', models.TextField()),
                ('medicament_administré', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soins_infirmiers', to='accounts.medicament')),
                ('infirmier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soins_infirmiers', to='accounts.technician')),
            ],
        ),
        migrations.AddField(
            model_name='dossierpatient',
            name='soin_infirmier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dossiers', to='accounts.soininfermier'),
        ),
        migrations.CreateModel(
            name='SoinInfermierMedicament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.medicament')),
                ('soin_infirmier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.soininfermier')),
            ],
        ),
        migrations.AddField(
            model_name='patient',
            name='medecin_traitant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patients', to='accounts.technician'),
        ),
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('diagnostic', models.TextField()),
                ('resume', models.TextField()),
                ('dossier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultations', to='accounts.dossierpatient')),
                ('ordonnance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consultations', to='accounts.ordonnance')),
                ('medecin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='consultations', to='accounts.technician')),
            ],
        ),
        migrations.CreateModel(
            name='Certificat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('contenu', models.TextField()),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificats', to='accounts.patient')),
                ('medecin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificats', to='accounts.technician')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('technicien', 'Technicien'), ('patient', 'Patient')], default='admin', max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='custom_user_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_user_permissions_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='technician',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='technician', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='patient',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to='accounts.user'),
        ),
    ]
