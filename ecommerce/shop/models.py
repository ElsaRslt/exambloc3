from django.db import models

#création table
class Discipline (models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)
    
#faire que quand on ajoute une discipline elle se met en premier dans la liste
    class Meta:
        ordering = ['-date_added']
    def __str__(self):
        return self.name
    
    
#création table des evenements 
class Evenement (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Discipline, related_name = 'Discipline', on_delete=models.CASCADE)
    date_event = models.DateTimeField()
    image = models.CharField(max_length=5000, )
    date_added = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-date_added']
    def __str__(self):
        return self.title
    
    # faire la création d'une classe formule avec prix nombre de personne titre et une foreign key vers evenement 
    
class Formule (models.Model):
    formule = models.CharField(max_length=200)
    price = models.FloatField()
    evet_rattache = models.ForeignKey(Evenement, related_name = 'EV', on_delete=models.CASCADE)
    def __str__(self):
        return self.formule