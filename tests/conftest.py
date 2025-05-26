import os, sys
# 1) Calcula la ruta absoluta de la raíz del proyecto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db import SessionLocal, init_db
from seed_db import seed

# Fixture para TestClient de FastAPI
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# Fixture para inicializar la base fresh
@pytest.fixture(scope="module", autouse=True)
def setup_db(tmp_path_factory):
    # redirige la DB a un archivo temporal
    db_file = tmp_path_factory.mktemp("data") / "test_inventory.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    # seed completo
    seed()
    yield
    # cleanup opcional
