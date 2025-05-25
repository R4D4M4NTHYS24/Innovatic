# nl_to_sql.py
import os
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Carga la clave de OpenAI desde .env
dotenv_loaded = load_dotenv()

# Función principal que traduce NL a SQL
def nl_to_sql(natural_query: str) -> str:
    """
    Convierte una consulta en lenguaje natural a SQL para una base SQLite
    con tablas:
    - products(id, name, quantity)
    - movements(id, product_id, change, date)

    Retorna la consulta SQL adecuada según el tipo de petición:
      • Saldo disponible
      • Historial de movimientos (última semana)
      • Proyección de abastecimiento
    """
    # Extrae el nombre del producto después de la palabra 'producto'
    product = natural_query
    if 'producto' in natural_query.lower():
        parts = natural_query.lower().split('producto')
        product = parts[-1].strip().rstrip('.')

    # Plantilla con variables product y query para contexto
    prompt = PromptTemplate(
        input_variables=["product", "query"],
        template='''
Eres un asistente que convierte consultas de inventario en SQL para SQLite.
Tablas disponibles:
- products(id, name, quantity)
- movements(id, product_id, change, date)

Casos:
1) Saldo disponible:
   SELECT quantity
   FROM products
   WHERE name = "{product}";

2) Historial de movimientos (última semana):
   SELECT change, date
   FROM movements
   WHERE product_id = (
     SELECT id FROM products WHERE name = "{product}"
   )
   AND date >= date('now', '-7 days');

3) Proyección de abastecimiento:
   WITH recent AS (
     SELECT SUM(change) AS total_change
     FROM movements
     WHERE product_id = (
       SELECT id FROM products WHERE name = "{product}"
     )
     AND date >= date('now', '-7 days')
   )
   SELECT
     p.quantity AS current_stock,
     recent.total_change AS net_movement,
     CASE
       WHEN recent.total_change < 0 THEN
         ROUND(p.quantity / ABS(recent.total_change / 7.0), 1)
       ELSE NULL
     END AS days_until_stockout
   FROM products p, recent
   WHERE p.name = "{product}";

Ahora recibe la consulta en lenguaje natural:
"""
{query}
"""
Devuelve solo la consulta SQL apropiada sin explicaciones.
'''
    )

    # Construye y ejecuta la cadena
    llm = OpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    sql = chain.run(product=product, query=natural_query).strip()
    return sql
