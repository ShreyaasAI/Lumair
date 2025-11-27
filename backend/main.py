from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import logging
from config import settings
from database import init_db, SessionLocal
from routes import aqi, locations
from ml.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background scheduler for data collection
scheduler = BackgroundScheduler()

def scheduled_data_collection():
    """Periodic data collection job"""
    logger.info("Running scheduled data collection")
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        collector.collect_all_active_locations()
    except Exception as e:
        logger.error(f"Error in scheduled collection: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Lumair API...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Initialize default locations
    db = SessionLocal()
    try:
        collector = DataCollector(db)
        collector.initialize_default_locations()
        
        # Initial data collection
        collector.collect_all_active_locations()
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
    finally:
        db.close()
    
    # Start scheduler
    scheduler.add_job(
        scheduled_data_collection,
        'interval',
        seconds=settings.DATA_REFRESH_INTERVAL,
        id='data_collection',
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Scheduler started (interval: {settings.DATA_REFRESH_INTERVAL}s)")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Scheduler stopped")
    logger.info("Lumair API shutting down")

# Create FastAPI app
app = FastAPI(
    title="Lumair API",
    description="AI-powered air quality prediction system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(aqi.router)
app.include_router(locations.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lumair API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "aqi": "/api/aqi",
            "locations": "/api/locations"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "active" if scheduler.running else "inactive"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )