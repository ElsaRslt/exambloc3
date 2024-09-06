from django.contrib import admin
from .models import Discipline, Evenement, Formule, Commande, Utilisateur

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
    list_display = ('user_full_name', 'cle_securite_commande', 'numero_commande','prix_total', 'date_commande')

    def user_full_name(self, obj):
        return f"{obj.user.nom} {obj.user.prenom}"
    user_full_name.short_description = 'Nom Complet'

    
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom',"email", "cle_securite","is_superuser")
    
    
# enregistrement des class models 
admin.site.register(Evenement, AdminEvenement)
admin.site.register(Discipline, AdminDiscipline)
admin.site.register(Formule, AdminFormule)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)



