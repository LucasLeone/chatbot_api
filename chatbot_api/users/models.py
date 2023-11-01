from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from chatbot_api.utils.models import ChatbotAPIModel
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Default custom user model for Chatbot API.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


CIUDADES = (
    ('Villa Maria', 'Villa Maria'),
    ('Villa Nueva', 'Villa Nueva'),
)


class UserWSP(ChatbotAPIModel):
    """User whatsapp model."""

    nombre = models.CharField(max_length=50, null=True, blank=True)
    celular_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message="El número debe ser en formato: +999999999. Hasta 15 digitos permitidos."
    )
    celular = models.CharField(validators=[celular_regex], max_length=17)
    direccion = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=25, null=True, blank=True, choices=CIUDADES)

    def __str__(self):
        """Return celular."""
        return self.celular
    
    class Meta:
        """Meta options."""

        verbose_name = 'Usuario de WhatsApp'
        verbose_name_plural = 'Usuarios de WhatsApp'