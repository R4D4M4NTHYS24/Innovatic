# Inventario Automático

**Solución automatizada de consultas de inventario vía correo electrónico**  
Utiliza Python, FastAPI, LangChain, MS Graph API y SQLite para leer peticiones en lenguaje natural, traducirlas a SQL con un LLM, ejecutar la query y responder automáticamente.

---

## 📋 Contenidos

1. [Requisitos](#-requisitos)  
2. [Instalación](#-instalación)  
3. [Variables de entorno](#-variables-de-entorno)  
4. [Inicializar base de datos](#-inicializar-base-de-datos)  
5. [Ejecutar servidor](#-ejecutar-servidor)  
6. [Pruebas unitarias](#-pruebas-unitarias)  
7. [Generar `requirements.txt`](#-generar-requirementstxt)


---

## Requisitos

- Python 3.10+  
- Cuenta en Azure AD con permisos de Graph API (Mail.Read, Mail.Send)  
- Clave de OpenAI con acceso al endpoint de completions  

---

## Instalación


# 1. Clona el repositorio
git clone https://github.com/R4D4M4NTHYS24/Innovatic
cd Innovatic

# 2. Crea y activa un virtualenv
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# 3. Instala dependencias
pip install -r requirements.txt

---

## Variables de entorno

#Crea un fichero .env en la raíz con estas claves:
CLIENT_ID=tu_client_id_de_azure
TENANT_ID=tu_tenant_id_de_azure
OPENAI_API_KEY=tu_openai_api_key

---

## Inicializar base de datos

# Genera la base SQLite con datos de ejemplo:
python seed_db.py
# ✔ Base de datos seed creada en data/inventory.db con 5 productos y 30 días de movimientos.

---

## Ejecutar servidor

# uvicorn main:app --reload

# Arrancará en http://127.0.0.1:8000

# Forzará autenticación Device Code Flow en MS Graph la primera vez.

---

## Pruebas unitarias

# pytest --maxfail=1 --disable-warnings -q

#Cubre:

Traducción NL→SQL (tests/test_nl_to_sql.py)

Endpoint FastAPI (tests/test_main.py)

---

## Requirements.txt

#Las librerias del proyecto son:

- aiohappyeyeballs==2.6.1
- aiohttp==3.11.18
- aiosignal==1.3.2
- annotated-types==0.7.0
- anyio==4.9.0
- attrs==25.3.0
- certifi==2025.4.26
- cffi==1.17.1
- charset-normalizer==3.4.2
- click==8.2.1
- colorama==0.4.6
- cryptography==45.0.2
- dataclasses-json==0.6.7
- distro==1.9.0
- fastapi==0.115.12
- frozenlist==1.6.0
- greenlet==3.2.2
- h11==0.16.0
- httpcore==1.0.9
- httpx==0.28.1
- httpx-sse==0.4.0
- idna==3.10
- iniconfig==2.1.0
- jiter==0.10.0
- jsonpatch==1.33
- jsonpointer==3.0.0
- langchain==0.3.25
- langchain-community==0.3.24
- langchain-core==0.3.61
- langchain-openai==0.3.18
- langchain-text-splitters==0.3.8
- langsmith==0.3.42
- marshmallow==3.26.1
- msal==1.32.3
- multidict==6.4.4
- mypy_extensions==1.1.0
- numpy==2.2.6
- openai==1.82.0
- orjson==3.10.18
- packaging==24.2
- pluggy==1.6.0
- propcache==0.3.1
- pycparser==2.22
- pydantic==2.11.5
- pydantic-settings==2.9.1
- pydantic_core==2.33.2
- PyJWT==2.10.1
- pytest==8.3.5
- python-dotenv==1.1.0
- PyYAML==6.0.2
- regex==2024.11.6
- requests==2.32.3
- requests-toolbelt==1.0.0
- sniffio==1.3.1
- SQLAlchemy==2.0.41
- starlette==0.46.2
- tenacity==9.1.2
- tiktoken==0.9.0
- tqdm==4.67.1
- typing-inspect==0.9.0
- typing-inspection==0.4.1
- typing_extensions==4.13.2
- urllib3==2.4.0
- uvicorn==0.34.2
- yarl==1.20.0
- zstandard==0.23.0

#¡Listo! Con esto, debería tener el proyecto Inventario Automático configurado y funcionando. 

#Siga las secciones anteriores para configurar cada parte y no dude en revisar la documentación oficial de cada herramienta (FastAPI, LangChain, Microsoft Graph) 

#¡Buena suerte con su automatización de inventarios!




