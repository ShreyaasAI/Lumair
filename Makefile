.PHONY: help setup start stop restart logs clean test train db-init

help:
	@echo "Lumair - Available Commands"
	@echo "============================"
	@echo "make setup      - Initial setup with Docker"
	@echo "make start      - Start all services"
	@echo "make stop       - Stop all services"
	@echo "make restart    - Restart all services"
	@echo "make logs       - View logs"
	@echo "make test       - Test API endpoints"
	@echo "make train      - Train ML model"
	@echo "make db-init    - Initialize database"
	@echo "make clean      - Remove containers and volumes"

setup:
	@bash setup.sh

start:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend:  http://localhost:8000"

stop:
	docker-compose down
	@echo "✅ Services stopped"

restart:
	docker-compose restart
	@echo "✅ Services restarted"

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	@echo "✅ Containers and volumes removed"

test:
	@bash test_api.sh

train:
	docker-compose exec backend python ml/train_model.py

db-init:
	docker-compose exec backend python -c "from database import init_db; init_db()"
	@echo "✅ Database initialized"

collect-data:
	docker-compose exec backend python -c "from database import SessionLocal; from ml.data_collector import DataCollector; db = SessionLocal(); c = DataCollector(db); c.collect_all_active_locations(); db.close()"
	@echo "✅ Data collection complete"

dev-backend:
	cd backend && uvicorn main:app --reload

dev-frontend:
	cd frontend && npm run dev