"""Chatbot views."""

# Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response

# Utils
from chatbot_api.chatbot import services, sett


class ChatbotView(APIView):
    """Chatbot view.
    
    That view have principal functions of the system.
        - get: verify token
        - post: recive message and send answer
    """

    def get(self, request):
        try:
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')
            if token == sett.token and challenge is not None:
                return Response(challenge)
            else:
                return Response('token incorrecto', status=403)
        except Exception as e:
            return Response(str(e), status=403)

    def post(self, request):
        try:
            body = request.data
            entry = body['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            message = value['messages'][0]
            number = services.replace_start(message['from'])
            messageId = message['id']
            contacts = value['contacts'][0]
            name = contacts['profile']['name']
            text = services.obtener_Mensaje_whatsapp(message)
            services.administrar_chatbot(text, number, messageId, name)
            return Response('enviado')
        except Exception as e:
            return Response('no enviado ' + str(e))