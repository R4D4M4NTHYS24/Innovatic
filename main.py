# main.py
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from email_io import fetch_new_emails, send_email
from nl_to_sql import nl_to_sql
from db import execute_sql

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Inventario Automático")

class EmailIn(BaseModel):
    from_address: str
    subject: str
    body: str

@app.post("/process-email")
def process_email(email: EmailIn):
    """
    1) Traduce NL → SQL
    2) Ejecuta SQL
    3) Envía respuesta (simulada)
    """
    try:
        # 1) Convertir a SQL
        sql = nl_to_sql(email.body)
        logger.info("SQL generado: %s", sql)

        # 2) Ejecutar en DB
        results = execute_sql(sql)
        logger.info("Resultados obtenidos: %s", results)

        # 3) Formatear respuesta
        # Aquí puedes mejorar: usar plantillas, HTML, etc.
        if not results:
            reply = "No se encontraron registros para tu consulta."
        else:
            lines = []
            for row in results:
                lines.append(", ".join(f"{k}: {v}" for k, v in row.items()))
            reply = "Resultados:\n" + "\n".join(lines)

        # 4) Enviar correo simulado
        send_email(
            to=email.from_address,
            subject=f"Re: {email.subject}",
            body=reply
        )

        return {"status": "success", "sent_to": email.from_address, "results": results}

    except Exception as e:
        logger.error("Error en process_email: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
