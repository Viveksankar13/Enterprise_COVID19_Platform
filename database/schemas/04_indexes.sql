-- ==============================================================================
-- FILE: 04_indexes.sql
-- Enterprise COVID-19 Analytics Platform — Index Strategy
-- Run after 03_constraints.sql
--
-- Index naming convention: idx_{table}_{columns}_{type_suffix}
--   _brin   = BRIN index (for monotonically-increasing date columns)
--   _gin    = GIN index (for JSONB or array columns)
--   _trgm   = GIN trigram index (for full-text search on text columns)
--   _hash   = Hash index (for equality-only lookups)
-- ==============================================================================

-- ==============================================================================
-- COUNTRIES
-- ==============================================================================

-- Fast lookup by location name (used in search/filter UI)
CREATE INDEX idx_countries_location_trgm
    ON countries USING GIN (location gin_trgm_ops);

-- Filter by continent
CREATE INDEX idx_countries_continent
    ON countries (continent)
    WHERE continent IS NOT NULL;

-- Active countries only (partial index — most queries exclude aggregates)
CREATE INDEX idx_countries_active_not_aggregate
    ON countries (iso_code)
    WHERE is_active = TRUE AND is_aggregate = FALSE;

-- ==============================================================================
-- DEMOGRAPHICS
-- ==============================================================================

-- Sorted population (for top-N queries)
CREATE INDEX idx_demographics_population_desc
    ON demographics (population DESC NULLS LAST);

-- GDP per capita (for income quartile analysis)
CREATE INDEX idx_demographics_gdp_per_capita
    ON demographics (gdp_per_capita DESC NULLS LAST);

-- ==============================================================================
-- CALENDAR
-- ==============================================================================

-- Year + Month grouping (very common in trend queries)
CREATE INDEX idx_calendar_year_month
    ON calendar (year, month);

-- Year + Quarter grouping
CREATE INDEX idx_calendar_year_quarter
    ON calendar (year, quarter);

-- Year-Month string (used in GROUP BY for chart labels)
CREATE INDEX idx_calendar_year_month_str
    ON calendar (year_month);

-- ==============================================================================
-- DAILY_METRICS
-- ==============================================================================

-- Primary query pattern: country + date range
-- Covered by the composite PK (iso_code, date), but add date-first index
-- for global date range queries (e.g. "all countries on 2021-01-01")
CREATE INDEX idx_daily_metrics_date
    ON daily_metrics (date);

-- BRIN index on date for time-range scans (very space-efficient for sorted data)
CREATE INDEX idx_daily_metrics_date_brin
    ON daily_metrics USING BRIN (date)
    WITH (pages_per_range = 32);

-- Loaded_at — for incremental ETL queries
CREATE INDEX idx_daily_metrics_loaded_at
    ON daily_metrics (loaded_at DESC);

-- ETL run lookback
CREATE INDEX idx_daily_metrics_etl_run_id
    ON daily_metrics (etl_run_id)
    WHERE etl_run_id IS NOT NULL;

-- New cases (for hot-spot detection — top N countries by new_cases)
CREATE INDEX idx_daily_metrics_new_cases_desc
    ON daily_metrics (date, new_cases DESC NULLS LAST);

-- ==============================================================================
-- VACCINATIONS
-- ==============================================================================

CREATE INDEX idx_vaccinations_date
    ON vaccinations (date);

CREATE INDEX idx_vaccinations_date_brin
    ON vaccinations USING BRIN (date)
    WITH (pages_per_range = 32);

-- Vaccination rate for coverage league tables
CREATE INDEX idx_vaccinations_people_fully_vacc_per_hundred
    ON vaccinations (people_fully_vaccinated_per_hundred DESC NULLS LAST);

CREATE INDEX idx_vaccinations_loaded_at
    ON vaccinations (loaded_at DESC);

-- ==============================================================================
-- TESTING
-- ==============================================================================

CREATE INDEX idx_testing_date
    ON testing (date);

CREATE INDEX idx_testing_date_brin
    ON testing USING BRIN (date)
    WITH (pages_per_range = 32);

-- Positivity rate monitoring
CREATE INDEX idx_testing_positive_rate
    ON testing (date, positive_rate DESC NULLS LAST)
    WHERE positive_rate IS NOT NULL;

-- ==============================================================================
-- HOSPITALIZATIONS
-- ==============================================================================

CREATE INDEX idx_hospitalizations_date
    ON hospitalizations (date);

CREATE INDEX idx_hospitalizations_date_brin
    ON hospitalizations USING BRIN (date)
    WITH (pages_per_range = 32);

-- ICU pressure monitoring
CREATE INDEX idx_hospitalizations_icu_per_million
    ON hospitalizations (date, icu_patients_per_million DESC NULLS LAST)
    WHERE icu_patients_per_million IS NOT NULL;

-- ==============================================================================
-- USERS
-- ==============================================================================

-- Email lookup (used on every login)
CREATE UNIQUE INDEX idx_users_email_lower
    ON users (lower(email::TEXT));

-- Username lookup
CREATE INDEX idx_users_username
    ON users (username);

-- Active users by role (for RBAC checks)
CREATE INDEX idx_users_role_active
    ON users (role_id, is_active)
    WHERE is_active = TRUE;

-- ==============================================================================
-- ETL_LOGS
-- ==============================================================================

-- Most recent runs first (dashboard shows latest N runs)
CREATE INDEX idx_etl_logs_started_at_desc
    ON etl_logs (started_at DESC);

-- Filter by pipeline name
CREATE INDEX idx_etl_logs_pipeline_name
    ON etl_logs (pipeline_name, started_at DESC);

-- Filter by status
CREATE INDEX idx_etl_logs_status
    ON etl_logs (status, started_at DESC);

-- JSONB metadata queries
CREATE INDEX idx_etl_logs_metadata_gin
    ON etl_logs USING GIN (metadata);

-- ==============================================================================
-- AUDIT_LOGS
-- ==============================================================================

-- Time-range queries (primary access pattern)
CREATE INDEX idx_audit_logs_created_at_brin
    ON audit_logs USING BRIN (created_at)
    WITH (pages_per_range = 64);

-- User activity lookup
CREATE INDEX idx_audit_logs_user_id
    ON audit_logs (user_id, created_at DESC)
    WHERE user_id IS NOT NULL;

-- Action-based filtering (e.g. find all LOGIN events)
CREATE INDEX idx_audit_logs_action
    ON audit_logs (action, created_at DESC);

-- IP address for security investigations
CREATE INDEX idx_audit_logs_ip
    ON audit_logs (ip_address, created_at DESC)
    WHERE ip_address IS NOT NULL;

-- JSONB metadata
CREATE INDEX idx_audit_logs_metadata_gin
    ON audit_logs USING GIN (metadata)
    WHERE metadata != '{}';

-- ==============================================================================
-- COMPOSITE COVERING INDEXES
-- Designed for the most expensive analytical queries
-- ==============================================================================

-- "Country trend" query: iso_code + date range → cases + deaths
-- Fully covers the most common API endpoint
CREATE INDEX idx_daily_metrics_trend_covering
    ON daily_metrics (iso_code, date)
    INCLUDE (new_cases, new_cases_smoothed, new_deaths, new_deaths_smoothed,
             total_cases, total_deaths, reproduction_rate, stringency_index);

-- "Vaccination progress" covering index
CREATE INDEX idx_vaccinations_progress_covering
    ON vaccinations (iso_code, date)
    INCLUDE (people_vaccinated, people_fully_vaccinated, total_boosters,
             people_vaccinated_per_hundred, people_fully_vaccinated_per_hundred);

-- "Testing positivity" covering index
CREATE INDEX idx_testing_positivity_covering
    ON testing (iso_code, date)
    INCLUDE (new_tests, total_tests, positive_rate, tests_per_case);

-- "Global leaderboard" for a given date (used in KPI cards)
CREATE INDEX idx_daily_metrics_global_date
    ON daily_metrics (date, iso_code)
    INCLUDE (new_cases_per_million, new_deaths_per_million, total_cases_per_million);

-- ==============================================================================
-- STATISTICS TARGETS
-- Increase planner statistics for high-cardinality columns
-- ==============================================================================

ALTER TABLE daily_metrics    ALTER COLUMN date        SET STATISTICS 500;
ALTER TABLE daily_metrics    ALTER COLUMN iso_code     SET STATISTICS 500;
ALTER TABLE vaccinations     ALTER COLUMN date         SET STATISTICS 500;
ALTER TABLE testing          ALTER COLUMN date         SET STATISTICS 500;
ALTER TABLE hospitalizations ALTER COLUMN date         SET STATISTICS 500;
