# tests/test_nl_to_sql.py
import pytest
from nl_to_sql import nl_to_sql_from_subject

@pytest.mark.parametrize("subject,product", [
    ("Consulta inventario: ABC, saldo, 7 días", "ABC"),
    ("Consulta inventario: XYZ, historial, 3 días", "XYZ"),
    ("Consulta inventario: DEF, proyección, 5 días", "DEF"),
])
def test_nl_to_sql_basic_minimal(subject, product):
    sql = nl_to_sql_from_subject(subject).strip()
    # 1) termina en ';'
    assert sql.endswith(";"), f"No termina en ';': {sql}"
    # 2) empieza con SELECT o WITH
    assert sql.upper().startswith(("SELECT", "WITH")), f"No empieza con SELECT/ WITH: {sql}"
    # 3) menciona el producto
    assert product in sql, f"No contiene '{product}': {sql}"

def test_nl_to_sql_invalid_prefix():
    with pytest.raises(ValueError):
        nl_to_sql_from_subject("Foo: ABC, saldo, 1 día")

def test_nl_to_sql_missing_parts():
    with pytest.raises(ValueError):
        nl_to_sql_from_subject("Consulta inventario: ABC, saldo")
