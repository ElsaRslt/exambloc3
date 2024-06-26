from django.shortcuts import render
from .models import Evenement


#fonction qui va permettre d'afficher le fichier index et les images
def index(request):
    evenement_object =Evenement.objects.all() #selection de tous les evenements qui sont dans la BDD 
    #fonction pour faire la recherche via la barre de recherche
    items_name = request.GET.get('items-name') #recuperation des informations dans le formulaire 
    if items_name !='' and items_name is not None: #recherche sur le mon de l'évenement 
        evenement_object = Evenement.objects.filter(title__icontains=items_name) # va contenir une partie du mot pour l'afficher 
    return render(request, 'index.html', {'evenement_object': evenement_object})
