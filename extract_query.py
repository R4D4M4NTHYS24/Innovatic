# extract_query.py
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Cadena que extrae JSON con producto, tipo y días
EXTRACT_TEMPLATE = """\
Eres un extractor. Recibes un texto de correo (asunto + cuerpo). 
De ahí solo extrae en JSON estas 3 llaves, nada más:
  - product: nombre del producto (exacto, mayúsculas/minúsculas como en DB)
  - request_type: uno de ["saldo", "historial", "proyección"]
  - days: número entero de días

Texto de entrada:
\"\"\"{text}\"\"\"

Salida JSON válida:
{{"product": "...", "request_type": "...", "days": ...}}
"""

extract_prompt = PromptTemplate(
    input_variables=["text"],
    template=EXTRACT_TEMPLATE
)
_llm = OpenAI(temperature=0, max_tokens=100)
_extract_chain = LLMChain(llm=_llm, prompt=extract_prompt)

def extract_query(text: str) -> dict:
    out = _extract_chain.run(text=text)
    try:
        data = __import__("json").loads(out)
        # Validaciones básicas
        if not all(k in data for k in ("product", "request_type", "days")):
            raise ValueError
        return data
    except Exception:
        raise ValueError(f"No pude extraer consulta válida del texto:\n{out}")
