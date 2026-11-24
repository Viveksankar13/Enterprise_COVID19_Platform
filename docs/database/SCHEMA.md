# Enterprise COVID-19 Analytics Platform — Database Schema Documentation

## Overview

The database uses **PostgreSQL 16** with a star-schema hybrid designed for both OLTP operations (user management, ETL logging) and OLAP analytics (window functions, materialized views, CTEs).

---

## Schema Layers

```
┌─────────────────────────────────────────────────────────────┐
│  SECURITY LAYER       roles │ permissions │ users           │
├─────────────────────────────────────────────────────────────┤
│  REFERENCE LAYER      countries │ demographics │ calendar   │
├─────────────────────────────────────────────────────────────┤
│  FACT LAYER           daily_metrics │ vaccinations │        │
│                       testing │ hospitalizations            │
├─────────────────────────────────────────────────────────────┤
│  OPERATIONAL LAYER    etl_logs │ audit_logs │ metadata      │
├─────────────────────────────────────────────────────────────┤
│  ANALYTICAL LAYER     Views │ Materialized Views │ Functions│
└─────────────────────────────────────────────────────────────┘
```

---

## Table Reference

### `roles`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `role_id` | SMALLINT | PK, GENERATED | Auto-incremented role ID |
| `name` | VARCHAR(50) | NOT NULL, UNIQUE | Role name: admin \| analyst \| viewer \| api_user |
| `description` | TEXT | — | Human-readable role description |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft-disable flag |
| `created_at` | TIMESTAMPTZ | NOT NULL | Row creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Auto-updated on change |

### `permissions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `permission_id` | INTEGER | PK, GENERATED | Auto-incremented ID |
| `role_id` | SMALLINT | FK → roles, NOT NULL | Parent role |
| `resource` | VARCHAR(100) | NOT NULL | e.g. `analytics`, `etl`, `users` |
| `action` | VARCHAR(50) | NOT NULL | e.g. `read`, `write`, `execute`, `delete` |
| `created_at` | TIMESTAMPTZ | NOT NULL | Row creation timestamp |

**Unique**: `(role_id, resource, action)`

### `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | UUID | PK, DEFAULT uuid_generate_v4() | Globally unique user ID |
| `email` | CITEXT | NOT NULL, UNIQUE | Case-insensitive email |
| `username` | VARCHAR(100) | NOT NULL, UNIQUE | Login username |
| `full_name` | VARCHAR(200) | — | Display name |
| `password_hash` | TEXT | NOT NULL | bcrypt hash — never plaintext |
| `role_id` | SMALLINT | FK → roles, NOT NULL | Assigned role |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active flag |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | Email verification flag |
| `last_login_at` | TIMESTAMPTZ | — | Last successful login |
| `login_count` | INTEGER | NOT NULL, DEFAULT 0 | Cumulative login count |

### `countries`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `iso_code` | VARCHAR(8) | PK | ISO 3166-1 alpha-3 or OWID aggregate code |
| `continent` | VARCHAR(50) | — | Africa \| Asia \| Europe \| North America \| Oceania \| South America |
| `location` | VARCHAR(200) | NOT NULL | Country or region name |
| `income_group` | VARCHAR(50) | — | World Bank income classification |
| `who_region` | VARCHAR(50) | — | WHO region |
| `is_aggregate` | BOOLEAN | NOT NULL | TRUE for OWID_WRL, OWID_EUR, etc. |
| `is_active` | BOOLEAN | NOT NULL | Soft-delete flag |

### `demographics`
| Column | Type | Description |
|---|---|---|
| `iso_code` | VARCHAR(8) PK, FK → countries | One-to-one with Country |
| `population` | BIGINT | Total population |
| `population_density` | NUMERIC(10,3) | People per km² |
| `median_age` | NUMERIC(5,2) | Median age (years) |
| `aged_65_older` | NUMERIC(6,3) | % aged 65+ |
| `aged_70_older` | NUMERIC(6,3) | % aged 70+ |
| `gdp_per_capita` | NUMERIC(12,3) | 2017 int. dollars (PPP) |
| `extreme_poverty` | NUMERIC(6,3) | % below $1.90/day |
| `cardiovasc_death_rate` | NUMERIC(8,3) | Deaths per 100k from cardiovascular disease |
| `diabetes_prevalence` | NUMERIC(6,3) | % of population 20–79 |
| `hospital_beds_per_thousand` | NUMERIC(6,3) | Hospital beds per 1,000 people |
| `life_expectancy` | NUMERIC(5,2) | Life expectancy at birth |
| `human_development_index` | NUMERIC(5,4) | UNDP HDI (0–1 scale) |

### `calendar`
Date dimension table. Populated for **2019-01-01 to 2030-12-31** (4,383 rows).

| Column | Type | Description |
|---|---|---|
| `date_value` | DATE | PK — the date itself |
| `year` | SMALLINT | Calendar year |
| `quarter` | SMALLINT | 1–4 |
| `month` | SMALLINT | 1–12 |
| `month_name` | VARCHAR(10) | 'January' etc. |
| `week_of_year` | SMALLINT | 1–53 (ISO week) |
| `day_of_week` | SMALLINT | 0=Sunday, 6=Saturday |
| `is_weekend` | BOOLEAN | TRUE for Sat/Sun |
| `year_month` | CHAR(7) | 'YYYY-MM' — for GROUP BY |
| `year_quarter` | CHAR(7) | 'YYYY-Q#' — for GROUP BY |

### `daily_metrics`
**Primary fact table.** Composite PK: `(iso_code, date)`.

| Column | Type | Description |
|---|---|---|
| `iso_code` | VARCHAR(8) FK | Country reference |
| `date` | DATE FK | Date reference |
| `new_cases` | BIGINT | New confirmed cases |
| `new_cases_smoothed` | NUMERIC(14,3) | 7-day rolling average (OWID pre-computed) |
| `total_cases` | BIGINT | Cumulative confirmed cases |
| `new_cases_per_million` | NUMERIC(14,3) | Per-million normalized |
| `total_cases_per_million` | NUMERIC(14,3) | Per-million normalized |
| `new_deaths` | INTEGER | New confirmed deaths |
| `new_deaths_smoothed` | NUMERIC(12,3) | 7-day rolling average |
| `total_deaths` | BIGINT | Cumulative confirmed deaths |
| `reproduction_rate` | NUMERIC(6,3) | Estimated R value |
| `stringency_index` | NUMERIC(6,3) | OxCGRT policy stringency (0–100) |
| `etl_run_id` | UUID FK | Links to etl_logs |
| `loaded_at` | TIMESTAMPTZ | ETL load timestamp |

### `vaccinations`
Composite PK: `(iso_code, date)`.

| Column | Description |
|---|---|
| `total_vaccinations` | Cumulative doses administered |
| `people_vaccinated` | Cumulative people with ≥1 dose |
| `people_fully_vaccinated` | Completed primary series |
| `total_boosters` | Cumulative booster doses |
| `people_fully_vaccinated_per_hundred` | Coverage % of population |

### `testing`
Composite PK: `(iso_code, date)`.

| Column | Description |
|---|---|
| `new_tests` | New tests performed |
| `total_tests` | Cumulative tests |
| `positive_rate` | Share of tests returning positive (0.0–1.0) |
| `tests_per_case` | Tests per confirmed case |
| `tests_units` | Reporting unit definition (varies by country) |

> ⚠️ **Important**: `tests_units` varies by country — always filter or annotate in cross-country comparisons.

### `hospitalizations`
Composite PK: `(iso_code, date)`.

| Column | Description |
|---|---|
| `icu_patients` | Current ICU patients |
| `icu_patients_per_million` | Per-million normalized |
| `hosp_patients` | Current hospital patients |
| `weekly_icu_admissions` | Weekly ICU admissions (flow metric) |
| `weekly_hosp_admissions` | Weekly hospital admissions (flow metric) |

### `etl_logs`
| Column | Description |
|---|---|
| `run_id` | UUID PK — unique run identifier |
| `pipeline_name` | e.g. `covid19_etl_pipeline` |
| `status` | RUNNING \| SUCCESS \| FAILED \| PARTIAL \| SKIPPED |
| `rows_downloaded` | Raw rows in source file |
| `rows_rejected` | Rows failing validation |
| `rows_inserted` | New rows added to DB |
| `rows_updated` | Existing rows updated |
| `duration_seconds` | GENERATED STORED column |
| `dataset_checksum` | SHA-256 for change detection |

### `audit_logs`
Append-only — no UPDATE or DELETE.

| Column | Description |
|---|---|
| `log_id` | BIGINT PK — monotonic |
| `user_id` | FK → users (SET NULL on delete) |
| `action` | e.g. `LOGIN`, `EXPORT_DATA`, `ETL_TRIGGER` |
| `ip_address` | INET type for IPv4/IPv6 |
| `metadata` | JSONB for arbitrary additional context |

---

## Analytical Views

| View | Purpose | Key Techniques |
|---|---|---|
| `v_country_latest_snapshot` | Latest data per country across all facts | Multi-CTE, LEFT JOINs |
| `v_daily_trends_with_rolling_averages` | 7/14-day MA, running totals, WoW change | Window: AVG, SUM, LAG, LEAD |
| `v_country_rankings` | Country leaderboards globally and by continent | Window: DENSE_RANK, NTILE, ROW_NUMBER, PARTITION BY |
| `v_monthly_aggregates` | Month-level aggregation | GROUP BY, MAX, SUM, AVG |
| `v_vaccination_progress` | Milestone tracking + linear projection | Window: LAG, arithmetic |
| `v_testing_quality` | WHO 5% positivity alerts + 7-day MA | Window: AVG, LAG |
| `v_excess_burden` | 14-day lagged CFR + severity classification | Window: LAG with offset |
| `v_global_daily_summary` | World-level daily aggregates | GROUP BY with conditional JOIN |
| `v_etl_pipeline_health` | ETL run status dashboard | ROW_NUMBER, computed rates |

## Materialized Views

| Materialized View | Refresh Trigger | Rows (est.) |
|---|---|---|
| `mv_country_kpis` | After each ETL load | ~250 |
| `mv_global_summary` | After each ETL load | 1 |
| `mv_monthly_country_trends` | After each ETL load | ~30,000 |
| `mv_continent_summary` | After each ETL load | 7 |

Refresh via: `CALL refresh_all_materialized_views();`

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Composite PKs on fact tables | Enforces uniqueness, eliminates surrogate key overhead |
| BRIN indexes on date columns | 90% space savings vs. B-Tree for monotonically-ordered insert patterns |
| CITEXT for email | Database-level case-insensitivity without application overhead |
| JSONB for etl_logs.metadata | Flexible schema for ETL-specific context without altering the table |
| GENERATED STORED for duration_seconds | Computed at write time, readable without overhead |
| UUID PKs for users/etl_logs | Globally unique, suitable for distributed systems, not guessable |
| Materialized view unique indexes | Required for REFRESH CONCURRENTLY — allows online refreshes without table locks |
