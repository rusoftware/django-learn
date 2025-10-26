import requests
import string
import mimetypes
import os
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

# validadores de archivos multimedia
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("application/pdf", ".pdf")

# Función para obtener el tipo MIME y el tipo de medio
# a partir del nombre del archivo
def get_mimetype_and_mediatype(mediafile):
    mimetype, _ = mimetypes.guess_type(mediafile)
    mimetype = mimetype or "application/octet-stream"
    
    if mimetype.startswith("image/"):
        mediatype = "image"
    elif mimetype.startswith("video/"):
        mediatype = "video"
    elif mimetype.startswith("audio/"):
        mediatype = "audio"
    else:
        mediatype = "document"

    return mimetype, mediatype

# Validador para archivos multimedia
# que verifica si el tipo de medio es permitido
# (imagen, video, audio, documento)
def validate_supported_media_file(file):
    mimetype, mediatype = get_mimetype_and_mediatype(file.name)
    allowed_media_types = ["image", "video", "audio", "document"]
    
    if mediatype not in allowed_media_types:
        raise ValidationError(f"Tipo de archivo no permitido: {mimetype} ({mediatype})")

# Define el nombre del archivo a partir del que seleccione
# el usuario o de la URL del archivo multimedia
def get_filename_from_campaign(campaign):
    name = (campaign.filename or "").strip()
    if name:
        return name

    if campaign.media_url:
        path = urlparse(campaign.media_url).path
        name = os.path.basename(path)
        if name:
            return name

    return "default-file.jpg"


# Valida que el parámetro sea un integer positivo
def get_int_param(request, name):
    value = request.GET.get(name)
    if value is None:
        raise ValueError(f"Falta el parámetro ?{name}=<id>")
    
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"El parámetro ?{name} debe ser un número válido.")

############################################################################
# generador de mensajes para WhatsApp
# basado en plantillas de texto
def build_message(contact, template):
    data = {
        "name": contact.name or "",
        "phone": contact.phone or "",
        "text_1": contact.text_1 or "",
        "text_2": contact.text_2 or "",
        "text_3": contact.text_3 or "",
    }

    try:
        return string.Template(template).safe_substitute(data)
    except Exception as e:
        return f"[ERROR en plantilla: {str(e)}]"

# Función para enviar mensajes de texto a través de la API de WhatsApp
def send_whatsapp_message(instance, contact, message_text):
    phone_number = contact.phone.lstrip("+")
    url = f"{instance.api_url.rstrip('/')}/message/sendText/{instance.instance_name}"
    payload = {
        "number": phone_number,
        "text": message_text
    }
    headers = {
        "Content-Type": "application/json",
        "apikey": instance.api_key
    }

    print("Sending to:", url)
    print("Payload:", payload)
    print("Headers:", headers)
    print("Instance ID raw:", repr(instance.instance_name))

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        return f"success ({response.status_code})"
    except Exception as e:
        return f"error: {str(e)}"

# Función para enviar archivos multimedia a través de la API de WhatsApp
def send_whatsapp_media(instance, contact, *, mediatype, mimetype, media_url, caption, filename):
    phone_number = contact.phone.lstrip("+")
    url = f"{instance.api_url}/message/sendMedia/{instance.instance_name}"

    headers = {
        "Content-Type": "application/json",
        "apikey": instance.api_key,
    }

    payload = {
        "number": phone_number,
        "mediatype": mediatype,
        "mimetype": mimetype,
        "caption": caption,
        "media": media_url,
        "fileName": filename
    }

    print(f"Sending media to {contact.name} ({contact.phone}) via {url}")
    print("Payload:", payload)
    print("Headers:", headers)

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return 'success'
    except Exception as e:
        print("ERROR:", str(e))
        return f'error: {str(e)}'