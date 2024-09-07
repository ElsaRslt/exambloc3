from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from.models import Utilisateur
from django.utils.translation import gettext_lazy as _  # Pour rendre les messages traduisibles

class InscriptionForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'password1', 'password2']
        labels = {
            'nom':'Nom',
            'prenom': 'Prénom',
            'email': 'Email',
            'password1': 'Mot de passe',
            'password2': 'Confirmation du mot de passe',
        }
    """    widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmation du mot de passe'}),
        } """

    def save(self, commit=True):
        user = super().save(commit=commit)
        return user

        
        