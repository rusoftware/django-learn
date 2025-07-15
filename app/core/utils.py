import requests
import string

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

def send_whatsapp_message(instance, contact, message_text):
    url = f"{instance.api_url.rstrip('/')}/message/sendText/{instance.instance_name}"
    payload = {
        "number": contact.phone,
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

def send_whatsapp_media(instance, contact, *, mediatype, mimetype, media_url, caption, filename):
    url = f"{instance.api_url}/message/sendMedia/{instance.instance_name}"

    headers = {
        "Content-Type": "application/json",
        "apikey": instance.api_key,
    }

    payload = {
        "number": contact.phone,
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