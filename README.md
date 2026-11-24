# 🦠 Enterprise COVID-19 Analytics Platform

[![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/your-org/covid19-analytics/ci.yml?branch=main&label=CI%2FCD&style=for-the-badge)](https://github.com/your-org/covid19-analytics/actions)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)](https://docs.docker.com/compose/)
[![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.9-017CEE?style=for-the-badge&logo=apache-airflow)](https://airflow.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **A production-grade, full-stack enterprise analytics platform** for global COVID-19 intelligence — engineered to the standards of a Fortune 500 consulting engagement.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Module Documentation](#-module-documentation)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [ETL Pipeline](#-etl-pipeline)
- [Power BI Integration](#-power-bi-integration)
- [Authentication & RBAC](#-authentication--rbac)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)

---

## 🌐 Overview

The **Enterprise COVID-19 Analytics Platform** is a comprehensive business intelligence and data engineering solution that ingests, processes, and visualizes the complete Our World in Data COVID-19 dataset. It is engineered to consulting-grade standards, featuring:

| Capability | Implementation |
|---|---|
| **Data Ingestion** | Automated ETL via Apache Airflow DAGs |
| **Data Storage** | Normalized PostgreSQL schema with analytical views |
| **Backend API** | FastAPI with async endpoints, JWT auth, RBAC |
| **Frontend Portal** | React 19 + TypeScript + Tailwind CSS executive portal |
| **Business Intelligence** | Embedded Microsoft Power BI dashboards |
| **Deployment** | Docker Compose with full orchestration |
| **CI/CD** | GitHub Actions pipeline |
| **Monitoring** | Pipeline health, ETL audit logs, API observability |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE COVID-19 ANALYTICS PLATFORM           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────┐                      │
│  │  Our World in    │    │   Apache Airflow  │                      │
│  │  Data (OWID)     │───▶│   Orchestration   │                      │
│  │  Dataset (CSV)   │    │   (Scheduled ETL) │                      │
│  └──────────────────┘    └────────┬─────────┘                      │
│                                   │                                  │
│                    ┌──────────────▼──────────────┐                  │
│                    │       Python ETL Engine       │                  │
│                    │  Download → Validate →        │                  │
│                    │  Clean → Transform → Load     │                  │
│                    └──────────────┬──────────────┘                  │
│                                   │                                  │
│                    ┌──────────────▼──────────────┐                  │
│                    │        PostgreSQL 16          │                  │
│                    │  ┌──────────────────────┐   │                  │
│                    │  │  Normalized Tables   │   │                  │
│                    │  │  Analytical Views    │   │                  │
│                    │  │  Materialized Views  │   │                  │
│                    │  │  Audit Logs          │   │                  │
│                    │  └──────────────────────┘   │                  │
│                    └──────────────┬──────────────┘                  │
│                                   │                                  │
│              ┌────────────────────▼────────────────────┐            │
│              │           FastAPI Backend                │            │
│              │  ┌──────────┐  ┌──────────┐            │            │
│              │  │Analytics │  │Auth/RBAC │            │            │
│              │  │  APIs    │  │  Layer   │            │            │
│              │  └──────────┘  └──────────┘            │            │
│              └────────────────────┬────────────────────┘            │
│                                   │                                  │
│         ┌─────────────────────────▼──────────────────────────┐      │
│         │              React 19 Executive Portal              │      │
│         │  ┌──────────────┐  ┌──────────────┐               │      │
│         │  │  Dashboards  │  │  Power BI    │               │      │
│         │  │  Charts      │  │  Embedded    │               │      │
│         │  └──────────────┘  └──────────────┘               │      │
│         └────────────────────────────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

For the full architecture diagram see [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md).

---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI Framework |
| TypeScript | 5.x | Type Safety |
| Vite | 6.x | Build Tool |
| Tailwind CSS | 4.x | Styling |
| React Router | 7 | Client Routing |
| React Query | 5 | Server State |
| Axios | 1.x | HTTP Client |
| Recharts | 2.x | Lightweight Charts |
| Framer Motion | 12.x | Animations |
| Power BI Embedded | SDK | BI Dashboards |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Runtime |
| FastAPI | 0.115 | API Framework |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | DB Migrations |
| Pydantic | 2.x | Data Validation |
| psycopg2 | 2.9 | PostgreSQL Driver |
| Pandas | 2.x | Data Processing |
| NumPy | 2.x | Numerical Computing |
| python-jose | 3.x | JWT |
| passlib | 1.x | Password Hashing |

### Infrastructure
| Technology | Version | Purpose |
|---|---|---|
| PostgreSQL | 16 | Primary Database |
| Apache Airflow | 2.9 | Workflow Orchestration |
| Docker | Latest | Containerization |
| Docker Compose | V2 | Local Orchestration |
| Redis | 7 | Airflow Celery Broker |
| Nginx | Latest | Reverse Proxy |

---

## 📂 Project Structure

```
covid19-analytics/
├── 📁 frontend/                    # React 19 + TypeScript Portal
├── 📁 backend/                     # FastAPI Application
├── 📁 database/                    # SQL Scripts & Migrations
├── 📁 airflow/                     # DAGs & ETL Orchestration
├── 📁 etl/                         # Python ETL Engine
├── 📁 powerbi/                     # Power BI Templates & Docs
├── 📁 docker/                      # Dockerfiles
├── 📁 tests/                       # Test Suites
├── 📁 scripts/                     # Utility Scripts
├── 📁 docs/                        # Full Documentation
├── 📁 architecture/                # Architecture Diagrams
├── 📁 assets/                      # Static Assets
├── 📄 docker-compose.yml           # Full Stack Orchestration
├── 📄 docker-compose.dev.yml       # Development Override
├── 📄 .env.example                 # Environment Template
├── 📄 .gitignore                   # Git Ignore Rules
├── 📄 Makefile                     # Developer Convenience
└── 📄 README.md                    # This File
```

See [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) for full annotated tree.

---

## 🚀 Quick Start

### Prerequisites

- Docker 24+ and Docker Compose V2
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)
- PostgreSQL 16+ (if running without Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/covid19-analytics.git
cd covid19-analytics
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Launch with Docker Compose

```bash
docker compose up -d
```

### 4. Initialize the Database

```bash
make db-migrate
make db-seed
```

### 5. Trigger Initial ETL

```bash
make etl-run
```

### 6. Access the Platform

| Service | URL |
|---|---|
| React Portal | http://localhost:3000 |
| FastAPI Docs | http://localhost:8000/docs |
| Airflow UI | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |

---

## 📚 Module Documentation

- [Frontend Architecture](docs/frontend/FRONTEND.md)
- [Backend Architecture](docs/backend/BACKEND.md)
- [Database Schema](docs/database/SCHEMA.md)
- [ETL Pipeline](docs/etl/ETL_PIPELINE.md)
- [Airflow DAGs](docs/airflow/AIRFLOW.md)
- [Power BI Setup](docs/powerbi/POWERBI.md)
- [API Reference](docs/api/API_REFERENCE.md)
- [Authentication](docs/auth/AUTHENTICATION.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT.md)
- [Testing Guide](docs/testing/TESTING.md)

---

## 🔐 Authentication & RBAC

| Role | Permissions |
|---|---|
| `admin` | Full access, user management, ETL control |
| `analyst` | Read dashboards, run queries, export data |
| `viewer` | Read-only dashboard access |
| `api_user` | API key access for programmatic usage |

---

## 🐳 Deployment

See the full [Deployment Guide](docs/deployment/DEPLOYMENT.md) for:
- Local Docker Compose
- Production Docker Swarm
- AWS ECS / Azure ACI deployment
- Environment hardening

---

## 🧪 Testing

```bash
# Run all tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# API tests
make test-api
```

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🏢 Built To Consulting Standards

> This platform was engineered following patterns from enterprise consulting engagements at Capgemini, Deloitte, and Accenture — featuring clean architecture, separation of concerns, comprehensive logging, audit trails, and production-grade deployment.
