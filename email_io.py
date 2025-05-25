# email_io.py
# Simulación de lectura y envío de correos reales usando flujo delegado (/me)...

import logging
import requests
from auth import get_graph_token

logger = logging.getLogger(__name__)
graph_api_endpoint = "https://graph.microsoft.com/v1.0"

def fetch_new_emails(folder_id: str = 'Inbox', top: int = 10):
    """
    Obtiene los últimos correos desde Microsoft Graph API usando flujo delegado (/me).
    Retorna una lista de dicts: {'from', 'subject', 'body'}.
    """
    token = get_graph_token()
    if not token:
        return []

    url = f"{graph_api_endpoint}/me/mailFolders/{folder_id}/messages"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        '$top': top,
        '$select': 'sender,subject,body'
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        logger.error("Error al leer correos: %s %s", resp.status_code, resp.text)
        return []

    items = resp.json().get('value', [])
    emails = []
    for item in items:
        sender = item.get('sender', {}).get('emailAddress', {}).get('address')
        subject = item.get('subject')
        body_content = item.get('body', {}).get('content')
        emails.append({'from': sender, 'subject': subject, 'body': body_content})
    logger.info(f"Obtenidos {len(emails)} correos")
    return emails


def send_email(to: str, subject: str, body: str):
    """
    Envía un correo usando Microsoft Graph API con flujo delegado (/me/sendMail).
    """
    token = get_graph_token()
    if not token:
        return False

    url = f"{graph_api_endpoint}/me/sendMail"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    message = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'toRecipients': [
                {'emailAddress': {'address': to}}
            ]
        }
    }
    resp = requests.post(url, headers=headers, json=message)
    if resp.status_code in (200, 202):
        logger.info(f"Correo enviado a {to} vía Graph API")
        return True
    else:
        logger.error("Error al enviar correo: %s %s", resp.status_code, resp.text)
        return False
