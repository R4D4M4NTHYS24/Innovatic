import os
import logging
from dotenv import load_dotenv
from msal import PublicClientApplication, SerializableTokenCache

# Carga variables de entorno
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")

# Scopes necesarios para Device Code Flow (delegados)
SCOPES = ["User.Read", "Mail.Read", "Mail.Send"]

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1) Prepara el token cache
CACHE_FILE = "token_cache.bin"
cache = SerializableTokenCache()
if os.path.exists(CACHE_FILE):
    cache.deserialize(open(CACHE_FILE, "r").read())

# 2) Construye la app MSAL con el cache
app = PublicClientApplication(
    client_id=CLIENT_ID,
    authority="https://login.microsoftonline.com/common",
    token_cache=cache
)

def get_graph_token():
    # 3) Intenta silent (caché)
    result = app.acquire_token_silent(SCOPES, account=None)
    if result and "access_token" in result:
        logger.info("Usando token en caché.")
        return result["access_token"]

    # 4) Si no hay token válido, levanta Device Code Flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        logger.error("Error iniciando Device Code Flow: %s", flow)
        return None
    print(flow["message"])  # instrucciones al usuario

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" in result:
        # 5) Guarda cache a disco
        open(CACHE_FILE, "w").write(cache.serialize())
        logger.info("Token obtenido y cache guardado.")
        return result["access_token"]
    else:
        logger.error("Error obteniendo token: %s", result.get("error_description"))
        return None

if __name__ == "__main__":
    token = get_graph_token()
    if token:
        print("Token válido — primeros 100 chars:", token[:100])
