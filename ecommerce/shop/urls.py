from django.urls import path
from shop.views import index, detail, panier, inscription
from . import views

urlpatterns = [
    path('', index, name ='home'), 
    path('<int:myid>/', detail, name='detail'),
    path('panier/', panier, name='panier'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
] 

