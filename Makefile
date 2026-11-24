# ── COVID-19 Analytics Platform Orchestration Makefile ────────────────────────

.PHONY: help build up down restart logs test migrate seed etl clean

help:
	@echo "========================================================================"
	@echo "               COVID-19 Analytics Platform Makefile                    "
	@echo "========================================================================"
	@echo "  build         Build all service container images"
	@echo "  up            Launch the multi-container platform in background"
	@echo "  down          Stop and remove all active containers and networks"
	@echo "  restart       Restart all services"
	@echo "  logs          Tail logs from all active containers"
	@echo "  test          Run backend python test suite using pytest"
	@echo "  migrate       Run database Alembic migrations"
	@echo "  seed          Populate database with initial calendar and security seeds"
	@echo "  etl           Manually trigger python ETL extraction run"
	@echo "  clean         Wipe temp python pycaches and log outputs"
	@echo "========================================================================"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "🚀 Platform launched successfully!"
	@echo "   - React Portal: http://localhost:3000"
	@echo "   - FastAPI API:  http://localhost:8000/docs"
	@echo "   - Airflow UI:   http://localhost:8080 (admin/admin)"

down:
	docker-compose down -v

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	docker-compose exec backend pytest tests/ -v --cov=app

migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec -T postgres psql -U covid_admin -d covid19_analytics -f /docker-entrypoint-initdb.d/seeds/calendar.sql
	docker-compose exec -T postgres psql -U covid_admin -d covid19_analytics -f /docker-entrypoint-initdb.d/seeds/roles.sql
	@echo "✅ Database seeded successfully."

etl:
	docker-compose exec backend python etl/runner.py

clean:
	rm -rf backend/app/__pycache__
	rm -rf backend/app/*/__pycache__
	rm -rf backend/app/*/*/__pycache__
	rm -rf etl/__pycache__
	rm -rf etl/*/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	@echo "🧹 Clean operation completed."
