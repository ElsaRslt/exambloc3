from django.urls import path, include
import views 
from django.contrib.auth import views as auth_views
from django.urls import path
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.index, name ='home'), 
    
    path('<int:myid>/', views.detail, name='detail'),
    
    # URL pour le panier
    path('panier/', views.panier, name='panier'),
    
    # URL pour la page évenements
    path('evenements/', views.evenements, name='evenements'),
    
    # URL pour la page sports
    path('sports/', views.sports, name='sports'),
    
        # URL pour la page formules
    path('formules/', views.formules, name='formules'),

    # URL pour s'inscrire
    path('inscription/', views.inscription, name='inscription'),
    
    # URL pour se connecter
    path('connexion/', views.connexion, name='connexion'),
    
    # URL pour se deco
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    

    # si le client n'est pas connecté
    path('proceder-au-paiement/', views.proceder_au_paiement, name='proceder_au_paiement'),
    
	# # URL pour demander la réinitialisation du mot de passe
    # path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(template_name='mot_de_passe_oublie.html'), name='password_reset'),
    
    # URL pour confirmer l'envoi de l'email
    path('mot-de-passe-oublie/envoye/', auth_views.PasswordResetDoneView.as_view(template_name='mot_de_passe_envoye.html'), name='password_reset_done'),
    
    # URL pour la réinitialisation à partir du lien reçu par email
    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reinitialisation_mot_de_passe.html'), name='password_reset_confirm'),
    
    # URL pour confirmer que le mot de passe a bien été réinitialisé
    path('reinitialiser/complet/', auth_views.PasswordResetCompleteView.as_view(template_name='reinitialisation_complete.html'), name='password_reset_complete'),
    
    #personnalisation du mail de réinitialisation du MDP 
    path('mot-de-passe-oublie/',auth_views.PasswordResetView.as_view(template_name='mot_de_passe_oublie.html', email_template_name='password_reset_email.html'),name='password_reset'),
    
    # URL pour la page commande
    path('commandes/', views.commandes, name='commandes'),
    
    # URL pour la page paiement
    path('paiement/', views.paiement, name='paiement'),
    
    path('telecharger-ebillet/<int:commande_id>/', views.telecharger_ebillet, name='telecharger_ebillet'),
    
    # URL pour la page mock_paiement
    path('mock_paiement/', views.mock_paiement, name='mock_paiement')

    
]

    
