"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from shop import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # La page d'accueil
    path('panier/', views.panier, name='panier'),  # Ajouter une route pour le panier
    path('evenement/<int:myid>/', views.detail, name='detail'),  # Ajouter une route pour le détail de l'événement
    path('shop/', include('shop.urls')),
    path('inscription/', views.inscription, name='inscription'),# Ajouter une route pour la page d'inscription
    path('connexion/', views.connexion, name='connexion'),# Ajouter une route pour la page de connexion
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)