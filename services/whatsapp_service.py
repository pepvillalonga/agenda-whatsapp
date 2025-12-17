import os
import requests
from dotenv import load_dotenv

load_dotenv()

WA_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"

def send_whatsapp_message(to_number, text_body):
    """Envía un mensaje de texto a un usuario de WhatsApp."""
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text_body}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True
        print(f"Error WhatsApp Send: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"Exception WhatsApp: {e}")
        return False

def get_media_url(media_id):
    """Obtiene la URL de descarga de un archivo multimedia."""
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {
            "Authorization": f"Bearer {WA_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("url")
        return None
    except Exception as e:
        print(f"Error getting media URL: {e}")
        return None

def download_media(media_url):
    """Descarga el contenido binario del medio."""
    try:
        headers = {
            "Authorization": f"Bearer {WA_TOKEN}"
        }
        response = requests.get(media_url, headers=headers)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"Error downloading media: {e}")
        return None
