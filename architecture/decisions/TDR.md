# ==============================================================================
# TECHNOLOGY DECISION RECORDS (TDR)
# Enterprise COVID-19 Analytics Platform
# ==============================================================================
# Format: TDR-NNN — Title
# Fields: Status | Date | Context | Decision | Rationale | Consequences
# ==============================================================================

# TDR Index

| ID | Title | Status | Date |
|---|---|---|---|
| TDR-001 | PostgreSQL over ClickHouse | ✅ Accepted | 2026-07-07 |
| TDR-002 | FastAPI over Django REST Framework | ✅ Accepted | 2026-07-07 |
| TDR-003 | React 19 SPA over Next.js | ✅ Accepted | 2026-07-07 |
| TDR-004 | Apache Airflow over Prefect | ✅ Accepted | 2026-07-07 |
| TDR-005 | Docker Compose over Kubernetes | ✅ Accepted | 2026-07-07 |
| TDR-006 | SQLAlchemy 2.x Async over Tortoise ORM | ✅ Accepted | 2026-07-07 |
| TDR-007 | Pydantic v2 for validation | ✅ Accepted | 2026-07-07 |
| TDR-008 | JWT with Refresh Tokens over Session Auth | ✅ Accepted | 2026-07-07 |
| TDR-009 | React Query over Redux for server state | ✅ Accepted | 2026-07-07 |
| TDR-010 | Alembic for DB Migrations | ✅ Accepted | 2026-07-07 |

---

## TDR-001 — PostgreSQL over ClickHouse

**Status**: Accepted  
**Date**: 2026-07-07

### Context
The OWID COVID-19 dataset contains approximately 200,000 rows per full refresh (6.7MB compressed). We evaluated both transactional (OLTP) and analytical (OLAP) databases.

### Decision
Use **PostgreSQL 16** as the sole database.

### Rationale
- Dataset is well within PostgreSQL's analytical capabilities at this scale
- Materialized Views + Window Functions satisfy all BI query patterns
- Eliminates operational complexity of running two separate database systems
- PostgreSQL 16's parallel query execution handles complex CTEs efficiently
- Native JSON support for flexible metadata storage
- pg_stat_statements provides query performance visibility
- Mature tooling ecosystem (pgAdmin, Alembic, SQLAlchemy)

### Consequences
- **Positive**: Single technology to operate, monitor, and back up
- **Positive**: All engineers familiar with PostgreSQL
- **Negative**: If dataset grows to 100M+ rows, migration to ClickHouse needed
- **Mitigation**: Materialized views and proper indexing defer this threshold

---

## TDR-002 — FastAPI over Django REST Framework

**Status**: Accepted  
**Date**: 2026-07-07

### Context
Backend API must serve analytical queries, handle authentication, manage ETL status, and generate Power BI embed tokens.

### Decision
Use **FastAPI 0.115** with **async SQLAlchemy**.

### Rationale
- Native async/await throughout avoids blocking I/O during long analytical queries
- Automatic OpenAPI + Swagger documentation satisfies API documentation requirements
- Pydantic v2 integration provides zero-cost request/response validation
- Dependency injection system is cleaner than DRF's class-based view hierarchy
- FastAPI benchmarks show 3–4× faster throughput than DRF for JSON-heavy APIs
- Type hints throughout improve IDE support and code quality

### Consequences
- **Positive**: Self-documenting API with zero extra effort
- **Positive**: Async DB queries allow higher concurrent load
- **Negative**: Smaller ecosystem than Django (fewer plug-ins)
- **Mitigation**: All required functionality (auth, CORS, rate limiting) is available as standard libraries

---

## TDR-003 — React 19 SPA over Next.js

**Status**: Accepted  
**Date**: 2026-07-07

### Context
The executive portal is an authenticated internal tool. SEO is not a consideration.

### Decision
Use **Vite + React 19** single-page application.

### Rationale
- Portal is behind authentication — server-side rendering provides no SEO benefit
- Simpler deployment: static build served by Nginx
- Faster development iterations with Vite HMR
- React 19 concurrent features (Suspense, useTransition) improve dashboard UX for heavy data loads
- No server infra required for the frontend tier
- Power BI SDK integrates cleanly in a browser SPA

### Consequences
- **Positive**: Frontend deployment is just an Nginx static file serve
- **Positive**: Simpler CI/CD pipeline (just `npm run build`)
- **Negative**: No built-in SSR if public-facing pages are added later
- **Mitigation**: Migrating to Next.js app router is straightforward if required

---

## TDR-004 — Apache Airflow over Prefect/Dagster

**Status**: Accepted  
**Date**: 2026-07-07

### Context
The ETL pipeline must run daily, support retries, send failure alerts, and provide a visual monitoring UI.

### Decision
Use **Apache Airflow 2.9** with CeleryExecutor.

### Rationale
- Industry standard in enterprise data engineering (Capgemini, Deloitte, TCS all standardize on Airflow)
- Rich operator ecosystem (PostgreSQL, HTTP, Email operators built-in)
- Battle-tested at scale in production environments
- Interview panels and hiring managers will recognise it
- Airflow UI satisfies ETL monitoring requirements out of the box
- Celery + Redis provides scalable task execution

### Consequences
- **Positive**: Maximum enterprise credibility
- **Positive**: Native retry, alerting, and SLA monitoring
- **Negative**: Airflow is heavyweight — adds Redis + 3 Airflow containers
- **Mitigation**: All within Docker Compose, resource impact is acceptable

---

## TDR-005 — Docker Compose over Kubernetes

**Status**: Accepted  
**Date**: 2026-07-07

### Context
Platform must be runnable locally (developer laptops) and in small cloud VMs without Kubernetes expertise.

### Decision
Use **Docker Compose V2** for orchestration, with Kubernetes manifests as a future deliverable.

### Rationale
- Single-node Docker Compose is production-viable for this dataset size
- Any developer with Docker Desktop can run the full stack locally
- Kubernetes would add 6–8 additional configuration files and operational overhead
- Cloud VMs (AWS EC2 t3.large, Azure B2ms) handle all services comfortably

### Consequences
- **Positive**: Dramatically simplified DevOps for the initial delivery
- **Positive**: Zero Kubernetes expertise required to operate
- **Negative**: No horizontal scaling without migration
- **Mitigation**: All services are 12-factor compliant — Kubernetes migration is additive, not rewrite

---

## TDR-006 — SQLAlchemy 2.x Async over Tortoise ORM

**Status**: Accepted  
**Date**: 2026-07-07

### Decision
Use **SQLAlchemy 2.x** with asyncpg driver.

### Rationale
- SQLAlchemy is the Python ORM standard with 15+ years of production hardening
- Version 2.x adds native async support without compromising on features
- Alembic (same authors) provides seamless migration management
- Tortoise ORM is less mature and has fewer community resources

---

## TDR-007 — Pydantic v2 for Validation

**Status**: Accepted  
**Date**: 2026-07-07

### Decision
Use **Pydantic v2** for all request/response schemas and ETL data validation.

### Rationale
- 5–50× faster than Pydantic v1 due to Rust-based core (pydantic-core)
- Deeply integrated into FastAPI
- Used for both API schemas AND ETL row validation — single validation library
- Strict mode catches type coercion bugs at the boundary

---

## TDR-008 — JWT with Refresh Tokens over Session Auth

**Status**: Accepted  
**Date**: 2026-07-07

### Decision
Use **JWT access tokens (30-min expiry) + JWT refresh tokens (7-day expiry)** stored in HttpOnly cookies.

### Rationale
- Stateless — scales to multiple backend workers without shared session store
- Short access token expiry limits breach exposure window
- Refresh tokens allow long user sessions without re-authentication
- HttpOnly cookie storage prevents XSS token theft (vs. localStorage)

---

## TDR-009 — React Query over Redux for Server State

**Status**: Accepted  
**Date**: 2026-07-07

### Decision
Use **TanStack React Query v5** for all server state, and **Zustand** for UI-only state (theme, filters).

### Rationale
- React Query handles caching, background refetching, loading/error states automatically
- Eliminates 80% of boilerplate that Redux requires for async data
- Zustand for local state is 1/10th the code of Redux Toolkit for the same result
- Separating server state from UI state is a cleaner architecture pattern

---

## TDR-010 — Alembic for DB Migrations

**Status**: Accepted  
**Date**: 2026-07-07

### Decision
Use **Alembic** for all database schema migrations.

### Rationale
- Native SQLAlchemy migration tool — zero impedance mismatch
- Supports auto-generated migrations from ORM model diffs
- Full upgrade/downgrade support for safe rollbacks
- Migration history is version-controlled
- Used in every serious Python/PostgreSQL production deployment
