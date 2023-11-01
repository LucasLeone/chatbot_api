from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChatbotConfig(AppConfig):
    name = "chatbot_api.chatbot"
    verbose_name = _("Chatbot")

    def ready(self):
        try:
            import chatbot_api.chatbot.signals  # noqa: F401
        except ImportError:
            pass
