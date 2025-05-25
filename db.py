# db.py
from sqlalchemy import text
from models import SessionLocal, init_db

# Inicializa la base de datos (crea tablas) antes de consultas
def init():
    init_db()

# Ejecuta init al importar el módulo
auto_init = init()

def execute_sql(sql: str):
    """
    Ejecuta la consulta SQL en SQLite y devuelve resultados como lista de diccionarios.
    """
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        keys = result.keys()
        rows = result.fetchall()
        # Mapea a dict por fila
        return [dict(zip(keys, row)) for row in rows]
    finally:
        db.close()
