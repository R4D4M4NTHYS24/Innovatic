# nl_to_sql.py
import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

# Asegúrate de exportar tu clave:
# export OPENAI_API_KEY=tu_openai_api_key
# o definirla en tu .env y cargarla con python-dotenv si lo prefieres.

def nl_to_sql(natural_query: str) -> str:
    """
    Convierte una consulta en lenguaje natural a SQL para nuestra tabla products.
    """
    template = """
    Eres un asistente experto que traduce peticiones de inventario en SQLite.
    La tabla se llama products y tiene columnas: id, name, quantity, last_movement.
    Genera SOLO la sentencia SQL correcta para esta petición sin explicación.

    Petición: "{query}"
    SQL:
    """
    prompt = PromptTemplate(
        input_variables=["query"],
        template=template
    )
    llm = OpenAI(temperature=0)
    chain = LLMChain(llm=llm, prompt=prompt)
    sql = chain.run(query=natural_query).strip()
    return sql
