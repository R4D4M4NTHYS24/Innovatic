# seed_db.py
import os
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define el modelo
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    movements = relationship("Movement", back_populates="product")

class Movement(Base):
    __tablename__ = 'movements'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    change = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="movements")

def seed():
    # Crea carpeta data si no existe
    os.makedirs('data', exist_ok=True)
    engine = create_engine('sqlite:///data/inventory.db')
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Productos de ejemplo
    productos = [
        Product(name='ABC', quantity=120),
        Product(name='XYZ', quantity=45),
        Product(name='DEF', quantity=200),
    ]
    session.add_all(productos)
    session.commit()

    # Movimientos diarios de la última semana
    for prod in productos:
        for i in range(7):
            mv = Movement(
                product_id=prod.id,
                change = (-5 if i % 2 == 0 else +10),
                date = datetime.utcnow() - timedelta(days=i)
            )
            session.add(mv)
    session.commit()
    print("Base de datos seed creada en data/inventory.db")

if __name__ == "__main__":
    seed()
