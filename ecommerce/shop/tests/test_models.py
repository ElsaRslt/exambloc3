# shop/tests/test_models.py
import pytest
from shop.models import Evenement

@pytest.mark.django_db
def test_evenement_creation():
    evenement = Evenement.objects.create(title="Test Event", description="Just a test")
    assert evenement.title == "Test Event"
    assert evenement.description == "Just a test"