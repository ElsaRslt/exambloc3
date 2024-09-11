from django.contrib import admin
from .models import Discipline, Evenement, Formule, Commande, Utilisateur

admin.site.site_header = "JO PARIS 2024"
admin.site.site_title = "Administration"
admin.site.index_title = "Administration"

# Classer les produits et Discipline sous forme de tableau avec les informations 
class AdminDiscipline(admin.ModelAdmin):
    list_display = ('name', 'date_added')
    search_fields = ('name',)

class AdminEvenement(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_added', 'base_price', 'total_sales')
    search_fields = ('title', 'category',)
    list_editable = ('base_price',)

    def total_sales(self, obj):
        # Compte le nombre de commandes associées à cet événement
        return Commande.objects.filter(evenements=obj).count()
    total_sales.short_description = 'Nombre de ventes'

class AdminFormule(admin.ModelAdmin):
    list_display = ('formule', 'price_multiplier', 'total_sales')

    def total_sales(self, obj):
        # Compte le nombre de commandes associées à cette formule
        return Commande.objects.filter(formules=obj).count()
    total_sales.short_description = 'Nombre de ventes'

class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero_commande', 'user', 'prix_total', 'date_commande', 'cle_securite_commande', 'get_formules', 'get_evenements']
    
    def has_change_permission(self, request, obj=None):
        return False

    def get_formules(self, obj):
        return ", ".join([f.formule for f in obj.formules.all()])
    get_formules.short_description = 'Formules'

    def get_evenements(self, obj):
        return ", ".join([e.title for e in obj.evenements.all()])
    get_evenements.short_description = 'Événements'

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'cle_securite', 'is_superuser')

admin.site.register(Evenement, AdminEvenement)
admin.site.register(Discipline, AdminDiscipline)
admin.site.register(Formule, AdminFormule)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Utilisateur, UtilisateurAdmin)



