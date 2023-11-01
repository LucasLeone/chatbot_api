import requests
from chatbot_api.chatbot import sett
import json
import time
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim


FARMACIAS = [
    {"name": "Farmacia Moderna Marcellino", "latitude": -32.408998531857854, "longitude": -63.256605205702186},
    {"name": "Farmacia Moderna Subnivel", "latitude": -32.413532723509945, "longitude": -63.24583211845355},
    {"name": "Farmacia Moderna II", "latitude": -32.40958736241506, "longitude": -63.24118811667923},
]


def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    elif typeMessage == 'location':
        user_latitude = str(message.get('location').get('latitude'))
        user_longitude = str(message.get('location').get('longitude'))
        text = user_latitude + ', ' + user_longitude + 'location'
    else:
        text = 'mensaje no procesado'
    
    
    return text
  
  
def get_coordinates(location):
    geolocator = Nominatim(user_agent="pharmacy_locator")
    location = geolocator.geocode(location)
    return location.latitude, location.longitude



def calculate_distance(client_coords, farmacia_coords):
    lat1, lon1 = map(radians, client_coords)
    lat2, lon2 = map(radians, farmacia_coords)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    radius = 6371

    distance = radius * c
    return distance

def encontrar(user_location, farmacias, max_distance=6000):
    farmacias_cercas = []
    for farmacia in farmacias:
        distance = calculate_distance(user_location, (farmacia["latitude"], farmacia["longitude"]))
        if distance <= max_distance:
            farmacias_cercas.append({"farmacia": farmacia, "distance": distance})
            
    farmacias_cercas = sorted(farmacias_cercas, key=lambda x: x["distance"])
    # print(farmacias_cercas)
    
    for farmacia in farmacias_cercas:
        del farmacia["distance"]
        
    # print(farmacias_cercas)
    return farmacias_cercas
  

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def image_Message(number, link):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {
                "link": link
            }
        }
    )
    return data
  
def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    elif media_type == "image":
        media_id = sett.images.get(media_name, None)
    elif media_type == "video":
        media_id = sett.videos.get(media_name, None)
    elif media_type == "audio":
        media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)
    
    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido/a a Farmacias Moderna!"
        footer = "Red Farmacias Moderna"
        options = ["🛍️Realizar un pedido", "🎁Promociones del mes", "💰Consultar Precios", "❓Preguntas Frecuentes", "📍Sucursales cercanas"]
        
        listReply = listReply_Message(number, options, body, footer, "sed1", messageId)
        replyReaction = replyReaction_Message(number, messageId, "❤️")
        list.append(replyReaction)
        list.append(listReply)
    
    elif "pedido" in text:
        body = "¿Qué tipo de pedido desea realizar?"
        footer = "Red Farmacia Moderna"
        options = ["Medicamentos", "Perfumería", "Dermocosmética"]

        
        listButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        list.append(listButtonData)
        
    elif "medicamentos" in text:
        body = "¿Que tipo de medicamento desea"
        footer = "Red Farmacia Moderna"
        options = ['Con receta', 'Venta libre']
        
        listButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
        list.append(listButtonData)
    
    elif "receta" in text:
        body = "¿Que tipo de medicamento desea"
        footer = "Red Farmacia Moderna"
        options = ['Con receta', 'Venta libre']
        
        listButtonData = buttonReply_Message(number, options, body, footer, "sed5", messageId)
        list.append(listButtonData)
    
    elif "promociones" in text:
        body = "¿Te gustaría que te enviara la revista de promociones del mes?"
        footer = "Red Farmacia Moderna"
        options = ["✅ Envía la revista", "⛔ No, gracias"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed3",messageId)
        list.append(replyButtonData)
        
    elif "no, gracias." in text:
        textMessage = text_Message(number,"Perfecto! No dudes en contactarnos si tienes más preguntas. Recuerda que también ofrecemos material gratuito para la comunidad. ¡Hasta luego! 😊")
        list.append(textMessage)
    
    elif "envía" in text:
        textMessage1 = text_Message(number, "Aquí tienes la revista")
        textMessage2 = text_Message(number,"https://drive.google.com/file/d/1B6tQPCdoaSPAhT7Ei4yfuCa_mHv9aRPS/view?usp=sharing")
        enviar_Mensaje_whatsapp(textMessage1)
        enviar_Mensaje_whatsapp(textMessage2)
        
        time.sleep(10)
        
        body = "¿Deseas volver al menú principal?"
        footer = "Red Farmacias Moderna"
        options = ["✅ Sí", "Finalizar chat"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed8", messageId)
        list.append(replyButtonData)
        
    elif "sí" in text:
        textMessage = text_Message(number, "Perfecto! ahora serás redirigido al menú principal")
        enviar_Mensaje_whatsapp(textMessage)
        
        body = "Bienvenido/a a Farmacias Moderna"
        footer = "Red Farmacias Moderna"
        options = ["🛍️Realizar un pedido", "🎁Promociones del mes", "💰Consultar Precios", "❓Preguntas Frecuentes", "📍Sucursales cercanas"]
        
        listReply = listReply_Message(number, options, body, footer, "sed9", messageId)
        list.append(listReply)
    
    elif "finalizar chat" in text:
       textMessage = text_Message(number, "Damos por finalizado el chat. Para futuras consultas, podés utilizar este canal de atención de L a V de 8:30 a 21hs. ¡Que tengas buen día! 🖐")
       list.append(textMessage)
        
    elif "consultar precios" in text:
        textMessage = text_Message(number, "Por favor, escríbenos los productos que te interesan y te responderemos lo antes posible")
        enviar_Mensaje_whatsapp(textMessage)
        
    #elif "preguntas frecuentes" in text:
    #   textMessage = text_Message(number, "Por favor, a continuación envía tu ubicación")
    #   list.append(textMessage)
      
    elif "sucursales cercanas" in text:
        textMessage = text_Message(number, "Por favor, a continuación envía tu ubicación")
        enviar_Mensaje_whatsapp(textMessage)
           
    elif "location" in text:
        text = text[:-8] # elimina la palabra location del string
        user_location = get_coordinates(text) # obtiene las coordenadas del usuario
        farmacias_cercas = encontrar(user_location, FARMACIAS) # filtra las farmacias cercanas
        textMessageLocation = text_Message(number, f"La farmacia mas cercana es: {farmacias_cercas[0]['farmacia']['name']}.")
        enviar_Mensaje_whatsapp(textMessageLocation)
        
        time.sleep(10)
        
        body = "¿Deseas volver al menú principal?"
        footer = "Red Farmacias Moderna"
        options = ["✅ Sí", "Finalizar chat"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed8", messageId)
        list.append(replyButtonData)
    
    else :
        textMessage = text_Message(number, "Por favor, envía una opción correcta")
        enviar_Mensaje_whatsapp(textMessage)

    for item in list:
        enviar_Mensaje_whatsapp(item)
        
        
# para argentina
def replace_start(s):
    s = str(s)
    if s.startswith("549"):
        return "54" + s[3:]
    else:
        return s