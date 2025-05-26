from db import execute_sql

def test_db_seeded_products():
    rows = execute_sql("SELECT name, quantity FROM products;")
    # Debe haber 5 productos
    assert len(rows) == 5
    names = {r["name"] for r in rows}
    assert {"ABC", "XYZ", "DEF", "MNO", "PQR"} <= names

def test_db_movements_count():
    rows = execute_sql("SELECT COUNT(*) AS cnt FROM movements;")
    # 5 productos × 30 días = 150 movimientos
    assert rows[0]["cnt"] == 150
