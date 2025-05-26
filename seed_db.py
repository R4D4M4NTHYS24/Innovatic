# seed_db.py
import os
import random
from datetime import datetime, timedelta

from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Carpeta y fichero
os.makedirs("data", exist_ok=True)
DATABASE_URL = "sqlite:///data/inventory.db"

# Base y engine
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    movements = relationship("Movement", back_populates="product")

class Movement(Base):
    __tablename__ = "movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="movements")

def seed():
    # Reinicia
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()

    # 1) Definimos 5 productos de ejemplo con stock inicial
    product_defs = [
        ("ABC", 120),
        ("XYZ", 45),
        ("DEF", 200),
        ("MNO", 75),
        ("PQR", 150),
    ]
    products = [Product(name=n, quantity=q) for n, q in product_defs]
    session.add_all(products)
    session.commit()

    # 2) Para cada producto, generamos movimientos diarios de los últimos 30 días
    for prod in products:
        for days_ago in range(30):
            date = datetime.utcnow() - timedelta(days=days_ago)
            delta = random.choice([-10, -5, +5, +10, 0])
            m = Movement(product_id=prod.id, change=delta, date=date)
            session.add(m)
        # **NO ACTUALIZAR prod.quantity aquí** — mantenemos el “quantity” original

    session.commit()
    session.close()
    print("✔ Base de datos seed creada en data/inventory.db con 5 productos y 30 días de movimientos.")

if __name__ == "__main__":
    seed()
