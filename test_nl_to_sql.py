# test_nl_to_sql.py
from nl_to_sql import nl_to_sql

queries = [
    "Saldo disponible para producto ABC",
    "Historial de movimientos de la última semana para producto ABC",
    "Proyección de abastecimiento para producto ABC"
]

for q in queries:
    print(f"\n🔍 Consulta NL: {q}")
    print(nl_to_sql(q))
