from django.shortcuts import render
from .models import Evenement


#fonction qui va permettre d'afficher le fichier index et les images
def index(request):
    product_object =Evenement.objects.all() #selection de tous les evenements qui sont dans la BDD
    return render(request, 'index.html', {'product_object': product_object})
