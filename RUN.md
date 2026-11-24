# 🚀 Execution Guide: COVID-19 Enterprise Analytics Platform

This guide details how to build, run, seed, and test the multi-service analytics platform.

---

## 📋 Prerequisites

Ensure the following tools are installed and running on your host system:
- **Docker** (Engine v20.10+)
- **Docker Compose** (v2.0+)
- **GNU Make** (Optional, but recommended for helper commands)

---

## 🛠️ Step-by-Step Run Instructions

Open your terminal and navigate to the project root directory:
```powershell
cd "d:\Code\Covid-19 Project"
```

### 1. Build and Launch Containers
Build all required custom images (FastAPI backend, React frontend, Apache Airflow scheduler) and launch the stack in the background:
```bash
make build
make up
```
*If `make` is not available on your system, execute:*
```bash
docker-compose up --build -d
```

### 2. Apply Database Migrations
Create the normalized PostgreSQL schema structures by running Alembic migrations:
```bash
make migrate
```
*Manual fallback:*
```bash
docker-compose exec backend alembic upgrade head
```

### 3. Seed Database Dimensions & Security RBAC
Seed the database with initial calendar arrays, security roles, permission matrices, and default user accounts:
```bash
make seed
```
*Manual fallback:*
```bash
docker-compose exec -T postgres psql -U covid_admin -d covid19_analytics -f /docker-entrypoint-initdb.d/seeds/calendar.sql
docker-compose exec -T postgres psql -U covid_admin -d covid19_analytics -f /docker-entrypoint-initdb.d/seeds/roles.sql
```

### 4. Trigger Ingestion Pipeline (Initial Load)
Trigger the Python ETL pipeline manually to download the latest dataset from Our World in Data (OWID), execute quality checks, load data in batches of 5,000, and refresh materialized views:
```bash
make etl
```
*Manual fallback:*
```bash
docker-compose exec backend python etl/runner.py
```

---

## 🌐 Web Interface Endpoints

Once running, the following services are exposed:

| Service | Local Address | Access Credentials |
|---|---|---|
| **React Analytics Portal** | [http://localhost:3000](http://localhost:3000) | Username: `admin` <br> Password: `admin` |
| **FastAPI Swagger docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Log in using Swagger Authorize button |
| **Apache Airflow Web UI** | [http://localhost:8080](http://localhost:8080) | Username: `admin` <br> Password: `admin` |

---

## 🧪 Running Automated Tests

To execute the Pytest suite (which creates, runs, and rolls back transaction queries in an isolated `covid19_analytics_test` database):
```bash
make test
```
*Manual fallback:*
```bash
docker-compose exec backend pytest tests/ -v --cov=app
```

---

## 🛑 Stopping the Platform

To stop all active container streams, remove networks, and destroy local volumes:
```bash
make down
```
*Manual fallback:*
```bash
docker-compose down -v
```
