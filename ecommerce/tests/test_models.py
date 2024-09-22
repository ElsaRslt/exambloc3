from django.test import TestCase
from ecommerce.models import Discipline, Formule, Evenement, Commande, Utilisateur

class DisciplineModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.discipline = Discipline.objects.create(
            name='Test Discipline',
            description='This is a test discipline.',
            image='path/to/image.jpg',
        )
    
    def test_discipline_creation(self):
        self.assertEqual(self.discipline.name, 'Test Discipline')
        self.assertEqual(self.discipline.description, 'This is a test discipline.')
    
    def test_str_method(self):
        self.assertEqual(str(self.discipline), 'Test Discipline')


class FormuleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.formule = Formule.objects.create(
            formule='Test Formule',
            price_multiplier=1.5,
            description='This is a test formule.',
        )
    
    def test_formule_creation(self):
        self.assertEqual(self.formule.formule, 'Test Formule')
        self.assertEqual(self.formule.price_multiplier, 1.5)
        self.assertEqual(self.formule.description, 'This is a test formule.')

    def test_str_method(self):
        self.assertEqual(str(self.formule), 'Test Formule')


class EvenementModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.discipline = Discipline.objects.create(
            name='Test Discipline',
            description='This is a test discipline.',
            image='path/to/image.jpg',
        )
        cls.formule = Formule.objects.create(
            formule='Test Formule',
            price_multiplier=1.5,
            description='This is a test formule.',
        )
        cls.evenement = Evenement.objects.create(
            title='Test Evenement',
            description='This is a test evenement.',
            category=cls.discipline,  # Associe l'événement à la discipline
            date_event='2024-12-01 12:00:00',
            image='path/to/image.jpg',
            base_price=20.0,
        )
        cls.evenement.formules.add(cls.formule)

    def test_evenement_creation(self):
        self.assertEqual(self.evenement.title, 'Test Evenement')
        self.assertEqual(self.evenement.description, 'This is a test evenement.')
        self.assertEqual(self.evenement.category, self.discipline)
        self.assertEqual(self.evenement.base_price, 20.0)
        self.assertIn(self.formule, self.evenement.formules.all())
    
    def test_str_method(self):
        self.assertEqual(str(self.evenement), 'Test Evenement')


class CommandeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.discipline = Discipline.objects.create(
            name='Test Discipline',
            description='This is a test discipline.',
            image='path/to/image.jpg',
        )
        cls.formule = Formule.objects.create(
            formule='Test Formule',
            price_multiplier=1.5,
            description='This is a test formule.',
        )
        cls.evenement = Evenement.objects.create(
            title='Test Evenement',
            description='This is a test evenement.',
            category=cls.discipline,
            date_event='2024-12-01 12:00:00',
            image='path/to/image.jpg',
            base_price=20.0,
        )
        cls.evenement.formules.add(cls.formule)
        cls.user = Utilisateur.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
            nom='Test',
            prenom='User',
        )
        cls.commande = Commande.objects.create(
            user=cls.user,
            panier='{"items": [{"formule": "Test Formule", "quantity": 2}]}',
            prix_total=40.0,
            ebillet_path='path/to/ebillet.pdf',
            numero_commande='TEST123'  # Numéro de commande fixe
        )
        cls.commande.formules.add(cls.formule)
        cls.commande.evenements.add(cls.evenement)

    def test_commande_creation(self):
        self.assertEqual(self.commande.user, self.user)
        self.assertEqual(self.commande.prix_total, 40.0)
        self.assertIn(self.formule, self.commande.formules.all())
        self.assertIn(self.evenement, self.commande.evenements.all())
    
    def test_str_method(self):
        self.assertEqual(str(self.commande), f"Commande TEST123 - {self.user.username}")