from django.db import models
import uuid

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
class Utilisateur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    Email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=50)
    cle_securite = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    USERNAME_FIELD = 'Email'
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    