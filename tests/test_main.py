import pytest
from fastapi.testclient import TestClient

def test_process_email_saldo(client: TestClient):
    payload = {
        "sender": "test@foo.com",
        "subject": "Consulta inventario: ABC, saldo, 1 día",
        "body": ""
    }
    resp = client.post("/process-email", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "sent"
    assert "120 unidades" in data["body"]

def test_process_email_historial(client: TestClient):
    payload = {
        "sender": "test@foo.com",
        "subject": "Consulta inventario: ABC, historial, 2 días",
        "body": ""
    }
    resp = client.post("/process-email", json=payload)
    assert resp.status_code == 200
    assert "Historial de movimientos" in resp.json()["body"]

def test_process_email_invalid(client: TestClient):
    payload = {
        "sender": "test@foo.com",
        "subject": "Hola mundo",
        "body": ""
    }
    resp = client.post("/process-email", json=payload)
    assert resp.status_code == 400
