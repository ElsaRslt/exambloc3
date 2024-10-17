from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.timezone import now
from datetime import timedelta
import json
import qrcode
import os
from io import BytesIO
from zipfile import ZipFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from datetime import timedelta
import tempfile

from ecommerce.models import Evenement, Formule, Commande, Utilisateur, Discipline
from .form import InscriptionForm
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.core.files.storage import default_storage
import boto3
from django.core.files.base import ContentFile
from django.core.files import File
from botocore.exceptions import NoCredentialsError



# Fonction pour afficher les évenements sur la page 
def evenements(request):
    evenement_object = Evenement.objects.all()
    
    # Récupération de l'ID du sport depuis les paramètres de la requête
    sport_id = request.GET.get('sport')
    sport_name = None  # Variable pour stocker le nom du sport
    if sport_id:
        evenement_object = evenement_object.filter(category_id=sport_id)
        # Récupération du nom du sport
        sport_name = Discipline.objects.get(id=sport_id).name

    items_name = request.GET.get('items-name')
    if items_name != '' and items_name is not None:
        evenement_object = evenement_object.filter(
            Q(title__icontains=items_name) |
            Q(category__name__icontains=items_name)
        )
        
    paginator = Paginator(evenement_object, 15)
    page = request.GET.get('page')
    evenement_object = paginator.get_page(page)

    return render(request, 'evenements.html', {
        'evenement_object': evenement_object,
        'sport_name': sport_name,  # Passer le nom du sport au template
    })


#fonction pour afficher le detail des evenements quand on clique sur le bouton detail
def detail(request, myid):
    event = get_object_or_404(Evenement, id=myid)
    return render(request, 'detail.html', {'event': event})
    
    
# Fonction pour afficher la page du panier
def panier(request):
    panier = request.session.get('panier', {})
    return render(request, 'panier.html', {'panier': panier})

# Fonction pour afficher la page principale
def index(request):
    return render(request, 'index.html')

# Fonction pour afficher la page sport
def sports(request):
    sports_object = Discipline.objects.all()  # Sélection de tous les sports qui sont dans la BDD
        
    # Fonction pour faire la recherche via la barre de recherche
    items_name = request.GET.get('items-name')  # Récupération des informations dans le formulaire
    if items_name != '' and items_name is not None:  # Recherche dans la barre
        sports_object = Discipline.objects.filter(
            Q(name__icontains=items_name) # Recherche dans le nom du sport
            )
            
    #mise en place de la pagination    
    paginator = Paginator( sports_object,15) # on veut 15 sports par page
    page = request.GET.get('page')
    sports_object = paginator.get_page(page)
    return render(request, 'sports.html', {'sports_object': sports_object})


# Fonction pour afficher la page formules
def formules(request):
    formule_object=Formule.objects.all()
    return render(request, 'formules.html', {'formule_object': formule_object})

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
    
    # Enregistrez le timestamp de l'envoi
    request.session['email_sent_time'] = now().timestamp()
    
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

        if token_is_valid :
            print("le token est ok")
            email_sent_time = request.session.get('email_sent_time')
            if email_sent_time and not account_activation_token.token_expired(email_sent_time):
                user.is_active = True
                user.email_verified = True  # Mettre à jour le champ email_verified
                user.save()
                login(request, user)
                return redirect('home')
            else:
                print("Le token a expiré.")
                return render(request, 'token_expired.html')  # Afficher un message d'expiration
        else:
            print("Utilisateur non trouvé.")
            return render(request, 'email_invalid.html')  # Afficher un message d'email invalide
    else:
        print("Utilisateur non trouvé.")
        return render(request, 'email_invalid.html')
    
    
    
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

    for commande in commandes:
        commande.evenement_formule_pairs = []

        # Récupérer les données du panier en JSON pour associer événements et formules
        panier_data_dict = json.loads(commande.panier)  # Assurez-vous que le format JSON est correct

        for key, item in panier_data_dict.items():
            if not isinstance(item, dict):
                continue
            try:
                formule_name = item.get('formule')
                evenement_id = item.get('ID')
                quantity = item.get('quantity', 1)

                if not formule_name or not evenement_id:
                    continue

                # Récupérer la formule et l'événement
                formule = Formule.objects.get(formule=formule_name)
                evenement = Evenement.objects.get(id=int(evenement_id))

                # Ajouter les paires à la liste
                for _ in range(quantity):
                    commande.evenement_formule_pairs.append((evenement, formule))

            except (Formule.DoesNotExist, Evenement.DoesNotExist):
                continue

    return render(request, 'commandes.html', {'commandes': commandes})




    return render(request, 'commandes.html', {'commandes': commandes})
# Fonction pour afficher la page du paiement
def paiement(request):
    return render(request, 'paiement.html')

# Fonction pour afficher la page du paiement
def mock_paiement(request):
    if request.method == 'POST':
        panier_data = request.POST.get('panier_data')  # Récupérer les données du panier
        total_prix = request.POST.get('total_prix')  # Récupérer le total du panier

        # Si le panier est envoyé sous forme de JSON, on le charge comme dictionnaire
        if panier_data:
            panier_data = json.loads(panier_data)

        # Rendre la page avec les données du panier et le total
        return render(request, 'mock_paiement.html', {
            'panier_data': panier_data,
            'total_prix': total_prix
        })

    return render(request, 'mock_paiement.html')

@login_required
def proceder_au_paiement(request):
    if request.method == 'POST':
        panier_data = request.POST.get('panier_data')
        total_prix = request.POST.get('total_prix')
        utilisateur = request.user

        print(f"Panier Data: {panier_data}")
        print(f"Total Prix: {total_prix}")
        print(f"Utilisateur: {utilisateur}")

        try:
            panier_data_dict = json.loads(panier_data)
            print(f"Structure du panier: {panier_data_dict}")
            print(f"Panier Data (raw): {panier_data}")
        except json.JSONDecodeError:
            print("Erreur de décodage JSON pour le panier_data")
            return redirect('erreur_page')

        commande = Commande(
            user=utilisateur,
            panier=panier_data,
            prix_total=total_prix
        )
        commande.save()
        print(f"Commande créée avec numéro: {commande.numero_commande}")

        ebillet_paths = []
        
        formules = set()
        evenements = set()
        
        for key, item in panier_data_dict.items():
            print(f"Key: {key}, Contenu du panier (type: {type(item)}): {item}")
            if not isinstance(item, dict):
                print(f"Erreur : item {key} n'est pas un dictionnaire. Type: {type(item)}")
                continue
            try:
                formule_name = item.get('formule')
                evenement_id = item.get('ID')
                quantity = item.get('quantity', 1)  

                if not formule_name or not evenement_id:
                    print(f"Erreur: formule_name ou evenement_id manquant pour item {key}")
                    continue

                # Récupérer la formule avec le nom
                formule = Formule.objects.get(formule=formule_name)
                evenement = Evenement.objects.get(id=int(evenement_id))

                print(f"Récupération réussie - Formule: {formule.formule}, Evénement: {evenement.title}")

                for _ in range(quantity):
                    ebillet_path = generate_ebillet(utilisateur, commande, evenement, formule)
                    ebillet_paths.append(ebillet_path)
                    
                # Ajouter la formule et l'événement à la commande autant de fois que nécessaire
                formules.update([formule] * quantity)
                evenements.update([evenement] * quantity)
                
            except (Formule.DoesNotExist, Evenement.DoesNotExist):
                print(f"Erreur pour item {key}: Formule ou événement non trouvé")
                continue

        
        commande.formules.set(formules)
        commande.evenements.set(evenements)

        commande.ebillet_path = ";".join(ebillet_paths)
        commande.save()

        user_email = request.user.email
        send_confirmation_email(user_email, ebillet_paths)
        print("Email envoyé")

        return redirect('paiement')
    
    return redirect('panier')


def generate_ebillet(utilisateur, commande, evenement, formule):
    # Chemin pour enregistrer le PDF
    pdf_filename = f"ebillet_{commande.numero_commande}_{evenement.title.replace(' ', '_')}_{formule.formule.replace(' ', '_')}.pdf"
    s3_pdf_path = f"ebillets/{pdf_filename}"
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

    # Générer le QR code spécifique à cet événement
    data = f"{utilisateur.cle_securite}-{commande.cle_securite_commande}-{evenement.title}-{evenement.date_event}-{formule.formule}"
    qr = qrcode.make(data)
    # Enregistrer le QR code dans un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_qr_file:
        qr.save(tmp_qr_file, format='PNG')
        qr_file_path = tmp_qr_file.name

    # Ajouter le QR code au PDF
    c.drawImage(qr_file_path, 100, 600, width=100, height=100)

    # Finaliser et sauvegarder le PDF
    c.showPage()
    c.save()

    # Enregistrer le PDF dans S3
    with default_storage.open(s3_pdf_path, 'wb') as s3_file:
        s3_file.write(buffer.getvalue())

    print("E-billet enregistré sur S3 à :", s3_pdf_path)

    return s3_pdf_path

#expédition du mail avec le ou les ebillets    
def send_confirmation_email(user_email, ebillet_paths):
    subject = 'Votre Confirmation de votre Commande'
    message = 'Merci pour votre commande. Veuillez trouver en pièce jointe vos e-billets. Le service commercial des JO Paris 2024'
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
    print('email ok')

    # Initialise le client S3
    s3_client = boto3.client('s3',
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                            region_name=settings.AWS_S3_REGION_NAME)

    # Ajouter les e-billets en tant que pièces jointes
    for ebillet_path in ebillet_paths:
        try:
            # Télécharger l'e-billet depuis S3
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            response = s3_client.get_object(Bucket=bucket_name, Key=ebillet_path)
            file_content = response['Body'].read()

            # Attacher l'e-billet à l'e-mail
            email.attach(ebillet_path.split('/')[-1], file_content, 'application/pdf')
            print(f"E-billet {ebillet_path} rattaché")

        except NoCredentialsError:
            print(f"Erreur lors du téléchargement ou de l'attachement de {ebillet_path}: Unable to locate credentials")
        except Exception as e:
            print(f"Erreur lors du téléchargement ou de l'attachement de {ebillet_path}: {str(e)}")
    
    # Envoyer l'e-mail
    email.send()
    print('ok fin du mail')

    
@login_required
def telecharger_ebillet(request, commande_id):
    try:
        # Récupérer la commande pour l'utilisateur actuel
        print(f"Recherche de la commande avec ID: {commande_id} pour l'utilisateur: {request.user}")
        commande = Commande.objects.get(id=commande_id, user=request.user)
        print(f"Commande trouvée: {commande}")
        print(f"ebillet_path brut: {commande.ebillet_path}")

        # Séparer les différents chemins d'ebillets
        ebillet_paths = commande.ebillet_path.split(";")

        # Création du fichier ZIP en mémoire
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for ebillet_path in ebillet_paths:
                ebillet_path = ebillet_path.strip()  # Nettoyer les espaces
                try:
                    # Générer l'URL du fichier dans S3
                    file_url = default_storage.url(ebillet_path)
                    print(f"E-billet {ebillet_path} rattaché avec URL: {file_url}")

                    # Ouvrir le fichier via l'URL (S3)
                    with default_storage.open(ebillet_path, 'rb') as ebillet_file:
                        # Ajouter le fichier au zip
                        zip_file.writestr(os.path.basename(ebillet_path), ebillet_file.read())
                except Exception as e:
                    print(f"Erreur: {str(e)}")
                    return HttpResponse(f"Fichier non trouvé dans S3 : {ebillet_path}", status=404)

        # Finaliser le fichier zip et l'envoyer dans la réponse
        zip_buffer.seek(0)
        response = FileResponse(zip_buffer, as_attachment=True, filename=f"ebillets_{commande.numero_commande}.zip")
        
        return response

    except Commande.DoesNotExist:
        return HttpResponse('Commande introuvable.', status=404)
    except Exception as e:
        return HttpResponse(f'Erreur lors du téléchargement des e-billets: {str(e)}', status=500)
    
    
    
# afficher les informations dans le compte client 
@login_required
def profil(request):
    utilisateur = request.user  # Récupère l'utilisateur connecté
    context = {
        'nom': utilisateur.nom,
        'prenom': utilisateur.prenom,
        'email': utilisateur.email,
        'password': '*' * 8,  # Masquer le mot de passe avec 8 étoiles
    }
    return render(request, 'profil.html', context)