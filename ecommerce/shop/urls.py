from django.urls import path
from shop.views import index, detail, panier

urlpatterns = [
    path('', index, name ='home'), 
    path('<int:myid>/', detail, name='detail'),
    path('panier/', panier, name='panier'),
] 

