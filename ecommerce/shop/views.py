from django.shortcuts import render


#fonction qui va permettre d'afficher le fichier index 
def index(request):
    return render(request, 'index.html')
