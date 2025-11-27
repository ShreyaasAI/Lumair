from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lumair"
    
    # API Keys
    OPENWEATHER_API_KEY: str
    WAQI_API_KEY: str
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model
    MODEL_PATH: str = "./ml/models/aqi_model.pkl"
    SCALER_PATH: str = "./ml/models/scaler.pkl"
    
    # Data Collection
    DATA_REFRESH_INTERVAL: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()