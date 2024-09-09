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
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import letter
from PIL import Image

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

            # Récupérer l'événement depuis le panier
            first_event_key = list(panier.keys())[0]
            first_event_name = panier[first_event_key]['name']
            evenement = Evenement.objects.get(title=first_event_name)

            # Créer une nouvelle commande
            commande = Commande.objects.create(
                user=utilisateur,
                panier=panier_data,
                prix_total=total_prix,
            )

            # Générer le e-billet avec l'événement et l'utilisateur
            ebillet_path = generate_ebillet(utilisateur, commande, evenement)

            # Assigner le chemin du e-billet à la commande et sauvegarder
            commande.ebillet_path = ebillet_path
            commande.save()

            # Envoyer l'email de confirmation avec le billet PDF
            send_confirmation_email(utilisateur.email, ebillet_path)

            # Rediriger vers la page de confirmation de paiement
            return redirect('paiement')

    # Si la requête n'est pas POST, rediriger vers le panier
    return redirect('panier')



#generation du ebillet et du qrcode
def generate_ebillet(utilisateur, commande, evenement):
    # Chemin pour enregistrer le PDF
    pdf_filename = f"ebillet_{commande.numero_commande}.pdf"
    ebillet_path = os.path.join(settings.MEDIA_ROOT, 'ebillets', pdf_filename)

    # Générer un buffer pour le PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Ajouter le texte au PDF
    c.setFont("Helvetica", 16)
    c.drawString(100, 800, "Votre E-Billet")
    c.setFont("Helvetica", 12)
    c.drawString(100, 780, f"Nom de l'événement : {evenement.title}")
    c.drawString(100, 760, f"Date de l'événement : {evenement.date_event.strftime('%d %b %Y %H:%M')}")
    c.drawString(100, 740, f"Nom de l'acheteur : {utilisateur.nom} {utilisateur.prenom}")
    c.drawString(100, 720, f"Commande n° : {commande.numero_commande}")
    c.drawString(100, 700, f"Prix : {commande.prix_total} €")

    # Générer le QR code
    data = f"{utilisateur.cle_securite}-{commande.cle_securite_commande}"
    qr = qrcode.make(data)
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f"qr_{commande.numero_commande}.png")
    qr.save(qr_path)

    # Ajouter le QR code au PDF
    c.drawImage(qr_path, 100, 600, width=100, height=100)

    # Finaliser et sauvegarder le PDF
    c.showPage()
    c.save()

    # Enregistrer le PDF dans un fichier
    with open(ebillet_path, 'wb') as f:
        f.write(buffer.getvalue())

    return ebillet_path




#expédition du mail avec le ebillet
def send_confirmation_email(user_email, ebillet_path):
    email = EmailMessage(
        'Confirmation de commande avec E-Billet',
        'Merci pour votre commande. Veuillez trouver votre e-billet en pièce jointe.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )

    # Attacher le fichier PDF
    with open(ebillet_path, 'rb') as f:
        email.attach('ebillet.pdf', f.read(), 'application/pdf')

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
    
def get_event_date(event_title):
    try:
        event = Evenement.objects.get(title=event_title)
        return event.date_event.strftime("%d %b %Y")  # Format de la date
    except Evenement.DoesNotExist:
        return "Date inconnue"