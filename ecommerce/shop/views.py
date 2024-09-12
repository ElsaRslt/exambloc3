from django.shortcuts import render, redirect
from .models import Evenement, Formule, Commande,  Utilisateur
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
from zipfile import ZipFile
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.timezone import now
from datetime import timedelta
from .tokens import account_activation_token
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


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
    event = get_object_or_404(Evenement, id=myid)
    return render(request, 'detail.html', {'event': event})
    
    
# Fonction pour afficher la page du panier
def panier(request):
    panier = request.session.get('panier', {})
    return render(request, 'panier.html', {'panier': panier})

# Fonction pour afficher la page pour renvoyer le mail pour validation mail utilisareur 
def renvoyer_email(request):
    return render(request, 'renvoyer_email.html')

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
            user = form.save(commit=False)
            #user.is_active = False   #Désactiver le compte avant validation
            user.save()
            print(user)
            envoyer_email_confirmation(user, request)  # Envoyer email de confirmation
            return render(request, 'email_sent.html')  # Page indiquant que l'email a été envoyé
    else:
        form = InscriptionForm()
    return render(request, 'inscription.html', {'form': form})


# envoyer un email pour validation du compte 
def envoyer_email_confirmation(user, request):
    current_site = get_current_site(request)
    subject = 'Confirmez votre adresse e-mail'
    message = render_to_string('email_confirmation.html', {
        'user': user,
        'domain': current_site.domain,
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
    subject,
    message,
    to=[user.email],
    from_email='noreply@example.com'
    )
    email.content_subtype = 'html' 
    email.send()
    
    
# gestion de la validité du mail 
def valider_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        print("UID décodé:", uid)
        user = get_object_or_404(Utilisateur, pk=uid)
    except (TypeError, ValueError, OverflowError) as e:
        print(f"Erreur de décodage UID: {e}")
        return render(request, 'email_invalid.html')

    if user is not None:
        # Vérifier la validité du token
        token_is_valid = account_activation_token.check_token(user, token)
        print(f"Token valide: {token_is_valid}")

        if token_is_valid:
            # Vérifier si le token a expiré (10 minutes)
            if now() - timedelta(minutes=10) < user.date_added:
                user.is_active = True
                user.email_verified = True  # Mettre à jour le champ email_verified
                user.save()
                login(request, user)
                return redirect('home')
            else:
                print("Le token a expiré.")
                return render(request, 'token_expired.html')  # Afficher un message d'expiration
        else:
            print("Token invalide.")
            return render(request, 'email_invalid.html')  # Afficher un message d'email invalide
    else:
        print("Utilisateur non trouvé.")
        return render(request, 'email_invalid.html')  # Afficher un message d'email invalide
    

#renvoyer le mail de validation 
def renvoyer_email_confirmation(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if not user.email_verified:
                envoyer_email_confirmation(user, request)
                return render(request, 'email_renvoi_confirmation.html')
        except User.DoesNotExist:
            messages.error(request, "L'utilisateur n'existe pas. Merci de creer votre compte")
    return render(request, 'renvoyer_email.html')
    
#connexion à son espace 
def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.email_verified:
                    if 'resend_email' in request.POST:
                        return redirect('renvoyer_email', uid=user.pk)
                    else:
                        messages.error(request, "Merci de valider votre adresse email avant de vous connecter.")
                elif not user.is_active:
                    messages.error(request, "Votre compte a été désactivé.")
                else:
                    login(request, user)
                    return redirect('home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, 'connexion.html', {'form': form})

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
        utilisateur = request.user

        print(f"Panier Data: {panier_data}")
        print(f"Total Prix: {total_prix}")
        print(f"utilisateur: {utilisateur }")
        
        # Convertir le panier_data en dictionnaire
        try:
            panier_data_dict = json.loads(panier_data)
        except json.JSONDecodeError:
            print("Erreur de décodage JSON pour le panier_data")
            return redirect('erreur_page')

        # Créez une nouvelle commande
        commande = Commande(
            user=utilisateur,
            panier=panier_data,
            prix_total=total_prix
        )
        commande.save()
        print(f"Commande créée avec numéro: {commande.numero_commande}")

        # Créez des e-billets pour chaque événement et mettez à jour la commande
        ebillet_paths = []
        
        formules = set()
        evenements = set()
        
        for item_id, item in panier_data_dict.items():
            try:
                formule = Formule.objects.get(formule=item.get('formule'))
                evenement = Evenement.objects.get(title=item.get('name'))
                print(f"ebillet ok etape 1")
                
                # Générer un e-billet unique pour chaque combinaison événement-formule
                ebillet_path = generate_ebillet(utilisateur, commande, evenement, formule)
                ebillet_paths.append(ebillet_path)
                
                formules.add(formule)
                evenements.add(evenement)
            except (Formule.DoesNotExist, Evenement.DoesNotExist):
                print(f"Erreur pour item {item_id}: formule ou événement non trouvé")
                continue
        
        # Ajouter les relations ManyToMany après avoir sauvegardé la commande
        commande.formules.set(formules)
        commande.evenements.set(evenements)

        # Sauvegarder le chemin des e-billets générés dans la commande
        commande.ebillet_path = json.dumps(ebillet_paths)  # Sauvegarder tous les chemins de e-billet sous forme de JSON
        commande.save()

        # Envoyer l'email de confirmation avec tous les billets en pièce jointe
        user_email = request.user.email
        send_confirmation_email(user_email, ebillet_paths)
        print("email envoyé")

        # Rediriger vers la page de confirmation de paiement
        return redirect('paiement')
    
    # Si la requête n'est pas POST, rediriger vers le panier
    return redirect('panier')




def generate_ebillet(utilisateur, commande, evenement, formule):#, event_price
    # Chemin pour enregistrer le PDF
    pdf_filename = f"ebillet_{commande.numero_commande}_{evenement.title}_{formule.formule}.pdf"
    ebillet_path = os.path.join(settings.MEDIA_ROOT, 'ebillets', pdf_filename)
    print(pdf_filename)

    # Générer un buffer pour le PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Ajouter le texte au PDF
    c.setFont("Helvetica", 16)
    c.drawString(100, 800, "Votre E-Billet")
    c.setFont("Helvetica", 12)
    c.drawString(100, 780, f"Nom de l'événement : {evenement.title}")
    c.drawString(100, 760, f"Formule : {formule.formule}")
    c.drawString(100, 740, f"Date de l'événement : {evenement.date_event.strftime('%d %b %Y %H:%M')}")
    c.drawString(100, 720, f"Nom de l'acheteur : {utilisateur.nom} {utilisateur.prenom}")
    c.drawString(100, 700, f"Commande n° : {commande.numero_commande}")
    # c.drawString(100, 680, f"Prix : {event_price} €")

    # Générer le QR code spécifique à cet événement
    data = f"{utilisateur.cle_securite}-{commande.cle_securite_commande}-{evenement.title}-{evenement.date_event}-{formule.formule}"
    qr = qrcode.make(data)
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', f"qr_{commande.numero_commande}_{evenement.title}_{formule.formule}.png")
    qr.save(qr_path)

    # Ajouter le QR code au PDF
    c.drawImage(qr_path, 100, 600, width=100, height=100)

    # Finaliser et sauvegarder le PDF
    c.showPage()
    c.save()

    # Enregistrer le PDF dans un fichier
    with open(ebillet_path, 'wb') as f:
        f.write(buffer.getvalue())
        print("ebillet enregistré")
        
    print("ebillet generé")

    return ebillet_path




#expédition du mail avec le ou les ebillets
""" def send_confirmation_email(user_email, ebillet_paths):
    email = EmailMessage(
        'Confirmation de commande avec E-Billet',
        'Merci pour votre commande. Veuillez trouver vos e-billets en pièce jointe.',
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        print('email ok')
    )

    # Attacher chaque e-billet au mail
    for path in ebillet_paths:
        with open(path, 'rb') as f:
            email.attach(f"ebillet_{os.path.basename(path)}", f.read(), 'application/pdf')
            print('ebillets rattachés')

    email.send() """
    
def send_confirmation_email(user_email, ebillet_paths):
    subject = 'Votre Confirmation de votre Commande'
    message = 'Merci pour votre commande. Veuillez trouver en pièce jointe vos e-billets. Le service commercial des JO Paris 2024'
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
    print('email ok')
    
    # Ajouter les e-billets en tant que pièces jointes
    for ebillet_path in ebillet_paths:
        email.attach_file(ebillet_path)
        print('ebillets rattachés')
    
    email.send()
    print('ok fin du mail')
    
    

    
@login_required
def telecharger_ebillet(request, commande_id):
    try:
        # Récupérer la commande
        commande = Commande.objects.get(id=commande_id, user=request.user)
        
        # Vérifier et corriger le format de ebillet_path
        try:
            ebillet_paths = json.loads(commande.ebillet_path)
            if not isinstance(ebillet_paths, list):
                raise ValueError("Le format des chemins des e-billets n'est pas une liste")
        except json.JSONDecodeError:
            return HttpResponse('Erreur de décodage JSON.', status=400)
        except ValueError as e:
            return HttpResponse(f'Erreur de format des données: {str(e)}', status=400)
        
        # Préparer une réponse pour le téléchargement de plusieurs fichiers
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="ebillets_{commande.numero_commande}.zip"'

        # Créer un fichier zip pour les e-billets
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for ebillet_path in ebillet_paths:
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