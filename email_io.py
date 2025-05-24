# email_io.py

import json
import logging

logger = logging.getLogger(__name__)

def fetch_new_emails(json_path="data/test_emails.json"):
    """
    Simula la lectura de correos nuevos desde un JSON de ejemplo.
    Retorna una lista de dicts: [{ 'from': ..., 'subject': ..., 'body': ... }, ...]
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            emails = json.load(f)
        logger.info(f"Cargados {len(emails)} correos de {json_path}")
        return emails
    except FileNotFoundError:
        logger.error(f"No se encontró el archivo {json_path}")
        return []

def send_email(to, subject, body, out_path="data/sent_emails.log"):
    """
    Simula el envío de un correo.  
    Escribe los datos en un log local.
    """
    log_entry = {
        "to": to,
        "subject": subject,
        "body": body
    }
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    logger.info(f"Correo simulado enviado a {to} (guardado en {out_path})")
