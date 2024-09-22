from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import os
import shutil
import tempfile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.timezone import now, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from ecommerce.tokens import account_activation_token

from ecommerce.models import Evenement, Formule, Commande, Discipline

class ViewsTestCase(TestCase):
    
    @override_settings(MEDIA_ROOT='/tmp/test_media')
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.media_root = tempfile.mkdtemp()
        self.image = SimpleUploadedFile(name='test_image.png', content=b'fake image content', content_type='image/png')
        os.makedirs(os.path.join(self.media_root, 'sport_images'), exist_ok=True)
        self.discipline = Discipline.objects.create(name='Test Discipline', description='Description of Test Discipline', image=self.image)
        self.event = Evenement.objects.create(title='Test Event', date_event='2023-12-12', category=self.discipline, image=self.image)
        self.formule = Formule.objects.create(formule='Test Formule', price_multiplier=1.5, description='Description of Test Formule')
        self.commande = Commande.objects.create(user=self.user, prix_total=100, numero_commande='12345')
        self.commande.ebillet_path = json.dumps(['path/to/ebillet1.pdf', 'path/to/ebillet2.pdf'])
        self.commande.save()
        self.token_id = account_activation_token.make_token(self.user)

    def tearDown(self):
        # Nettoyage du répertoire temporaire de médias
        if os.path.isdir(self.media_root):
            shutil.rmtree(self.media_root)

    def test_image_upload(self):
        discipline = Discipline.objects.create(
            name='Test Discipline',
            description='Description of Test Discipline',
            image=self.image
        )
        self.assertTrue(discipline.image)
        self.assertTrue(discipline.image.name.startswith('sport_images/test_image'))

    def test_evenements_view(self):
        response = self.client.get(reverse('evenements'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'evenements.html')

    def test_detail_view(self):
        response = self.client.get(reverse('detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')

    def test_panier_view(self):
        response = self.client.get(reverse('panier'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panier.html')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_sports_view(self):
        response = self.client.get(reverse('sports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sports.html')

    def test_formules_view(self):
        response = self.client.get(reverse('formules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formules.html')

    def test_inscription_view(self):
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inscription.html')

    def test_envoyer_email_confirmation(self):
        response = self.client.get(reverse('renvoyer_email_confirmation'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'renvoyer_email.html')

    def test_connexion_view(self):
        response = self.client.get(reverse('connexion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'connexion.html')

    def test_deconnexion_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('deconnexion'))
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion

    def test_proceder_au_paiement(self):
        self.client.login(username='testuser', password='testpassword')
        panier_data = {
            '1': {'formule': 'Test Formule', 'ID': str(self.event.id), 'quantity': 2}
        }
        response = self.client.post(reverse('proceder_au_paiement'), {
            'panier_data': json.dumps(panier_data),
            'total_prix': 100
        })
        self.assertEqual(response.status_code, 302)  # Redirection après paiement
    


    def test_deconnexion_redirection(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('deconnexion'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        
    def test_proceder_au_paiement_invalid_json(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('proceder_au_paiement'), {
            'panier_data': 'invalidjson',
            'total_prix': 100
        })
        self.assertEqual(response.status_code, 302)  # Redirection en cas d'erreur

        
    def test_valider_email_invalid_token(self):
        token = account_activation_token.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        invalid_token = 'invalidtoken'
        
        response = self.client.get(reverse('valider_email', args=[uid, invalid_token]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_invalid.html')
        

        
    def test_telecharger_ebillet(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('telecharger_ebillet', args=[self.commande.id]), {'csrfmiddlewaretoken': 'testtoken'})
        self.assertEqual(response.status_code, 302)
        print(response['Location'])  # Affiche l'URL de redirection
