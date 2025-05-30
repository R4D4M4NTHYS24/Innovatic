"""
Convierte el asunto del correo en SQL.

• saldo / historial → consultas fijas
• proyección       → LLM devuelve current_stock y net_movement
"""

import re
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence

_PROMPT = PromptTemplate(
    input_variables=["producto", "dias"],
    template="""\
Eres experto en SQLite. Tablas:
  products(id, name, quantity)
  movements(id, product_id, change, date)

Devuelve SOLO la sentencia SQL terminada en ';' que obtenga:
  current_stock , net_movement
donde

  current_stock = quantity actual del producto
  net_movement  = SUM(change) últimos {dias} días (0 si no hay filas)

REGLAS:
1. Usa CTE o LEFT JOIN para que net_movement sea 0 cuando no existan movimientos.
2. Orden de columnas: current_stock , net_movement
3. Sin comentarios ni columnas extra.

Datos:
- producto = "{producto}"
- rango    = {dias} días
"""
)

_CHAIN: RunnableSequence = _PROMPT | OpenAI(temperature=0)

def _sql_saldo(prod: str) -> str:
    return f"SELECT quantity FROM products WHERE name = '{prod}';"

def _sql_historial(prod: str, dias: int) -> str:
    return (
        "SELECT change, date "
        "FROM movements "
        f"WHERE product_id = (SELECT id FROM products WHERE name = '{prod}') "
        f"AND date >= date('now', '-{dias} days');"
    )

def nl_to_sql_from_subject(subject: str) -> str:
    try:
        prefix, rest = subject.split(":", 1)
    except ValueError:
        raise ValueError("Formato: 'Consulta inventario: <Producto>, <Tipo>, <n días>'")
    if prefix.strip().lower() != "consulta inventario":
        raise ValueError("Debe empezar con 'Consulta inventario:'")

    prod, tipo_raw, dias_raw = [p.strip() for p in rest.split(",")]
    m = re.search(r"\d+", dias_raw)
    if not m:
        raise ValueError("Número de días no encontrado")
    dias = int(m.group())

    tipo = tipo_raw.lower()
    if "saldo" in tipo:
        return _sql_saldo(prod)
    if "historial" in tipo:
        return _sql_historial(prod, dias)

    # proyección via LLM
    result = _CHAIN.invoke({"producto": prod, "dias": dias})
    sql = next(iter(result.values())).strip() if isinstance(result, dict) else str(result).strip()
    return sql if sql.endswith(";") else sql + ";"
