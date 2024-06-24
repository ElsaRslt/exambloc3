from django.db import models



#création table des disciplines

class Discipline (models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)
    

#la derniere discipline créée se place en premier dans la liste 
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
    
    #le dernier evenement créé se place en premier dans la liste 
    class Meta:
        ordering = ['-date_added']
    def __str__(self):
        return self.title
    
# Création d'une classe formule avec prix nombre de personne titre et une foreign key vers evenement 
class Formule (models.Model):
    formule = models.CharField(max_length=200)
    price = models.FloatField()
    evet_rattache = models.ForeignKey(Evenement, related_name = 'EV', on_delete=models.CASCADE)
    def __str__(self):
        return self.formule