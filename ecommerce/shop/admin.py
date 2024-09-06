from django.contrib import admin
from .models import Discipline, Evenement, Formule, Commande

admin.site.site_header = "JO PARIS 2024"
admin.site.site_title = "Administration"
admin.site.index_title = "Administration"

#classer les produits et Discipline sous forme de tableau avec les informations 
class AdminDiscipline(admin.ModelAdmin):
    list_display = ('name' , 'date_added')
    search_fields = ('name',) #permet de chercher avec le nom 
    
class AdminEvenement(admin.ModelAdmin):
    list_display = ('title','category','date_added', 'base_price')
    search_fields = ('title','category',) #permet de chercher avec le nom et le sport
    list_editable = ('base_price',)
    
class AdminFormule(admin.ModelAdmin):
    list_display = ('formule','price_multiplier')
    

class CommandeAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_security_key', 'prix_total', 'date_commande')

    def user_full_name(self, obj):
        return f"{obj.user.nom} {obj.user.prenom}"
    user_full_name.short_description = 'Nom Complet'

    def user_security_key(self, obj):
        return obj.user.cle_securite
    user_security_key.short_description = 'Clé de Sécurité'
    
    
# enregistrement des class models 
admin.site.register(Evenement, AdminEvenement)
admin.site.register(Discipline, AdminDiscipline)
admin.site.register(Formule, AdminFormule)
admin.site.register(Commande, CommandeAdmin)



