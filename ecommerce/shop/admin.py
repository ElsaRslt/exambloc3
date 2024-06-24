from django.contrib import admin

from .models import Discipline, Evenement, Formule

#classer les produits et Discipline sous forme de tableau avec les informations 
class AdminDiscipline(admin.ModelAdmin):
    list_display = ('name' , 'date_added')
    
class AdminEvenement(admin.ModelAdmin):
    list_display = ('title','category','date_added')
    
class AdminFormule(admin.ModelAdmin):
    list_display = ('formule', 'price','evet_rattache')
    
# enregistrement des class models 
admin.site.register(Evenement, AdminEvenement)
admin.site.register(Discipline, AdminDiscipline)
admin.site.register(Formule, AdminFormule)

