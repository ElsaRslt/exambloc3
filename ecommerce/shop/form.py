from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from.models import Utilisateur


class CustomUserCreationForm(UserCreationForm):
    nom = forms.CharField(label="Nom", max_length=50)
    prenom = forms.CharField(label="Prénom", max_length=50)
    Email = forms.EmailField(label="Email")
    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'Email', 'password1', 'password2']
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'Email': 'Email',
            'password1': 'Mot de passe',
            'password2': 'Confirmation du mot de passe',
        }
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'Email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmation du mot de passe'}),
        }

        
        
        
        