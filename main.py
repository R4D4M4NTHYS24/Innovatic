import os
import json
import logging
import asyncio
import atexit
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from db import execute_sql
from email_io import fetch_new_emails, send_email

# --- Configuración básica ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventario")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
BACKOFF_BASE = 2  # base para back-off exponencial

# --- Persistencia de IDs procesados ---
PROCESSED_FILE = "data/processed.json"
os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "r") as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

def _save_processed():
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)
atexit.register(_save_processed)

# --- FastAPI app ---
app = FastAPI(
    title="Inventario Automático",
    description="API que procesa consultas de inventario vía correo y responde automáticamente",
    version="1.0"
)

# --- Esquema de entrada ---
class EmailIn(BaseModel):
    sender: str = Field(..., example="usuario@empresa.com")
    subject: str = Field(..., example="Consulta inventario: ABC, saldo, 7 días")
    body: str = Field(None, example="Texto libre opcional en el cuerpo")

# --- Helpers de SQL dinámico ---
def parse_subject(subject: str):
    """Extrae producto, tipo y días desde el asunto."""
    try:
        prefix, rest = subject.split(":", 1)
    except ValueError:
        raise ValueError(
            "Asunto inválido. Debe ser: Consulta inventario: <Producto>, <Tipo>, <n días>"
        )
    if prefix.strip().lower() != "consulta inventario":
        raise ValueError("Asunto inválido. Debe empezar con 'Consulta inventario:'")

    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 3:
        raise ValueError(
            "Asunto inválido. Debe tener tres partes separadas por comas:\n"
            "  Consulta inventario: <Producto>, <Tipo>, <n días>"
        )

    producto, tipo, dias_texto = parts
    m = re.search(r"(\d+)", dias_texto)
    if not m:
        raise ValueError("No se encontró un número de días válido en el asunto.")
    dias = int(m.group(1))
    tipo = tipo.lower()
    if tipo not in ("saldo", "historial", "historial de movimientos", "proyección", "proyeccion"):
        raise ValueError("Tipo no soportado. Usa 'saldo', 'historial' o 'proyección'.")
    return producto, tipo, dias

def build_sql(producto: str, tipo: str, dias: int) -> str:
    """Genera la sentencia SQL según tipo y días."""
    if tipo == "saldo":
        return (
            f"SELECT quantity "
            f"FROM products "
            f"WHERE name = '{producto}';"
        )
    if tipo.startswith("historial"):
        return (
            f"SELECT change, date "
            f"FROM movements "
            f"WHERE product_id = ("
            f"  SELECT id FROM products WHERE name = '{producto}'"
            f") "
            f"AND date >= date('now','-{dias} days');"
        )
    # proyección
    return (
        f"WITH recent AS ( "
        f"  SELECT SUM(change) AS total_change "
        f"  FROM movements "
        f"  WHERE product_id = ("
        f"    SELECT id FROM products WHERE name = '{producto}'"
        f"  ) "
        f"  AND date >= date('now','-{dias} days')"
        f") "
        f"SELECT "
        f"  p.quantity AS current_stock, "
        f"  recent.total_change AS net_movement, "
        f"  CASE "
        f"    WHEN recent.total_change < 0 THEN "
        f"      ROUND(p.quantity / ABS(recent.total_change / {dias}.0), 1) "
        f"    ELSE NULL "
        f"  END AS days_until_stockout "
        f"FROM products p, recent "
        f"WHERE p.name = '{producto}';"
    )

def get_data_range(producto: str) -> int | None:
    """Devuelve cuántos días hay registrados para un producto; o None si no hay movimientos."""
    sql = (
        f"SELECT MIN(date) AS earliest "
        f"FROM movements "
        f"WHERE product_id = (SELECT id FROM products WHERE name = '{producto}')"
    )
    row = execute_sql(sql)[0]
    if not row.get("earliest"):
        return None
    earliest = datetime.fromisoformat(row["earliest"])
    return (datetime.utcnow() - earliest).days

def adjust_days(requested: int, available: int):
    """Ajusta días y opcionalmente devuelve un aviso."""
    if available < requested:
        aviso = (
            f"⚠ Solo hay datos desde hace {available} días. "
            f"Mostrando últimos {available} días disponibles."
        )
        return available, aviso
    return requested, None

# --- Formateo de la respuesta humana ---
def format_response(rows):
    if not rows:
        return "No se encontraron datos para tu solicitud."
    keys = set(rows[0].keys())
    if keys == {"quantity"}:
        return f"Saldo disponible: {rows[0]['quantity']} unidades"
    if keys == {"change", "date"}:
        lines = ["Historial de movimientos:"]
        for r in rows:
            date = r["date"][:10]
            change = f"{r['change']:+d}"
            lines.append(f"• {date} → {change}")
        return "\n".join(lines)
    # proyección
    r = rows[0]
    lines = [
        f"Saldo actual: {r['current_stock']} unidades",
        f"Cambio neto en última semana: {r['net_movement']:+d}"
    ]
    days = r.get("days_until_stockout")
    if days is not None:
        lines.append(f"Días hasta agotar stock: {days}")
    else:
        lines.append("Sin consumo neto, no se proyecta agotamiento.")
    return "\n".join(lines)

# --- Endpoint manual ---
@app.post("/process-email")
def process_email(email: EmailIn):
    try:
        producto, tipo, dias_req = parse_subject(email.subject)

        avail = get_data_range(producto)
        if avail is None:
            human_body = f"No hay movimientos registrados para el producto {producto}."
        else:
            dias_eff, aviso = adjust_days(dias_req, avail)
            sql = build_sql(producto, tipo, dias_eff)
            logger.info("SQL generado: %s", sql)

            rows = execute_sql(sql)
            if tipo.startswith("historial"):
                rows = rows[:dias_req]
            logger.info("Resultados obtenidos: %s", rows)

            human_body = (aviso + "\n\n" if aviso else "") + format_response(rows)

        resp_subj = f"Re: {email.subject}"
        send_email(email.sender, resp_subj, human_body)
        logger.info("Correo enviado a %s", email.sender)

        # ✏ Aquí agregamos 'body' a la respuesta JSON
        return {
            "status": "sent",
            "to": email.sender,
            "subject": resp_subj,
            "body": human_body
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        logger.exception("Error en process_email")
        raise HTTPException(status_code=500, detail="Error interno al procesar el correo")

# --- Polling automático ---
async def poll_inbox():
    backoff = 0
    await asyncio.sleep(POLL_INTERVAL)
    while True:
        try:
            mails = fetch_new_emails()
            for em in mails:
                msg_id = em.get("id") or (em.get("from","") + em.get("subject",""))
                subj = em.get("subject","")
                if msg_id in processed_ids:
                    continue
                processed_ids.add(msg_id)

                if not subj.lower().startswith("consulta inventario:"):
                    logger.debug("Ignorando: %s", subj)
                    continue

                try:
                    payload = EmailIn(
                        sender=em["from"], subject=subj, body=em.get("body")
                    )
                    process_email(payload)
                    backoff = 0
                except HTTPException as he:
                    logger.error("HTTPException %s: %s", msg_id, he.detail)
                except Exception:
                    logger.exception("Error interno %s", msg_id)

            if backoff > 0:
                wait = BACKOFF_BASE ** backoff
                logger.warning("Back-off %s s", wait)
                await asyncio.sleep(wait)
                backoff += 1
            else:
                await asyncio.sleep(POLL_INTERVAL)

        except Exception as e:
            status = getattr(e, "response", None) and getattr(e.response, "status_code", None)
            if status == 429:
                backoff = max(1, backoff+1)
                logger.warning("429 detectado, back-off nivel %s", backoff)
                continue
            logger.exception("Error inesperado en poll_inbox")
            await asyncio.sleep(POLL_INTERVAL)

# --- Arranque ---
@app.on_event("startup")
def on_startup():
    logger.info("🔑 Autenticando en Microsoft Graph…")
    fetch_new_emails()  # forzar login
    logger.info("✅ Autenticación completada. Polling cada %s s.", POLL_INTERVAL)
    asyncio.create_task(poll_inbox())
