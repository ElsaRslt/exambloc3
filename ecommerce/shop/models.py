from django.db import models
import uuid
import random
import string
from django.contrib.auth.models import AbstractUser, Group, Permission # pour avoir les fonctionnalité Django de la gestion utilisateur
from django.conf import settings


#création table des disciplines
class Discipline (models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)
#la derniere discipline créée se place en premier dans la liste 
    class Meta:
        ordering = ['-date_added']
    def __str__(self):
        return self.name
    

# Création d'une classe formule avec prix nombre de personne titre et une foreign key vers evenement 
class Formule (models.Model):
    formule = models.CharField(max_length=200)
    price_multiplier = models.FloatField()
    # evet_rattache = models.ForeignKey(Evenement, related_name = 'EV', on_delete=models.CASCADE)
    def __str__(self):
        return self.formule

    
#création table des evenements 
class Evenement (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Discipline, related_name = 'Discipline', on_delete=models.CASCADE)
    date_event = models.DateTimeField()
    image = models.ImageField(upload_to='event_images/')
    date_added = models.DateTimeField(auto_now=True)
    formules = models.ManyToManyField(Formule, related_name ='formule_choisie')
    base_price = models.FloatField(default=10.0)
    
    #le dernier evenement créé se place en premier dans la liste 
    class Meta:
        ordering = ['-date_added']
    def __str__(self):
        return self.title
    
    
# création table utilisateur pour inscription et connexion 
class Utilisateur(AbstractUser):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    cle_securite = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=150, unique=False)  # Le username devient obligatoire et unique

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nom', 'prenom']  # username devient requis

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
    )

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    

# Fonction pour générer un numéro de commande unique
def generate_order_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Création d'une classe pour enregistrement des commandes
class Commande(models.Model):
    user = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    panier = models.TextField()  # Pour stocker le panier en format JSON
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_commande = models.DateTimeField(auto_now_add=True)
    cle_securite_commande = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    numero_commande = models.CharField(max_length=6, unique=True, blank=True, editable=False)
    ebillet_path = models.CharField(max_length=255, null=True, blank=True)  # Stocker le chemin de l'e-billet

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            self.numero_commande = generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.numero_commande} - {self.user.username}"