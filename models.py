# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Ruta a tu SQLite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/inventory.db"

# Motor y sesión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    quantity = Column(Integer, nullable=False)
    last_movement = Column(DateTime, default=datetime.utcnow)

def init_db():
    # Crea tablas
    Base.metadata.create_all(bind=engine)

    # Poblado de ejemplo (solo si tabla vacía)
    db = SessionLocal()
    if not db.query(Product).first():
        ejemplos = [
            Product(name="ABC", quantity=120, last_movement=datetime(2025,5,20)),
            Product(name="XYZ", quantity=45,  last_movement=datetime(2025,5,22)),
        ]
        db.add_all(ejemplos)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada con datos de ejemplo.")
