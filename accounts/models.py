from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom user model that extends the default User model."""
    email = models.EmailField(_('email address'), unique=True)
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('standard', 'Standard'),
            ('premium', 'Premium'),
        ],
        default='basic'
    )
    subscription_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
