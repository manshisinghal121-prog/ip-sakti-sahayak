import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ip_sakti.db")

# Render/PostgreSQL often supplies postgres://; SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    persona = Column(String(50), nullable=False, default="innovator")
    language = Column(String(10), nullable=False, default="en")
    ml_category = Column(String(100), nullable=True)
    ml_confidence = Column(Float, nullable=True)
    ml_confidence_level = Column(String(30), nullable=True)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_query(**kwargs):
    db = SessionLocal()
    try:
        record = QueryHistory(**kwargs)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    finally:
        db.close()
