import json
from django import template

register = template.Library()

@register.filter
def get_event_names(panier_str):
    try:
        # Désérialisation du panier
        panier = json.loads(panier_str)
        
        # Récupération des noms d'événements
        event_names = [details.get('name') for details in panier.values()]
        
        return ", ".join(event_names)
    except (json.JSONDecodeError, AttributeError, TypeError):
        return ""