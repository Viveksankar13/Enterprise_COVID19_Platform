# Enterprise COVID-19 Analytics Platform — System Architecture

## 1. Architectural Philosophy

This platform follows **Clean Architecture** principles combined with **Domain-Driven Design (DDD)** patterns, ensuring:

- **Separation of Concerns** — each layer has a single, well-defined responsibility
- **Dependency Inversion** — inner layers never depend on outer layers
- **Testability** — every component is independently testable
- **Scalability** — horizontal scaling at every tier
- **Auditability** — every data mutation is logged and traceable

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ENTERPRISE COVID-19 ANALYTICS PLATFORM                    │
│                          System Architecture v1.0                           │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  PRESENTATION TIER                                                       │
  │  ┌──────────────────────────────────┐  ┌────────────────────────────┐   │
  │  │   React 19 Executive Portal      │  │   Power BI Embedded         │   │
  │  │   (TypeScript + Tailwind CSS)    │  │   (Azure Power BI Service) │   │
  │  │                                  │  │                            │   │
  │  │  ┌──────────┐  ┌─────────────┐  │  │  ┌──────────────────────┐  │   │
  │  │  │Dashboard │  │ SQL Explorer│  │  │  │ Executive Dashboards  │  │   │
  │  │  │Analytics │  │ ETL Monitor │  │  │  │ KPI Cards & Maps      │  │   │
  │  │  │Auth/RBAC │  │ Admin Panel │  │  │  │ DAX-powered Analytics │  │   │
  │  │  └──────────┘  └─────────────┘  │  │  └──────────────────────┘  │   │
  │  └────────────────┬─────────────────┘  └────────────┬───────────────┘   │
  └───────────────────┼──────────────────────────────────┼───────────────────┘
                      │ HTTPS/JSON                        │ Embed Token
  ┌───────────────────▼──────────────────────────────────▼───────────────────┐
  │  API GATEWAY (Nginx Reverse Proxy)                                       │
  │  Rate Limiting  │  TLS Termination  │  Load Balancing  │  Compression    │
  └───────────────────────────────┬─────────────────────────────────────────┘
                                  │
  ┌───────────────────────────────▼──────────────────────────────────────────┐
  │  APPLICATION TIER                                                        │
  │  ┌────────────────────────────────────────────────────────────────────┐  │
  │  │  FastAPI Application (Python 3.12, async)                          │  │
  │  │                                                                    │  │
  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
  │  │  │ Analytics│  │ Auth     │  │ Admin    │  │ ETL Status       │  │  │
  │  │  │ Router   │  │ Router   │  │ Router   │  │ Router           │  │  │
  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │  │
  │  │       └─────────────┴─────────────┴─────────────────┘            │  │
  │  │                              │                                    │  │
  │  │  ┌───────────────────────────▼──────────────────────────────────┐ │  │
  │  │  │  Service Layer (Business Logic)                               │ │  │
  │  │  │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐   │ │  │
  │  │  │  │ Analytics  │  │ ETL Service  │  │  Auth Service      │   │ │  │
  │  │  │  │ Service    │  │              │  │  JWT / RBAC        │   │ │  │
  │  │  │  └────────────┘  └──────────────┘  └────────────────────┘   │ │  │
  │  │  └───────────────────────────┬──────────────────────────────────┘ │  │
  │  │                              │                                    │  │
  │  │  ┌───────────────────────────▼──────────────────────────────────┐ │  │
  │  │  │  Repository Layer (Data Access)                               │ │  │
  │  │  │  SQLAlchemy 2.x  │  Alembic Migrations  │  Connection Pool   │ │  │
  │  │  └───────────────────────────┬──────────────────────────────────┘ │  │
  │  └──────────────────────────────┼─────────────────────────────────────┘  │
  └─────────────────────────────────┼────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────▼────────────────────────────────────────┐
  │  DATA TIER                                                               │
  │  ┌────────────────────────────────────────────────────────────────────┐  │
  │  │  PostgreSQL 16                                                     │  │
  │  │                                                                    │  │
  │  │  ┌──────────────────────────────────────────────────────────────┐ │  │
  │  │  │  NORMALIZED TABLES                                           │ │  │
  │  │  │  countries │ daily_metrics │ vaccinations │ hospitalizations  │ │  │
  │  │  │  testing   │ demographics  │ calendar     │ metadata          │ │  │
  │  │  │  users     │ roles         │ audit_logs   │ etl_logs          │ │  │
  │  │  └──────────────────────────────────────────────────────────────┘ │  │
  │  │  ┌──────────────────────────────────────────────────────────────┐ │  │
  │  │  │  ANALYTICAL LAYER                                            │ │  │
  │  │  │  Views  │  Materialized Views  │  Window Functions           │ │  │
  │  │  │  CTEs   │  Partitioned Tables  │  Indexes                    │ │  │
  │  │  └──────────────────────────────────────────────────────────────┘ │  │
  │  └────────────────────────────────────────────────────────────────────┘  │
  └──────────────────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  ORCHESTRATION TIER (Apache Airflow)                                     │
  │                                                                          │
  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
  │  │ Download │───▶│ Validate │───▶│  Clean   │───▶│ Load PostgreSQL  │  │
  │  │  OWID    │    │  Schema  │    │Transform │    │ Refresh Views    │  │
  │  └──────────┘    └──────────┘    └──────────┘    └────────┬─────────┘  │
  │                                                            │            │
  │  ┌─────────────────────────────────────────────────────────▼──────────┐  │
  │  │  QA Checks  │  Generate Reports  │  Notify Success/Failure          │  │
  │  └────────────────────────────────────────────────────────────────────┘  │
  └──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Architecture

```
Our World in Data (OWID)
        │
        │  HTTPS GET (daily CSV download)
        ▼
┌────────────────────────────────────┐
│  ETL Extractor                     │
│  - Requests library                │
│  - Checksum validation             │
│  - Schema drift detection          │
│  - Raw file storage with timestamp │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  ETL Validator                     │
│  - Pydantic model validation       │
│  - Range checks                    │
│  - Referential integrity checks    │
│  - Missing country detection       │
│  - Metric plausibility checks      │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  ETL Transformer                   │
│  - Pandas data cleaning            │
│  - Outlier detection (IQR)         │
│  - Date normalization              │
│  - Metric derivation               │
│    • 7-day rolling averages        │
│    • Per-million calculations      │
│    • Case Fatality Rate (CFR)      │
│    • Vaccination effectiveness     │
│  - Country ISO code mapping        │
│  - Continent classification        │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  ETL Loader                        │
│  - Upsert with conflict resolution │
│  - Batch inserts (5,000 rows)      │
│  - Transaction management          │
│  - Rollback on failure             │
│  - ETL audit log entry             │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  PostgreSQL Database               │
│  - Normalized tables updated       │
│  - Materialized views refreshed    │
│  - Analytical views auto-updated   │
└────────────────┬───────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│  FastAPI Backend                   │
│  - Reads from views & tables       │
│  - Caches hot queries (Redis)      │
│  - Serves JSON to React Portal     │
│  - Serves embed tokens to Power BI │
└────────────────────────────────────┘
```

---

## 4. Authentication & Authorization Architecture

```
┌──────────────┐         ┌───────────────────────┐
│   Browser    │         │   FastAPI Backend      │
│              │──POST──▶│  /auth/login           │
│              │◀──JWT───│  - bcrypt verify       │
│              │         │  - generate access +   │
│              │         │    refresh tokens      │
│              │         └───────────────────────┘
│              │
│  Subsequent  │         ┌───────────────────────┐
│  API calls   │──JWT──▶│   Auth Middleware      │
│  with Bearer │         │  - Validate signature  │
│              │         │  - Check expiry        │
│              │         │  - Extract user_id +   │
│              │         │    roles from payload  │
│              │         └──────────┬────────────┘
│              │                    │
│              │         ┌──────────▼────────────┐
│              │         │  RBAC Guard            │
│              │         │  - Endpoint requires   │
│              │         │    @requires_role()    │
│              │         │  - Roles: admin,       │
│              │         │    analyst, viewer,    │
│              │         │    api_user            │
│              │         └───────────────────────┘
└──────────────┘
```

---

## 5. Frontend Component Architecture

```
frontend/src/
│
├── App.tsx                           # Root application
├── main.tsx                          # Entry point
│
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx              # Master layout wrapper
│   │   ├── Sidebar.tsx               # Role-based navigation sidebar
│   │   ├── TopBar.tsx                # Header with search & user menu
│   │   └── Footer.tsx                # Platform footer
│   │
│   ├── ui/                           # Design system primitives
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Skeleton.tsx              # Loading skeletons
│   │   ├── Alert.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx                 # Sortable, paginated table
│   │   ├── Select.tsx
│   │   ├── Input.tsx
│   │   └── Tooltip.tsx
│   │
│   ├── charts/                       # Recharts wrappers
│   │   ├── LineChart.tsx
│   │   ├── AreaChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── ScatterChart.tsx
│   │   ├── KPICard.tsx
│   │   └── GeoHeatmap.tsx
│   │
│   └── powerbi/
│       ├── PowerBIEmbed.tsx          # Embed wrapper
│       └── EmbedTokenProvider.tsx    # Token management
│
├── pages/
│   ├── Home.tsx
│   ├── dashboard/
│   │   ├── ExecutiveDashboard.tsx
│   │   ├── GlobalStatistics.tsx
│   │   └── CountryComparison.tsx
│   ├── analytics/
│   │   ├── VaccinationAnalytics.tsx
│   │   ├── MortalityAnalytics.tsx
│   │   ├── TestingDashboard.tsx
│   │   ├── HospitalDashboard.tsx
│   │   └── TrendAnalysis.tsx
│   ├── admin/
│   │   ├── AdminDashboard.tsx
│   │   ├── ETLStatus.tsx
│   │   ├── PipelineHealth.tsx
│   │   └── UserManagement.tsx
│   └── auth/
│       ├── Login.tsx
│       └── Unauthorized.tsx
│
├── hooks/                            # Custom React hooks
│   ├── useAuth.ts
│   ├── useCountries.ts
│   ├── useMetrics.ts
│   ├── useTheme.ts
│   └── usePagination.ts
│
├── services/                         # Axios API clients
│   ├── api.ts                        # Axios instance + interceptors
│   ├── analyticsService.ts
│   ├── countryService.ts
│   ├── authService.ts
│   └── adminService.ts
│
├── stores/                           # Zustand state stores
│   ├── authStore.ts
│   ├── themeStore.ts
│   └── filterStore.ts
│
├── types/                            # TypeScript interfaces
│   ├── analytics.types.ts
│   ├── country.types.ts
│   ├── auth.types.ts
│   └── api.types.ts
│
├── contexts/                         # React contexts
│   ├── AuthContext.tsx
│   └── ThemeContext.tsx
│
└── utils/
    ├── formatters.ts                 # Number/date formatters
    ├── validators.ts
    └── constants.ts
```

---

## 6. Database Layer Architecture

```
PostgreSQL 16 Schema Design

┌─────────────────────────────────────────────────────────────────────────┐
│                          REFERENCE LAYER                                │
│  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐ │
│  │   countries     │   │    calendar       │   │    metadata         │ │
│  │  iso_code (PK)  │   │  date (PK)        │   │  key (PK)           │ │
│  │  country_name   │   │  year             │   │  value              │ │
│  │  continent      │   │  quarter          │   │  updated_at         │ │
│  │  region         │   │  month            │   │                     │ │
│  │  income_group   │   │  week_of_year     │   │                     │ │
│  └────────┬────────┘   └──────────────────┘   └─────────────────────┘ │
└───────────┼────────────────────────────────────────────────────────────┘
            │ FK
┌───────────▼────────────────────────────────────────────────────────────┐
│                            FACT LAYER                                   │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │  daily_metrics (iso_code, date) COMPOSITE PK                       ││
│  │  new_cases | total_cases | new_deaths | total_deaths               ││
│  │  reproduction_rate | stringency_index                              ││
│  │  new_cases_smoothed | new_deaths_smoothed                          ││
│  └──────────────────────────────────┬─────────────────────────────────┘│
│                                     │ (iso_code, date) FK              │
│  ┌───────────────────┐  ┌───────────▼──────────┐  ┌─────────────────┐ │
│  │  vaccinations     │  │  testing             │  │ hospitalizations │ │
│  │  iso_code + date  │  │  iso_code + date     │  │ iso_code + date  │ │
│  │  people_vaccinated│  │  total_tests         │  │ icu_patients     │ │
│  │  fully_vaccinated │  │  positive_rate       │  │ hosp_patients    │ │
│  │  boosters         │  │  tests_per_case      │  │ weekly_admissions│ │
│  └───────────────────┘  └──────────────────────┘  └─────────────────┘ │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  demographics (iso_code)  ONE-TO-ONE                            │  │
│  │  population | population_density | median_age | gdp_per_capita  │  │
│  │  life_expectancy | human_development_index | extreme_poverty     │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                          SECURITY LAYER                                 │
│  ┌──────────────────┐   ┌──────────────────┐   ┌───────────────────┐  │
│  │  users           │   │  roles           │   │  permissions      │  │
│  │  user_id (PK)    │   │  role_id (PK)    │   │  permission_id    │  │
│  │  email (UNIQUE)  │   │  name            │   │  resource         │  │
│  │  password_hash   │   │  description     │   │  action           │  │
│  │  role_id (FK)    │   │  created_at      │   │  role_id (FK)     │  │
│  │  is_active       │   └──────────────────┘   └───────────────────┘  │
│  └──────────────────┘                                                  │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                          OPERATIONAL LAYER                              │
│  ┌──────────────────────────────┐   ┌──────────────────────────────┐  │
│  │  etl_logs                    │   │  audit_logs                  │  │
│  │  run_id (PK, UUID)           │   │  log_id (PK)                 │  │
│  │  pipeline_name               │   │  user_id (FK)                │  │
│  │  status (RUNNING/OK/FAILED)  │   │  action                      │  │
│  │  rows_inserted               │   │  resource                    │  │
│  │  rows_updated                │   │  ip_address                  │  │
│  │  rows_rejected               │   │  timestamp                   │  │
│  │  duration_seconds            │   │  metadata (JSONB)            │  │
│  │  error_message               │   │                              │  │
│  │  started_at / completed_at   │   │                              │  │
│  └──────────────────────────────┘   └──────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Deployment Architecture

```
Production Target (Docker Compose / Docker Swarm)

┌────────────────────────────────────────────────────────────────────────────┐
│  External Traffic                                                          │
│           HTTPS :443                                                       │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────────┐
│  Nginx (Reverse Proxy + Static Serving)                                    │
│  - TLS termination                                                         │
│  - Serve React build at /                                                  │
│  - Proxy /api/* → FastAPI :8000                                            │
│  - Rate limiting: 100 req/min per IP                                       │
│  - Gzip compression                                                        │
└──────────────────────────────────┬─────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼──────────────────────────┐
           │                       │                          │
┌──────────▼──────────┐  ┌─────────▼────────────┐  ┌────────▼──────────────┐
│  FastAPI :8000       │  │  Airflow Web :8080   │  │  pgAdmin :5050        │
│  4 Gunicorn workers  │  │  Scheduler           │  │  DB Management UI     │
│  Async endpoints     │  │  Celery Worker       │  │                       │
└──────────┬──────────┘  └─────────┬────────────┘  └───────────────────────┘
           │                       │
           └──────────┬────────────┘
                      │
        ┌─────────────┼───────────────────┐
        │             │                   │
┌───────▼──────┐ ┌────▼──────────┐ ┌─────▼──────────┐
│ PostgreSQL   │ │ Redis :6379   │ │ Volume Mounts  │
│ :5432        │ │ Celery Broker │ │ /data          │
│ Primary DB   │ │               │ │ /logs          │
└──────────────┘ └───────────────┘ └────────────────┘
```

---

## 8. Technology Decision Records (TDR)

### TDR-001: PostgreSQL over ClickHouse
**Decision**: Use PostgreSQL 16 as primary database  
**Rationale**: COVID-19 dataset is ~200MB — well within PostgreSQL's sweet spot. Advanced SQL features (window functions, CTEs, materialized views) meet all analytical requirements without introducing OLAP complexity. Simplifies DevOps.

### TDR-002: FastAPI over Django REST Framework
**Decision**: FastAPI with async SQLAlchemy  
**Rationale**: Native async support matches our I/O-bound analytical queries. Automatic OpenAPI docs. Pydantic v2 for zero-overhead validation. 3× faster request throughput vs DRF in benchmarks.

### TDR-003: React 19 over Next.js
**Decision**: Vite + React 19 SPA  
**Rationale**: Portal is behind auth — SEO not required. Simpler deployment (static files via Nginx). Faster development cycle. React 19 concurrent features improve dashboard rendering.

### TDR-004: Apache Airflow over Prefect/Dagster
**Decision**: Apache Airflow 2.9  
**Rationale**: Industry standard in consulting engagements. Strong enterprise adoption. Rich operator ecosystem. Familiar to most data engineering teams.

### TDR-005: Docker Compose over Kubernetes
**Decision**: Docker Compose for initial deployment  
**Rationale**: Platform must be runnable locally and in small VMs. Docker Compose V2 is production-viable for single-node deployments. Kubernetes manifests are a Phase 2 deliverable if horizontal scaling is required.
