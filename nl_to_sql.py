# nl_to_sql.py
import re
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def nl_to_sql_from_subject(subject: str) -> str:
    """
    1) Valida y extrae de un asunto como
         "Consulta inventario: ABC, historial, 7 días"
       las partes: producto, tipo de consulta y días.
    2) Llama a un LLM vía LangChain para generar SOLO la SQL.
    """
    # --- 1) Validación y extracción ---
    try:
        prefix, rest = subject.split(":", 1)
    except ValueError:
        raise ValueError(
            "Asunto inválido. Debe ser:\n"
            "  Consulta inventario: <Producto>, <Tipo>, <n días>"
        )
    if prefix.strip().lower() != "consulta inventario":
        raise ValueError("Asunto inválido. Debe empezar con 'Consulta inventario:'")

    parts = [p.strip() for p in rest.split(",")]
    if len(parts) != 3:
        raise ValueError(
            "Asunto inválido. Debe tener 3 partes separadas por comas:\n"
            "  Consulta inventario: <Producto>, <Tipo>, <n días>"
        )

    producto, tipo_raw, dias_texto = parts
    m = re.search(r"(\d+)", dias_texto)
    if not m:
        raise ValueError("No se encontró un número de días válido en el asunto.")
    dias = int(m.group(1))

    tipo = tipo_raw.strip().lower()
    if tipo not in ("saldo", "historial", "historial de movimientos", "proyección", "proyeccion"):
        raise ValueError("Tipo no soportado. Usa 'saldo', 'historial' o 'proyección'.")

    # --- 2) LLM Prompt para SQL ---
    prompt = PromptTemplate(
        input_variables=["producto", "tipo", "dias"],
        template="""
Eres un experto en SQLite. Dispones de dos tablas:

  products(id, name, quantity)
  movements(id, product_id, change, date)

Genera **solo** la consulta SQL que corresponda a:
- producto: "{producto}"
- tipo de consulta: "{tipo}"     (uno de: saldo, historial, proyección)
- rango de días: últimos {dias} días.

No incluyas explicaciones ni comentarios, solo la sentencia SQL terminada en ';'
""",
    )

    llm = OpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    sql = chain.run(producto=producto, tipo=tipo, dias=dias).strip()

    # Aseguramos punto y coma
    if not sql.endswith(";"):
        sql += ";"
    return sql
