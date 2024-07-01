from django.shortcuts import render
from .models import Evenement, Formule
from django.db.models import Q  # Import de l'opérateur Q pour les requêtes complexes
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

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
    #mise en place de la pagination    
    paginator = Paginator( evenement_object,4) # on veut 4 evenement par page
    page = request.GET.get('page')
    evenement_object = paginator.get_page(page)
    return render(request, 'index.html', {'evenement_object': evenement_object})


#fonction pour afficher le detail des evenements quand on clique sur le bouton detail
def detail(request, myid):
    evenement_object = get_object_or_404(Evenement, id=myid)
    formules = evenement_object.formules.all()
    formules_with_prices = [
        {
            'id': formule.id,
            'formule': formule.formule,
            'price': evenement_object.base_price * formule.price_multiplier
        }
        for formule in formules
    ]

    if request.method == 'POST':
        formule_id = request.POST.get('formule')
        formule = get_object_or_404(Formule, id=formule_id)
        panier = request.session.get('panier', {})
        if myid not in panier:
            panier[myid] = {
                'formule': formule.formule,
                'price': evenement_object.base_price * formule.price_multiplier,
                'quantity': 1
            }
        else:
            panier[myid]['quantity'] += 1
        request.session['panier'] = panier

    return render(request, 'detail.html', {
        'evenement_object': evenement_object,
        'formules_with_prices': formules_with_prices
    })
    
    
# Fonction pour afficher la page du panier
def panier(request):
    panier = request.session.get('panier', {})
    return render(request, 'panier.html', {'panier': panier})