# db.py
from sqlalchemy import text
from models import SessionLocal, init_db

# Asegúrate de inicializar la DB antes de cualquier consulta
init_db()

def execute_sql(sql: str):
    """
    Ejecuta la consulta SQL en SQLite y devuelve los resultados como lista de dicts.
    """
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        # Obtiene columnas y filas
        keys = result.keys()
        rows = result.fetchall()
        # Convierte a lista de diccionarios
        data = [dict(zip(keys, row)) for row in rows]
        return data
    finally:
        db.close()
