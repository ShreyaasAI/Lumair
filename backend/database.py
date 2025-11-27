from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AQIRecord(Base):
    __tablename__ = "aqi_records"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    country = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    aqi = Column(Float)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)
    no2 = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_city_timestamp', 'city', 'timestamp'),
    )

class AQIPrediction(Base):
    __tablename__ = "aqi_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    predicted_aqi = Column(Float)
    prediction_hours = Column(Integer)  # 24, 48, 72
    created_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
    __table_args__ = (
        Index('idx_city_prediction', 'city', 'created_at'),
    )

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, unique=True, index=True)
    country = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    is_active = Column(Integer, default=1)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)