# Lumair - AI-Powered Air Quality Prediction System

Complete production-ready codebase for real-time air quality monitoring and ML-based forecasting.

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and **pnpm** (`npm install -g pnpm`)
- **Docker & Docker Compose**
- **API Keys** (free):
  - OpenWeatherMap: https://openweathermap.org/api
  - WAQI: https://aqicn.org/data-platform/token/

### Installation

```bash
# Install dependencies
pnpm install

# Run interactive setup (creates .env, starts Docker, initializes DB)
pnpm setup

# That's it! 🎉
```

### Access Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 📦 Available Commands

### Setup & Development
```bash
pnpm setup           # Interactive setup wizard
pnpm start           # Start all services (Docker)
pnpm stop            # Stop all services
pnpm dev             # Run backend + frontend in dev mode
pnpm logs            # View Docker logs
```

### Database
```bash
pnpm db:init         # Initialize database schema
pnpm db:seed         # Seed default locations + collect data
```

### Machine Learning
```bash
pnpm ml:train        # Train prediction model
pnpm ml:collect      # Manually collect AQI data
```

### Testing & Building
```bash
pnpm test:api        # Test all API endpoints
pnpm build           # Build frontend for production
pnpm clean           # Remove all containers and volumes
```

## 📁 Project Structure

```
lumair/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration
│   ├── database.py      # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # External API services
│   └── ml/              # ML pipeline
│       ├── data_collector.py
│       ├── train_model.py
│       └── predict.py
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── services/    # API client
│   │   └── utils/       # Helper functions
│   └── public/
├── scripts/             # Setup & utility scripts
│   ├── setup.js        # Interactive setup
│   ├── test-api.js     # API testing
│   └── seed-data.js    # Database seeding
├── docker-compose.yml
└── package.json         # Root scripts
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL + SQLAlchemy
- XGBoost (ML model)
- APScheduler (data collection)

**Frontend:**
- React + Vite
- TailwindCSS
- Chart.js
- Framer Motion

**APIs:**
- OpenWeatherMap (weather data)
- WAQI (air quality data)

## 🔌 API Endpoints

### AQI Endpoints
- `GET /api/aqi/current/{city}` - Current AQI
- `GET /api/aqi/predict/{city}` - Future predictions
- `GET /api/aqi/historical/{city}` - Historical data
- `GET /api/aqi/compare` - Compare multiple cities

### Location Endpoints
- `GET /api/locations/search` - Search cities
- `GET /api/locations/popular` - Popular locations
- `POST /api/locations/add` - Add new location

## 🔧 Development Workflow

### Day 1: Initial Setup
```bash
pnpm install
pnpm setup
# Open http://localhost:5173
```

### Day 2-3: Data Collection
Data is collected automatically every hour. Monitor with:
```bash
pnpm logs
```

### Day 3+: Train Model
After 24+ hours of data collection:
```bash
pnpm ml:train
```

## 🚢 Deployment

### Quick Deploy

**Backend (Render):**
1. Connect GitHub repo
2. Root Directory: `backend`
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Frontend (Vercel):**
```bash
cd frontend
vercel
```

**Database (Railway):**
```bash
railway login
railway init
railway add postgresql
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📊 Model Training

The XGBoost model uses:
- Historical AQI data
- Weather parameters (temp, humidity, wind, pressure)
- Pollutant levels (PM2.5, PM10, O3, NO2, SO2, CO)
- Temporal features (hour, day, month)
- Lag features (previous 24h data)

Train after collecting 90+ days of data for best results.

## 🐛 Troubleshooting

### Setup Issues
```bash
# Check Docker is running
docker --version

# Restart services
pnpm stop
pnpm start

# View logs
pnpm logs
```

### API Issues
```bash
# Test endpoints
pnpm test:api

# Check backend health
curl http://localhost:8000/health
```

### Database Issues
```bash
# Reinitialize database
pnpm db:init

# Reseed data
pnpm db:seed
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Cloud deployment guide
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Launch checklist

## 🧪 Testing

```bash
# Test all API endpoints
pnpm test:api

# Manual testing
curl http://localhost:8000/api/aqi/current/Mumbai
```

## 📱 Features

- ✅ Real-time AQI monitoring
- ✅ 24h, 48h, 72h predictions
- ✅ Historical trends
- ✅ Health recommendations
- ✅ City search with autocomplete
- ✅ Responsive design
- ✅ Auto-refresh data
- ✅ Color-coded visualizations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

MIT License - Build amazing things!

## 🆘 Support

- **Interactive Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Email:** support@lumair.example.com

---

**Built with ❤️ for clean air and healthy living** Training

The XGBoost model uses:
- Historical AQI data
- Weather parameters (temp, humidity, wind, pressure)
- Pollutant levels (PM2.5, PM10, O3, NO2, SO2, CO)
- Temporal features (hour, day, month)
- Lag features (previous 24h data)

Model automatically retrains when `train_model.py` is executed with sufficient data (90+ days).

## 🔐 Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENWEATHER_API_KEY` - Weather data
- `WAQI_API_KEY` - AQI data

Optional:
- `DATA_REFRESH_INTERVAL` - Data collection frequency (seconds)
- `CORS_ORIGINS` - Allowed origins
- `SECRET_KEY` - JWT secret

## 📱 Features

- Real-time AQI monitoring
- 24h, 48h, 72h predictions
- Historical trends
- Health recommendations
- City search with autocomplete
- Responsive design
- Auto-refresh data
- AQI color-coded visualizations

## 🧪 Testing APIs

```bash
# Health check
curl http://localhost:8000/health

# Get current AQI
curl http://localhost:8000/api/aqi/current/Mumbai

# Get predictions
curl http://localhost:8000/api/aqi/predict/Mumbai
```

## 📝 License

MIT License - Build amazing things!

## 🤝 Support

For issues or questions, check API documentation at http://localhost:8000/docs