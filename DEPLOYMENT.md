# Lumair Deployment Guide

## 🚀 Production Deployment

### Step 1: Get API Keys

1. **OpenWeatherMap API:**
   - Sign up at https://openweathermap.org/api
   - Get your free API key
   
2. **WAQI API:**
   - Get token at https://aqicn.org/data-platform/token/

### Step 2: Deploy Database (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL
railway add postgresql

# Get connection string
railway variables
# Copy DATABASE_URL value
```

### Step 3: Deploy Backend (Render)

1. Push code to GitHub
2. Go to https://render.com
3. Create new **Web Service**
4. Connect your repo
5. Configure:
   - **Name:** lumair-backend
   - **Root Directory:** backend
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   ```
   DATABASE_URL=<from-railway>
   OPENWEATHER_API_KEY=<your-key>
   WAQI_API_KEY=<your-key>
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```
7. Deploy!

### Step 4: Initialize Database

```bash
# SSH into Render or run locally with production DB
python -c "from database import init_db; init_db()"

# Run initial data collection
python -c "from database import SessionLocal; from ml.data_collector import DataCollector; db = SessionLocal(); collector = DataCollector(db); collector.initialize_default_locations(); collector.collect_all_active_locations(); db.close()"
```

### Step 5: Train Initial Model

```bash
# After 24 hours of data collection
python ml/train_model.py
```

### Step 6: Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# From frontend directory
cd frontend
vercel login
vercel

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://your-backend.onrender.com
```

Or via Vercel Dashboard:
1. Import GitHub repo
2. Framework: Vite
3. Root Directory: frontend
4. Environment Variables:
   - `VITE_API_URL` = `https://your-backend.onrender.com`
5. Deploy!

## 🔧 Alternative: Deploy with Docker (Single VPS)

### Requirements
- VPS with Docker (DigitalOcean, AWS EC2, etc.)
- Domain name (optional)

### Setup

```bash
# SSH into VPS
ssh user@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone https://github.com/yourusername/lumair.git
cd lumair

# Create .env file
nano .env
# Add your API keys and config

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Initialize database
docker-compose exec backend python -c "from database import init_db; init_db()"

# Initialize locations
docker-compose exec backend python -c "from database import SessionLocal; from ml.data_collector import DataCollector; db = SessionLocal(); c = DataCollector(db); c.initialize_default_locations(); c.collect_all_active_locations(); db.close()"
```

### Setup Nginx Reverse Proxy

```bash
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/lumair
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lumair /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Model Training Schedule

Set up cron job for weekly model retraining:

```bash
# Edit crontab
crontab -e

# Add (runs every Sunday at 2 AM)
0 2 * * 0 cd /path/to/lumair/backend && python ml/train_model.py
```

## 🔄 Updates & Maintenance

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Or on Render/Vercel: push to main branch (auto-deploy)
```

## 📈 Monitoring

### Check Backend Health
```bash
curl https://your-backend.onrender.com/health
```

### Check Database
```bash
docker-compose exec postgres psql -U lumair -d lumair -c "SELECT COUNT(*) FROM aqi_records;"
```

### View Logs
```bash
# Docker
docker-compose logs -f backend

# Render: Use dashboard logs viewer
```

## 🛡️ Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set proper CORS_ORIGINS
- [ ] Rotate API keys regularly
- [ ] Enable database backups
- [ ] Set up monitoring/alerts

## 💰 Cost Estimate

**Free Tier:**
- Render: 750 hours/month (backend)
- Vercel: Unlimited (frontend)
- Railway: $5/month (database with 512MB)
- OpenWeather: 1000 calls/day free
- WAQI: Free

**Total: ~$5/month**

## 🆘 Troubleshooting

**Backend won't start:**
- Check DATABASE_URL is correct
- Verify API keys are set
- Check logs for errors

**Frontend can't connect:**
- Verify VITE_API_URL is correct
- Check CORS_ORIGINS on backend
- Ensure backend is running

**No predictions:**
- Wait for data collection (1+ hours)
- Train model: `python ml/train_model.py`
- Check model files exist in ml/models/

**Database connection fails:**
- Verify PostgreSQL is running
- Check connection string format
- Ensure database exists