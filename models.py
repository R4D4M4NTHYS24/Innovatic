# models.py
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# Ruta a tu SQLite local
DATABASE_URL = "sqlite:///./data/inventory.db"

# Crea el motor y la sesión
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relación hacia movimientos
    movements = relationship("Movement", back_populates="product")

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    # Relación inversa
    product = relationship("Product", back_populates="movements")

def init_db():
    """
    Crea las tablas 'products' y 'movements' si no existen.
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Tablas creadas: products y movements en data/inventory.db")
