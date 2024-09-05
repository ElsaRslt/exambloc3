from django.urls import path, include
from shop.views import index, detail, panier, inscription
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', index, name ='home'), 
    
    path('<int:myid>/', detail, name='detail'),
    
    # URL pour le panier
    path('panier/', panier, name='panier'),
    
    # URL pour s'inscrire
    path('inscription/', views.inscription, name='inscription'),
    
    # URL pour se connecter
    path('connexion/', views.connexion, name='connexion'),
    
    # URL pour se deco
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
	# URL pour demander la réinitialisation du mot de passe
    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(template_name='mot_de_passe_oublie.html'), name='password_reset'),
    
    # URL pour confirmer l'envoi de l'email
    path('mot-de-passe-oublie/envoye/', auth_views.PasswordResetDoneView.as_view(template_name='mot_de_passe_envoye.html'), name='password_reset_done'),
    
    # URL pour la réinitialisation à partir du lien reçu par email
    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reinitialisation_mot_de_passe.html'), name='password_reset_confirm'),
    
    # URL pour confirmer que le mot de passe a bien été réinitialisé
    path('reinitialiser/complet/', auth_views.PasswordResetCompleteView.as_view(template_name='reinitialisation_complete.html'), name='password_reset_complete'),
]
    

