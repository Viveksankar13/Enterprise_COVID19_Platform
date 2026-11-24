-- ==============================================================================
-- FILE: 03_constraints.sql
-- Enterprise COVID-19 Analytics Platform — Constraints & Business Rules
-- Run after 02_tables.sql
-- ==============================================================================

-- ==============================================================================
-- ADDITIONAL CHECK CONSTRAINTS
-- (Core NOT NULL and type constraints are in 02_tables.sql)
-- ==============================================================================

-- Countries: iso_code format — 2–8 uppercase alpha or underscore
ALTER TABLE countries
    ADD CONSTRAINT chk_countries_iso_format
        CHECK (iso_code ~ '^[A-Z0-9_]{2,8}$');

-- Countries: continent must be a valid value or NULL (for aggregates)
ALTER TABLE countries
    ADD CONSTRAINT chk_countries_continent
        CHECK (continent IN (
            'Africa', 'Asia', 'Europe',
            'North America', 'Oceania', 'South America', 'Antarctica'
        ) OR continent IS NULL);

-- Demographics: population must be positive
ALTER TABLE demographics
    ADD CONSTRAINT chk_demographics_population
        CHECK (population IS NULL OR population > 0);

ALTER TABLE demographics
    ADD CONSTRAINT chk_demographics_population_density
        CHECK (population_density IS NULL OR population_density >= 0);

ALTER TABLE demographics
    ADD CONSTRAINT chk_demographics_median_age
        CHECK (median_age IS NULL OR median_age BETWEEN 0 AND 100);

ALTER TABLE demographics
    ADD CONSTRAINT chk_demographics_hdi
        CHECK (human_development_index IS NULL
               OR human_development_index BETWEEN 0 AND 1);

ALTER TABLE demographics
    ADD CONSTRAINT chk_demographics_life_expectancy
        CHECK (life_expectancy IS NULL
               OR life_expectancy BETWEEN 1 AND 120);

-- Daily metrics: totals must be non-negative and monotonically non-decreasing
-- (enforced at ETL layer; constraint here catches bad data slipping through)
ALTER TABLE daily_metrics
    ADD CONSTRAINT chk_daily_metrics_total_cases_nonneg
        CHECK (total_cases IS NULL OR total_cases >= 0);

ALTER TABLE daily_metrics
    ADD CONSTRAINT chk_daily_metrics_total_deaths_nonneg
        CHECK (total_deaths IS NULL OR total_deaths >= 0);

ALTER TABLE daily_metrics
    ADD CONSTRAINT chk_daily_metrics_stringency_range
        CHECK (stringency_index IS NULL
               OR stringency_index BETWEEN 0 AND 100);

ALTER TABLE daily_metrics
    ADD CONSTRAINT chk_daily_metrics_reproduction_rate
        CHECK (reproduction_rate IS NULL
               OR reproduction_rate BETWEEN 0 AND 50);

-- Vaccinations: people_fully_vaccinated cannot exceed people_vaccinated
ALTER TABLE vaccinations
    ADD CONSTRAINT chk_vaccinations_fully_le_vaccinated
        CHECK (people_fully_vaccinated IS NULL
               OR people_vaccinated IS NULL
               OR people_fully_vaccinated <= people_vaccinated);

ALTER TABLE vaccinations
    ADD CONSTRAINT chk_vaccinations_per_hundred_range
        CHECK (people_vaccinated_per_hundred IS NULL
               OR people_vaccinated_per_hundred BETWEEN 0 AND 200);

-- Testing: positive_rate must be 0–1
ALTER TABLE testing
    ADD CONSTRAINT chk_testing_positive_rate_range
        CHECK (positive_rate IS NULL
               OR positive_rate BETWEEN 0 AND 1);

ALTER TABLE testing
    ADD CONSTRAINT chk_testing_tests_per_case
        CHECK (tests_per_case IS NULL OR tests_per_case >= 0);

-- Hospitalizations: counts must be non-negative
ALTER TABLE hospitalizations
    ADD CONSTRAINT chk_hospitalizations_icu_nonneg
        CHECK (icu_patients IS NULL OR icu_patients >= 0);

ALTER TABLE hospitalizations
    ADD CONSTRAINT chk_hospitalizations_hosp_nonneg
        CHECK (hosp_patients IS NULL OR hosp_patients >= 0);

-- Users: email must contain @ (CITEXT already provides uniqueness)
ALTER TABLE users
    ADD CONSTRAINT chk_users_email_format
        CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$');

ALTER TABLE users
    ADD CONSTRAINT chk_users_login_count_nonneg
        CHECK (login_count >= 0);

-- ETL logs: completed_at must be after started_at
ALTER TABLE etl_logs
    ADD CONSTRAINT chk_etl_logs_dates_order
        CHECK (completed_at IS NULL OR completed_at >= started_at);

ALTER TABLE etl_logs
    ADD CONSTRAINT chk_etl_logs_row_counts_nonneg
        CHECK (
            rows_downloaded >= 0 AND
            rows_validated  >= 0 AND
            rows_rejected   >= 0 AND
            rows_inserted   >= 0 AND
            rows_updated    >= 0
        );

-- Audit logs: response_status must be valid HTTP code range
ALTER TABLE audit_logs
    ADD CONSTRAINT chk_audit_logs_http_status
        CHECK (response_status IS NULL
               OR response_status BETWEEN 100 AND 599);

-- ==============================================================================
-- UNIQUE CONSTRAINTS (supplementary)
-- ==============================================================================

-- Ensure each user can only have one role (already FK; just documenting intent)
-- A junction table would be used for multi-role support in v2.

-- ==============================================================================
-- FOREIGN KEY SUMMARY (explicitly named for DBA clarity)
-- All FK constraints are named to support easy identification in pg_constraint
-- ==============================================================================

-- Already defined inline in 02_tables.sql with ON DELETE rules:
--   permissions.role_id         → roles(role_id)           CASCADE
--   users.role_id               → roles(role_id)           RESTRICT (default)
--   demographics.iso_code       → countries(iso_code)      CASCADE
--   daily_metrics.iso_code      → countries(iso_code)      (inherits default)
--   daily_metrics.date          → calendar(date_value)     (inherits default)
--   vaccinations.iso_code       → countries(iso_code)
--   vaccinations.date           → calendar(date_value)
--   testing.iso_code            → countries(iso_code)
--   testing.date                → calendar(date_value)
--   hospitalizations.iso_code   → countries(iso_code)
--   hospitalizations.date       → calendar(date_value)
--   audit_logs.user_id          → users(user_id)           SET NULL
--   metadata.updated_by         → users(user_id)           SET NULL
