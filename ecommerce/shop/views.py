from django.shortcuts import render, redirect
from .models import Evenement, Formule, Commande
from django.db.models import Q  # Import de l'opérateur Q pour les requêtes complexes
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserCreationForm 
from .form import InscriptionForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
import os
from django.http import FileResponse, Http404

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
            'name': evenement_object.title,
            'formule': formule.formule,
            'price': evenement_object.base_price * formule.price_multiplier
        }
        for formule in formules
    ]

    if request.method == 'POST':
        formule_id = request.POST.get('formule')
        formule = get_object_or_404(Formule, id=formule_id)
        formule_name = formule.formule
        panier = request.session.get('panier', {})
        panier_key = f"{myid}_{formule_name}"
        if panier_key not in panier:
            panier[panier_key] = {
                'name': evenement_object.title,
                'formule': formule_name,
                'price': evenement_object.base_price * formule.price_multiplier,
                'quantity': 1
            }
        else:
            panier[panier_key]['quantity'] += 1
        request.session['panier'] = panier

    return render(request, 'detail.html', {
        'evenement_object': evenement_object,
        'formules_with_prices': formules_with_prices
    })
    
    
# Fonction pour afficher la page du panier
def panier(request):
    panier = request.session.get('panier', {})
    return render(request, 'panier.html', {'panier': panier})

""" # Fonction pour afficher la page d'inscription
def inscription(request):
    return render(request, 'inscription.html') """

""" # Fonction pour afficher la page de connexion
def connexion(request):
    return render(request, 'connexion.html') """

# Formulaire d'inscription avec InscriptionForm
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')  # Redirection après la création du compte
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})

#connexion à son espace 
def connexion(request):
    if request.method == 'POST':
        username = request.POST['username'] #récuperation du username avec methode post
        password = request.POST['password'] #récuperation du mdp avec methode post
        user = authenticate(request, username=username, password=password) # vérification que tout colle avec tout 
        if user is not None: # si ok connexion
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.') # si pas ok adieu 
    return render(request, 'connexion.html')

# #deconnexion de son compte
def deconnexion(request):
    logout(request)
    return redirect('home')  # Redirection vers la page d'accueil après déconnexion

#recuperation nom et prenom pour espace perso 
@login_required
def home(request):
    user = request.user
    return render(request, 'home.html', {
        'prenom': user.prenom,
        'nom': user.nom,
    })
    

# Fonction pour afficher la page des commandes et les commandes dans la page commandes
def commandes(request):
    commandes = Commande.objects.filter(user=request.user)
    return render(request, 'commandes.html', {'commandes': commandes})

# Fonction pour afficher la page du paiement
def paiement(request):
    return render(request, 'paiement.html')

@login_required
def proceder_au_paiement(request):
    if request.method == 'POST':
        panier_data = request.POST.get('panier_data')
        total_prix = request.POST.get('total_prix')

        if panier_data:
            panier = json.loads(panier_data)
            utilisateur = request.user

            # Crée une nouvelle commande
            commande = Commande.objects.create(
                user=utilisateur,
                panier=panier_data,
                prix_total=total_prix,
            )

            # Générer le QR code et l'enregistrer comme e-billet
            qr_code_path = generate_qr_code(utilisateur, commande)

            # Assigner le chemin de l'e-billet à la commande et sauvegarder
            commande.ebillet_path = qr_code_path
            commande.save()

            # Envoyer l'e-mail de confirmation avec le chemin du QR code
            send_confirmation_email(utilisateur.email, qr_code_path)

            # Redirige vers la page de confirmation de paiement
            return redirect('paiement')

    # Si la requête n'est pas POST, rediriger vers le panier
    return redirect('panier')

# generation du qrcode pour le ebillet
def generate_qr_code(utilisateur, commande):
    # Combinaison de la clé de sécurité de l'utilisateur et de la commande
    data = f"{utilisateur.cle_securite}-{commande.cle_securite_commande}"

    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Créer une image QR
    img = qr.make_image(fill='black', back_color='white')

    # Chemin où enregistrer l'image
    qr_code_filename = f"qr_code_{commande.numero_commande}.png"
    qr_code_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_code_filename)

    # S'assurer que le dossier existe
    os.makedirs(os.path.dirname(qr_code_path), exist_ok=True)

    # Sauvegarder l'image QR code
    img.save(qr_code_path)

    # Log pour vérifier le chemin
    print(f"QR code path: {qr_code_path}")

    return qr_code_path


#expédition du mail avec le qrcode qui fait office de ebillet
def send_confirmation_email(user_email, qr_code_path):
    # Construire l'email
    email = EmailMessage(
        'Confirmation de commande',
        'Merci pour votre commande. Veuillez trouver votre e-billet en pièce jointe.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )

    # Ajouter le QR code en pièce jointe
    with open(qr_code_path, 'rb') as f:
        email.attach('ebillet.png', f.read(), 'image/png')

    # Envoyer l'email
    email.send()
    
    
@login_required
def telecharger_ebillet(request, commande_id):
    try:
        # Récupérer la commande
        commande = Commande.objects.get(id=commande_id, user=request.user)
        
        # Récupérer le chemin du fichier e-billet (QR code)
        ebillet_path = commande.ebillet_path
        
        # Ouvrir le fichier e-billet en mode binaire
        if ebillet_path and os.path.exists(ebillet_path):
            response = FileResponse(open(ebillet_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(ebillet_path)}"'
            return response
        else:
            # Si le fichier n'existe pas
            return HttpResponse('Le billet électronique est introuvable.', status=404)
    except Commande.DoesNotExist:
        return HttpResponse('Commande introuvable.', status=404)