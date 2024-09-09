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
from django.http import HttpResponse

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
    commandes = Commande.objects.filter(user=request.user).order_by('-date_commande')
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

            # Créer une nouvelle commande
            commande = Commande.objects.create(
                user=utilisateur,
                panier=panier_data,
                prix_total=total_prix,
            )

            ebillet_paths = []

            # Générer un e-billet pour chaque événement dans le panier
            for event_key, event_info in panier.items():
                event_name = event_info['name']
                formule_name = event_info['formule']
                # event_price = event_info['price']

                # Récupérer l'événement correspondant
                evenement = Evenement.objects.get(title=event_name)

                # Générer le e-billet pour cet événement
                ebillet_path = generate_ebillet(utilisateur, commande, evenement, formule_name ) #event_price
                ebillet_paths.append(ebillet_path)

            # Sauvegarder le chemin des e-billets générés dans la commande
            commande.ebillet_path = json.dumps(ebillet_paths)  # Sauvegarder tous les chemins de e-billet sous forme de JSON
            commande.save()

            # Envoyer l'email de confirmation avec tous les billets en pièce jointe
            send_confirmation_email(utilisateur.email, ebillet_paths)

            # Rediriger vers la page de confirmation de paiement
            return redirect('paiement')

    # Si la requête n'est pas POST, rediriger vers le panier
    return redirect('panier')



def generate_ebillet(utilisateur, commande, evenement, formule_name):#, event_price
    # Chemin pour enregistrer le PDF
    pdf_filename = f"ebillet_{commande.numero_commande}_{evenement.title}.pdf"
    ebillet_path = os.path.join(settings.MEDIA_ROOT, 'ebillets', pdf_filename)

    # Générer un buffer pour le PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Ajouter le texte au PDF
    c.setFont("Helvetica", 16)
    c.drawString(100, 800, "Votre E-Billet")
    c.setFont("Helvetica", 12)
    c.drawString(100, 780, f"Nom de l'événement : {evenement.title}")
    c.drawString(100, 760, f"Formule : {formule_name}")
    c.drawString(100, 740, f"Date de l'événement : {evenement.date_event.strftime('%d %b %Y %H:%M')}")
    c.drawString(100, 720, f"Nom de l'acheteur : {utilisateur.nom} {utilisateur.prenom}")
    c.drawString(100, 700, f"Commande n° : {commande.numero_commande}")
    # c.drawString(100, 680, f"Prix : {event_price} €")

    # Générer le QR code spécifique à cet événement
    data = f"{utilisateur.cle_securite}-{commande.cle_securite_commande}-{evenement.title}-{evenement.date_event}"
    qr = qrcode.make(data)
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f"qr_{commande.numero_commande}_{evenement.title}.png")
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




#expédition du mail avec le ou les ebillets
def send_confirmation_email(user_email, ebillet_paths):
    email = EmailMessage(
        'Confirmation de commande avec E-Billet',
        'Merci pour votre commande. Veuillez trouver vos e-billets en pièce jointe.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )

    # Attacher chaque e-billet au mail
    for ebillet_path in ebillet_paths:
        with open(ebillet_path, 'rb') as f:
            email.attach(f"ebillet_{os.path.basename(ebillet_path)}", f.read(), 'application/pdf')

    email.send()
    
    
@login_required
def telecharger_ebillet(request, commande_id):
    try:
        # Récupérer la commande
        commande = Commande.objects.get(id=commande_id, user=request.user)
        
        # Récupérer les chemins des fichiers e-billets (sous forme de liste JSON)
        ebillet_paths = json.loads(commande.ebillet_path)
        
        # Préparer une réponse pour le téléchargement de plusieurs fichiers
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="ebillets_{commande.numero_commande}.zip"'

        # Créer un fichier zip pour les e-billets
        from zipfile import ZipFile
        from io import BytesIO

        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for ebillet_path in ebillet_paths:
                # Ajouter chaque e-billet au fichier zip
                if os.path.exists(ebillet_path):
                    zip_file.write(ebillet_path, os.path.basename(ebillet_path))
        
        # Finaliser le fichier zip
        zip_buffer.seek(0)
        response.write(zip_buffer.getvalue())
        
        return response
    except Commande.DoesNotExist:
        return HttpResponse('Commande introuvable.', status=404)
    except Exception as e:
        return HttpResponse(f'Erreur lors du téléchargement des e-billets: {str(e)}', status=500)