# Lumair API Documentation

Base URL: `http://localhost:8000` (development) or `https://your-domain.com` (production)

## 🔐 Authentication

Currently, all endpoints are public. Authentication can be added for production use.

---

## 📍 AQI Endpoints

### Get Current AQI

Retrieve real-time air quality data for a city.

**Endpoint:** `GET /api/aqi/current/{city}`

**Parameters:**
- `city` (path) - City name (e.g., "Mumbai", "New York")

**Response:**
```json
{
  "city": "Mumbai",
  "country": "India",
  "aqi": 156,
  "category": "Unhealthy",
  "pollutants": {
    "pm25": 89,
    "pm10": 145,
    "o3": 45,
    "no2": 32,
    "so2": 12,
    "co": 8
  },
  "weather": {
    "temperature": 28.5,
    "humidity": 75,
    "wind_speed": 3.2,
    "pressure": 1013
  },
  "timestamp": "2025-10-28T10:30:00"
}
```

**Example:**
```bash
curl http://localhost:8000/api/aqi/current/Mumbai
```

---

### Predict Future AQI

Get ML-based AQI predictions for specified time periods.

**Endpoint:** `GET /api/aqi/predict/{city}`

**Parameters:**
- `city` (path) - City name
- `hours` (query, optional) - Comma-separated prediction intervals (default: "24,48,72")

**Response:**
```json
{
  "city": "Mumbai",
  "current_aqi": 156,
  "aqi_category": "Unhealthy",
  "predictions": [
    {
      "hours": 24,
      "timestamp": "2025-10-29T10:30:00",
      "predicted_aqi": 142.5,
      "temperature": 29.0,
      "humidity": 70
    },
    {
      "hours": 48,
      "timestamp": "2025-10-30T10:30:00",
      "predicted_aqi": 138.2,
      "temperature": 28.5,
      "humidity": 72
    }
  ],
  "health_tips": [
    "Reduce prolonged outdoor exertion",
    "Wear a mask when going outside",
    "Keep windows closed"
  ],
  "generated_at": "2025-10-28T10:30:00"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/aqi/predict/Mumbai?hours=24,48"
```

---

### Get Historical AQI

Retrieve historical air quality data.

**Endpoint:** `GET /api/aqi/historical/{city}`

**Parameters:**
- `city` (path) - City name
- `days` (query, optional) - Number of days to retrieve (1-90, default: 7)

**Response:**
```json
{
  "city": "Mumbai",
  "country": "India",
  "data": [
    {
      "timestamp": "2025-10-21T10:00:00",
      "aqi": 145,
      "pm25": 85,
      "pm10": 140,
      "temperature": 27.5,
      "humidity": 78
    }
  ],
  "count": 168
}
```

**Example:**
```bash
curl "http://localhost:8000/api/aqi/historical/Mumbai?days=7"
```

---

### Compare Cities

Compare current AQI across multiple cities.

**Endpoint:** `GET /api/aqi/compare`

**Parameters:**
- `cities` (query) - Comma-separated city names (max 10)

**Response:**
```json
{
  "cities": [
    {
      "city": "Mumbai",
      "country": "India",
      "aqi": 156,
      "category": "Unhealthy",
      "timestamp": "2025-10-28T10:30:00"
    },
    {
      "city": "Delhi",
      "country": "India",
      "aqi": 287,
      "category": "Very Unhealthy",
      "timestamp": "2025-10-28T10:30:00"
    }
  ],
  "count": 2
}
```

**Example:**
```bash
curl "http://localhost:8000/api/aqi/compare?cities=Mumbai,Delhi,Beijing"
```

---

## 🌍 Location Endpoints

### Search Locations

Search for cities with autocomplete.

**Endpoint:** `GET /api/locations/search`

**Parameters:**
- `q` (query) - Search query (min 2 characters)
- `limit` (query, optional) - Max results (1-50, default: 10)

**Response:**
```json
{
  "results": [
    {
      "city": "Mumbai",
      "country": "India",
      "lat": 19.076,
      "lon": 72.8777,
      "display_name": "Mumbai, India"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/api/locations/search?q=Mumb"
```

---

### Get Popular Locations

Retrieve list of pre-configured popular cities.

**Endpoint:** `GET /api/locations/popular`

**Response:**
```json
{
  "locations": [
    {
      "city": "Mumbai",
      "country": "India",
      "lat": 19.076,
      "lon": 72.8777,
      "display_name": "Mumbai, India"
    }
  ],
  "count": 8
}
```

**Example:**
```bash
curl http://localhost:8000/api/locations/popular
```

---

### Add Location

Add a new city to monitoring list.

**Endpoint:** `POST /api/locations/add`

**Parameters:**
- `city` (query) - City name

**Response:**
```json
{
  "message": "Location added successfully",
  "location": {
    "city": "Paris",
    "country": "France",
    "lat": 48.8566,
    "lon": 2.3522
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/locations/add?city=Paris"
```

---

### Get Nearby Locations

Find monitored cities near coordinates.

**Endpoint:** `GET /api/locations/nearby`

**Parameters:**
- `lat` (query) - Latitude (-90 to 90)
- `lon` (query) - Longitude (-180 to 180)
- `radius_km` (query, optional) - Search radius in km (1-500, default: 50)

**Response:**
```json
{
  "locations": [
    {
      "city": "Mumbai",
      "country": "India",
      "lat": 19.076,
      "lon": 72.8777,
      "display_name": "Mumbai, India"
    }
  ],
  "count": 1
}
```

**Example:**
```bash
curl "http://localhost:8000/api/locations/nearby?lat=19.076&lon=72.8777&radius_km=100"
```

---

## 🏥 System Endpoints

### Health Check

Check API and service status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler": "active"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Root

Get API information.

**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "Lumair API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "aqi": "/api/aqi",
    "locations": "/api/locations"
  }
}
```

---

## 📊 AQI Categories

| AQI Range | Category | Color | Health Implications |
|-----------|----------|-------|---------------------|
| 0-50 | Good | Green | Air quality is excellent |
| 51-100 | Moderate | Yellow | Acceptable for most people |
| 101-150 | Unhealthy for Sensitive Groups | Orange | Sensitive groups should limit prolonged outdoor exertion |
| 151-200 | Unhealthy | Red | Everyone should reduce prolonged outdoor exertion |
| 201-300 | Very Unhealthy | Purple | Avoid outdoor activities |
| 301-500 | Hazardous | Maroon | Health alert: Stay indoors |

---

## 🔄 Data Refresh

- **Current AQI:** Cached for 1 hour, auto-refreshed by scheduler
- **Predictions:** Generated on-demand using latest data
- **Historical Data:** Stored permanently, collected hourly

---

## ⚠️ Error Responses

All endpoints return standard HTTP status codes:

**400 Bad Request:**
```json
{
  "detail": "Invalid parameter value"
}
```

**404 Not Found:**
```json
{
  "detail": "City not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Testing

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📈 Rate Limits

Currently no rate limits. For production:
- Recommended: 100 requests/minute per IP
- Burst: 200 requests/minute

---

## 🔧 SDK Examples

### Python
```python
import requests

BASE_URL = "http://localhost:8000"

# Get current AQI
response = requests.get(f"{BASE_URL}/api/aqi/current/Mumbai")
data = response.json()
print(f"Current AQI: {data['aqi']}")

# Get predictions
response = requests.get(f"{BASE_URL}/api/aqi/predict/Mumbai")
predictions = response.json()
for pred in predictions['predictions']:
    print(f"{pred['hours']}h: {pred['predicted_aqi']}")
```

### JavaScript
```javascript
const BASE_URL = 'http://localhost:8000';

// Get current AQI
fetch(`${BASE_URL}/api/aqi/current/Mumbai`)
  .then(res => res.json())
  .then(data => console.log(`Current AQI: ${data.aqi}`));

// Get predictions
fetch(`${BASE_URL}/api/aqi/predict/Mumbai`)
  .then(res => res.json())
  .then(data => {
    data.predictions.forEach(pred => {
      console.log(`${pred.hours}h: ${pred.predicted_aqi}`);
    });
  });
```

### cURL
```bash
# Get current AQI
curl http://localhost:8000/api/aqi/current/Mumbai | jq

# Get predictions
curl http://localhost:8000/api/aqi/predict/Mumbai | jq '.predictions'
```

---

## 📞 Support

- **Documentation:** http://localhost:8000/docs
- **GitHub Issues:** [Repository URL]
- **Email:** support@lumair.example.com