"""Chatbot URLs."""

# Django
from django.urls import path

# Views
from chatbot_api.chatbot.views import ChatbotView

app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotView.as_view(), name='chatbot'),
]
