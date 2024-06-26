from django.shortcuts import render
from .models import Evenement
from django.db.models import Q  # Import de l'opérateur Q pour les requêtes complexes

# Fonction qui va permettre d'afficher le fichier index et les images
def index(request):
    evenement_object = Evenement.objects.all()  # Sélection de tous les événements qui sont dans la BDD
    
    # Fonction pour faire la recherche via la barre de recherche
    items_name = request.GET.get('items-name')  # Récupération des informations dans le formulaire
    if items_name != '' and items_name is not None:  # Recherche dans la barre
        evenement_object = Evenement.objects.filter(
            Q(title__icontains=items_name) |  # Recherche dans le titre de l'événement
            Q(category__name__icontains=items_name)  # Recherche dans le nom de la catégorie (discipline)
        )
    
    return render(request, 'index.html', {'evenement_object': evenement_object})