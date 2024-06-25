from django.shortcuts import render
from .models import Evenement


#fonction qui va permettre d'afficher le fichier index et les images
def index(request):
    evenement_object =Evenement.objects.all() #selection de tous les evenements qui sont dans la BDD
    return render(request, 'index.html', {'evenement_object': evenement_object})
