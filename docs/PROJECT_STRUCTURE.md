# Enterprise COVID-19 Analytics Platform — Full Project Structure

```
covid19-analytics/
│
├── 📄 README.md                              # Project overview & quick start
├── 📄 Makefile                               # Developer convenience commands
├── 📄 .env.example                           # Environment template (copy → .env)
├── 📄 .gitignore                             # Git ignore rules
├── 📄 docker-compose.yml                     # Full stack orchestration
├── 📄 docker-compose.dev.yml                 # Development overrides
├── 📄 docker-compose.test.yml                # Test environment
│
├── 📁 frontend/                              # React 19 + TypeScript Portal
│   ├── 📄 package.json
│   ├── 📄 tsconfig.json
│   ├── 📄 tsconfig.app.json
│   ├── 📄 vite.config.ts
│   ├── 📄 tailwind.config.ts
│   ├── 📄 postcss.config.js
│   ├── 📄 .eslintrc.json
│   ├── 📄 index.html
│   │
│   ├── 📁 public/
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   └── 📁 src/
│       ├── 📄 main.tsx                       # Entry point
│       ├── 📄 App.tsx                        # Root component & router
│       ├── 📄 index.css                      # Global styles + Tailwind
│       │
│       ├── 📁 components/
│       │   ├── 📁 layout/
│       │   │   ├── AppShell.tsx              # Master layout wrapper
│       │   │   ├── Sidebar.tsx               # Collapsible navigation
│       │   │   ├── TopBar.tsx                # Header, search, user menu
│       │   │   └── Footer.tsx
│       │   │
│       │   ├── 📁 ui/                        # Design system primitives
│       │   │   ├── Button.tsx
│       │   │   ├── Card.tsx
│       │   │   ├── Badge.tsx
│       │   │   ├── Skeleton.tsx
│       │   │   ├── Alert.tsx
│       │   │   ├── Modal.tsx
│       │   │   ├── Table.tsx
│       │   │   ├── Select.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Tabs.tsx
│       │   │   ├── Tooltip.tsx
│       │   │   └── Spinner.tsx
│       │   │
│       │   ├── 📁 charts/
│       │   │   ├── LineChart.tsx
│       │   │   ├── AreaChart.tsx
│       │   │   ├── BarChart.tsx
│       │   │   ├── ScatterChart.tsx
│       │   │   ├── KPICard.tsx
│       │   │   └── GeoHeatmap.tsx
│       │   │
│       │   ├── 📁 tables/
│       │   │   ├── DataTable.tsx             # Reusable sortable/paginated table
│       │   │   └── CountryTable.tsx
│       │   │
│       │   ├── 📁 forms/
│       │   │   ├── CountryFilter.tsx
│       │   │   ├── DateRangePicker.tsx
│       │   │   └── SearchBar.tsx
│       │   │
│       │   └── 📁 powerbi/
│       │       ├── PowerBIEmbed.tsx          # Power BI SDK embed wrapper
│       │       └── EmbedTokenProvider.tsx
│       │
│       ├── 📁 pages/
│       │   ├── 📄 Home.tsx
│       │   ├── 📁 dashboard/
│       │   │   ├── ExecutiveDashboard.tsx
│       │   │   ├── GlobalStatistics.tsx
│       │   │   └── CountryComparison.tsx
│       │   ├── 📁 analytics/
│       │   │   ├── VaccinationAnalytics.tsx
│       │   │   ├── MortalityAnalytics.tsx
│       │   │   ├── TestingDashboard.tsx
│       │   │   ├── HospitalDashboard.tsx
│       │   │   └── TrendAnalysis.tsx
│       │   ├── 📁 admin/
│       │   │   ├── AdminDashboard.tsx
│       │   │   ├── ETLStatus.tsx
│       │   │   ├── PipelineHealth.tsx
│       │   │   └── UserManagement.tsx
│       │   └── 📁 auth/
│       │       ├── Login.tsx
│       │       └── Unauthorized.tsx
│       │
│       ├── 📁 hooks/
│       │   ├── useAuth.ts
│       │   ├── useCountries.ts
│       │   ├── useMetrics.ts
│       │   ├── useTheme.ts
│       │   └── usePagination.ts
│       │
│       ├── 📁 services/
│       │   ├── api.ts                        # Axios base instance
│       │   ├── analyticsService.ts
│       │   ├── countryService.ts
│       │   ├── authService.ts
│       │   └── adminService.ts
│       │
│       ├── 📁 stores/
│       │   ├── authStore.ts
│       │   ├── themeStore.ts
│       │   └── filterStore.ts
│       │
│       ├── 📁 types/
│       │   ├── analytics.types.ts
│       │   ├── country.types.ts
│       │   ├── auth.types.ts
│       │   └── api.types.ts
│       │
│       ├── 📁 contexts/
│       │   ├── AuthContext.tsx
│       │   └── ThemeContext.tsx
│       │
│       └── 📁 utils/
│           ├── formatters.ts
│           ├── validators.ts
│           └── constants.ts
│
├── 📁 backend/                               # FastAPI Application
│   ├── 📄 requirements.txt                   # Python dependencies
│   ├── 📄 requirements-dev.txt               # Dev/test dependencies
│   ├── 📄 pyproject.toml                     # Tool configuration (ruff, mypy)
│   ├── 📄 alembic.ini                        # Alembic configuration
│   │
│   ├── 📁 app/
│   │   ├── 📄 main.py                        # FastAPI app factory
│   │   │
│   │   ├── 📁 api/
│   │   │   └── 📁 v1/
│   │   │       ├── 📄 router.py              # API v1 root router
│   │   │       ├── 📁 endpoints/
│   │   │       │   ├── analytics.py
│   │   │       │   ├── countries.py
│   │   │       │   ├── vaccinations.py
│   │   │       │   ├── testing.py
│   │   │       │   ├── hospitalizations.py
│   │   │       │   ├── forecasts.py
│   │   │       │   ├── kpis.py
│   │   │       │   ├── admin.py
│   │   │       │   ├── auth.py
│   │   │       │   ├── etl.py
│   │   │       │   ├── health.py
│   │   │       │   └── powerbi.py
│   │   │       └── 📁 dependencies/
│   │   │           ├── auth.py               # JWT dependency injection
│   │   │           ├── database.py           # DB session dependency
│   │   │           └── pagination.py
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── config.py                     # Pydantic settings
│   │   │   ├── logging.py                    # Structured logging setup
│   │   │   ├── exceptions.py                 # Custom exception classes
│   │   │   └── constants.py
│   │   │
│   │   ├── 📁 database/
│   │   │   ├── base.py                       # SQLAlchemy base
│   │   │   ├── session.py                    # Async session factory
│   │   │   └── init_db.py                    # DB initialization
│   │   │
│   │   ├── 📁 models/                        # SQLAlchemy ORM models
│   │   │   ├── country.py
│   │   │   ├── daily_metric.py
│   │   │   ├── vaccination.py
│   │   │   ├── testing.py
│   │   │   ├── hospitalization.py
│   │   │   ├── demographic.py
│   │   │   ├── calendar.py
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── etl_log.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── 📁 schemas/                       # Pydantic request/response models
│   │   │   ├── analytics.py
│   │   │   ├── country.py
│   │   │   ├── vaccination.py
│   │   │   ├── testing.py
│   │   │   ├── hospitalization.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   └── common.py
│   │   │
│   │   ├── 📁 repositories/                  # Data access layer
│   │   │   ├── base.py                       # Generic CRUD repository
│   │   │   ├── country_repository.py
│   │   │   ├── analytics_repository.py
│   │   │   ├── vaccination_repository.py
│   │   │   ├── etl_repository.py
│   │   │   └── user_repository.py
│   │   │
│   │   ├── 📁 services/                      # Business logic layer
│   │   │   ├── analytics_service.py
│   │   │   ├── country_service.py
│   │   │   ├── vaccination_service.py
│   │   │   ├── forecast_service.py
│   │   │   ├── kpi_service.py
│   │   │   ├── powerbi_service.py
│   │   │   └── etl_service.py
│   │   │
│   │   ├── 📁 middleware/
│   │   │   ├── cors.py
│   │   │   ├── logging.py
│   │   │   ├── rate_limiting.py
│   │   │   └── request_id.py
│   │   │
│   │   ├── 📁 authentication/
│   │   │   ├── jwt_handler.py
│   │   │   ├── password_handler.py
│   │   │   └── rbac.py
│   │   │
│   │   ├── 📁 analytics/                     # Advanced SQL analytics
│   │   │   ├── window_functions.py
│   │   │   ├── kpi_calculator.py
│   │   │   ├── trend_detector.py
│   │   │   └── forecast_engine.py
│   │   │
│   │   └── 📁 utils/
│   │       ├── date_utils.py
│   │       ├── country_utils.py
│   │       ├── number_utils.py
│   │       └── cache.py
│   │
│   ├── 📁 migrations/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── 📁 versions/
│   │       ├── 001_initial_schema.py
│   │       ├── 002_add_analytical_views.py
│   │       └── 003_add_audit_system.py
│   │
│   └── 📁 tests/
│       ├── conftest.py
│       ├── 📁 unit/
│       │   ├── 📁 api/
│       │   ├── 📁 services/
│       │   └── 📁 crud/
│       ├── 📁 integration/
│       ├── 📁 api/
│       ├── 📁 etl/
│       └── 📁 fixtures/
│
├── 📁 etl/                                   # Python ETL Engine
│   ├── 📄 runner.py                          # ETL orchestration entry point
│   ├── 📄 config.py                          # ETL configuration
│   │
│   ├── 📁 extractors/
│   │   ├── owid_extractor.py                 # OWID CSV downloader
│   │   └── schema_detector.py                # Column drift detection
│   │
│   ├── 📁 validators/
│   │   ├── data_validator.py                 # Pydantic validation
│   │   ├── range_validator.py                # Statistical range checks
│   │   └── integrity_validator.py            # Referential integrity
│   │
│   ├── 📁 transformers/
│   │   ├── cleaner.py                        # Missing value handling
│   │   ├── normalizer.py                     # Data normalization
│   │   ├── metric_calculator.py              # Derived metrics
│   │   └── country_mapper.py                 # ISO code mapping
│   │
│   ├── 📁 loaders/
│   │   ├── postgres_loader.py                # Bulk upsert to PostgreSQL
│   │   └── view_refresher.py                 # Materialized view refresh
│   │
│   ├── 📁 reporters/
│   │   ├── audit_reporter.py                 # ETL audit log generator
│   │   └── quality_reporter.py               # Data quality report
│   │
│   └── 📁 utils/
│       ├── checksum.py
│       └── retry.py
│
├── 📁 database/                              # SQL Scripts
│   ├── 📁 schemas/
│   │   ├── 01_extensions.sql
│   │   ├── 02_tables.sql
│   │   ├── 03_constraints.sql
│   │   └── 04_indexes.sql
│   │
│   ├── 📁 views/
│   │   ├── 01_analytical_views.sql
│   │   ├── 02_materialized_views.sql
│   │   └── 03_kpi_views.sql
│   │
│   ├── 📁 stored_procedures/
│   │   ├── refresh_all_views.sql
│   │   └── calculate_kpis.sql
│   │
│   ├── 📁 seeds/
│   │   ├── countries.csv
│   │   ├── calendar.sql
│   │   └── roles.sql
│   │
│   └── 📁 scripts/
│       ├── backup.sh
│       └── restore.sh
│
├── 📁 airflow/                               # Apache Airflow
│   ├── 📄 requirements.txt                   # Airflow provider packages
│   │
│   ├── 📁 dags/
│   │   ├── covid19_etl_pipeline.py           # Main daily ETL DAG
│   │   ├── covid19_quality_checks.py         # Data quality DAG
│   │   └── covid19_maintenance.py            # Cleanup & archival DAG
│   │
│   ├── 📁 plugins/
│   │   └── covid19_operators/
│   │       ├── __init__.py
│   │       ├── owid_download_operator.py
│   │       ├── validate_operator.py
│   │       └── refresh_views_operator.py
│   │
│   └── 📁 config/
│       └── airflow.cfg                       # Airflow configuration
│
├── 📁 powerbi/
│   ├── 📁 templates/
│   │   └── covid19_dashboard.pbix            # Power BI Desktop file
│   ├── 📁 dax/
│   │   └── measures.dax                      # All DAX measure definitions
│   └── 📁 docs/
│       └── POWERBI.md                        # Setup & configuration guide
│
├── 📁 docker/
│   ├── 📁 backend/
│   │   └── Dockerfile
│   ├── 📁 frontend/
│   │   └── Dockerfile
│   ├── 📁 airflow/
│   │   └── Dockerfile
│   ├── 📁 nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── 📁 postgres/
│       └── init.sql
│
├── 📁 tests/
│   ├── 📁 e2e/                               # Playwright end-to-end tests
│   ├── 📁 load/                              # Locust load tests
│   └── 📁 smoke/                             # Smoke tests
│
├── 📁 scripts/
│   ├── 📁 setup/
│   │   ├── setup_local.sh
│   │   └── generate_keys.py
│   ├── 📁 maintenance/
│   │   ├── cleanup_old_logs.py
│   │   └── vacuum_analyze.sql
│   └── 📁 migrations/
│       └── run_migrations.sh
│
├── 📁 docs/
│   ├── 📁 architecture/
│   │   └── ARCHITECTURE.md
│   ├── 📁 api/
│   │   └── API_REFERENCE.md
│   ├── 📁 database/
│   │   └── SCHEMA.md
│   ├── 📁 etl/
│   │   └── ETL_PIPELINE.md
│   ├── 📁 frontend/
│   │   └── FRONTEND.md
│   ├── 📁 backend/
│   │   └── BACKEND.md
│   ├── 📁 airflow/
│   │   └── AIRFLOW.md
│   ├── 📁 powerbi/
│   │   └── POWERBI.md
│   ├── 📁 auth/
│   │   └── AUTHENTICATION.md
│   ├── 📁 deployment/
│   │   └── DEPLOYMENT.md
│   └── 📁 testing/
│       └── TESTING.md
│
├── 📁 architecture/
│   ├── 📁 diagrams/
│   │   ├── system_architecture.png
│   │   ├── er_diagram.png
│   │   └── sequence_diagram.png
│   └── 📁 decisions/
│       └── TDR.md                            # Technology Decision Records
│
├── 📁 assets/
│   ├── 📁 images/
│   └── 📁 diagrams/
│
└── 📁 backups/                               # Database backups (gitignored)
```
