# check_db.py
import sqlite3

conn = sqlite3.connect("data/inventory.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM products;")
print("Productos:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM movements;")
print("Movimientos:", cur.fetchone()[0])

# Opcional: lista de productos
cur.execute("SELECT id, name, quantity FROM products;")
print("\nProductos detalle:")
for row in cur.fetchall():
    print(" ", row)

conn.close()
