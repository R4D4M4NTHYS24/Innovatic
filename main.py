import os
import json
import logging
import asyncio
import atexit
import re
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

from nl_to_sql import nl_to_sql_from_subject
from db import execute_sql
from email_io import fetch_new_emails, send_email

# ------------------- logging y constantes --------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventario")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 30))
BACKOFF_BASE  = 2

# ------------------- persistencia de IDs procesados ----------------------------------
PROCESSED_FILE = "data/processed.json"
os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
processed_ids: set[str] = set()
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "r") as f:
        processed_ids = set(json.load(f))

def _save_processed():
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)

atexit.register(_save_processed)

# ------------------- FastAPI ----------------------------------------------------------
app = FastAPI(
    title="Inventario Automático",
    description="Procesa consultas de inventario vía correo y responde automáticamente",
    version="2.1",
)

# ------------------- Modelo de entrada (acepta 'from' o 'sender') ---------------------
class EmailIn(BaseModel):
    sender:  str = Field(..., alias="from")
    subject: str
    body:    str | None = None

    model_config = ConfigDict(populate_by_name=True)

# ------------------- helpers ----------------------------------------------------------
def _extract_days(subject: str) -> int:
    m = re.search(r"\d+", subject)
    return int(m.group()) if m else 7

# ------------------- formateo de respuesta -------------------------------------------
def format_response(rows, dias: int) -> str:
    if not rows:
        return "No se encontraron datos para tu solicitud."

    keys = set(rows[0])

    if keys == {"quantity"}:                               # SALDO
        return f"Saldo disponible: {rows[0]['quantity']} unidades"

    if keys == {"change", "date"}:                         # HISTORIAL
        lines = ["Historial de movimientos:"]
        lines += [f"• {r['date'][:10]} → {r['change']:+d}" for r in rows]
        return "\n".join(lines)

    if keys == {"current_stock", "net_movement"}:          # PROYECCIÓN
        r = rows[0]
        mov  = r["net_movement"]
        left = round(r["current_stock"] / abs(mov / dias), 1) if mov < 0 else None
        return "\n".join([
            f"Saldo actual: {r['current_stock']} unidades",
            f"Cambio neto en última semana: {mov:+d}",
            f"Días hasta agotar stock: {left}"
            if left is not None else
            "Sin consumo neto, no se proyecta agotamiento."
        ])

    # fallback
    return "\n".join(f"{k}: {v}" for k, v in rows[0].items())

# ------------------- endpoint ---------------------------------------------------------
@app.post("/process-email")
def process_email(email: EmailIn):
    try:
        dias_req = _extract_days(email.subject)

        sql  = nl_to_sql_from_subject(email.subject)
        logger.info("SQL generado: %s", sql)

        rows = execute_sql(sql)
        logger.info("Filas devueltas: %s", rows)

        body_text = format_response(rows, dias_req)

        resp_subj = f"Re: {email.subject}"
        send_email(email.sender, resp_subj, body_text)
        logger.info("Correo enviado a %s", email.sender)

        return {
            "status":  "sent",
            "to":      email.sender,
            "subject": resp_subj,
            "body":    body_text,
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        logger.exception("Error en process_email")
        raise HTTPException(status_code=500, detail="Error interno al procesar el correo")

# ------------------- polling ---------------------------------------------------------
async def poll_inbox():
    backoff = 0
    await asyncio.sleep(POLL_INTERVAL)
    while True:
        try:
            for em in fetch_new_emails():
                msg_id = em.get("id") or em.get("from","") + em.get("subject","")
                if msg_id in processed_ids:
                    continue
                processed_ids.add(msg_id)

                subj = em.get("subject","")
                if not subj.lower().startswith("consulta inventario:"):
                    logger.debug("Ignorado: %s", subj)
                    continue

                try:
                    process_email(EmailIn(**em))
                    backoff = 0
                except Exception:
                    backoff = min(backoff + 1, 5)
                    logger.exception("Error procesando %s", msg_id)

            await asyncio.sleep(BACKOFF_BASE**backoff if backoff else POLL_INTERVAL)
        except Exception:
            logger.exception("Fallo inesperado en poll_inbox")
            await asyncio.sleep(POLL_INTERVAL)

@app.on_event("startup")
def _startup():
    logger.info("🔑 Autenticando en Microsoft Graph…")
    fetch_new_emails()
    logger.info("✅ Autenticación lista. Polling cada %s s.", POLL_INTERVAL)
    asyncio.create_task(poll_inbox())
