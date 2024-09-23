from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.utils.timezone import now

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active) +
            six.text_type(user.password)  # Inclure le mot de passe pour plus de sécurité
        )

    def token_expired(self, timestamp):
        # Vérifie si le token est plus vieux que 10 minutes (600 secondes)
        return (now().timestamp() - timestamp) > 600  # 600 secondes = 10 minutes
        

account_activation_token = EmailVerificationTokenGenerator()