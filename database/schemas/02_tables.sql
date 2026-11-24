-- ==============================================================================
-- FILE: 02_tables.sql
-- Enterprise COVID-19 Analytics Platform — Core Table Definitions
-- Execution order matters: reference tables before fact tables.
-- ==============================================================================

-- ==============================================================================
-- SECTION 1: SECURITY & IDENTITY LAYER
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- ROLES — Application-level roles for RBAC
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    role_id       SMALLINT      PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name          VARCHAR(50)   NOT NULL UNIQUE,
    description   TEXT,
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  roles                IS 'Application roles for role-based access control (RBAC).';
COMMENT ON COLUMN roles.name          IS 'Unique role name: admin | analyst | viewer | api_user';
COMMENT ON COLUMN roles.is_active     IS 'Soft-disable a role without deleting it.';

-- ------------------------------------------------------------------------------
-- PERMISSIONS — Fine-grained resource + action permissions per role
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS permissions (
    permission_id   INTEGER       PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    role_id         SMALLINT      NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    resource        VARCHAR(100)  NOT NULL,   -- e.g. 'analytics', 'etl', 'users'
    action          VARCHAR(50)   NOT NULL,   -- e.g. 'read', 'write', 'execute', 'delete'
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (role_id, resource, action)
);

COMMENT ON TABLE permissions IS 'Maps roles to allowed resource+action combinations.';

-- ------------------------------------------------------------------------------
-- USERS — Platform users with bcrypt-hashed passwords
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id         UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           CITEXT        NOT NULL UNIQUE,
    username        VARCHAR(100)  NOT NULL UNIQUE,
    full_name       VARCHAR(200),
    password_hash   TEXT          NOT NULL,
    role_id         SMALLINT      NOT NULL REFERENCES roles(role_id),
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN       NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    login_count     INTEGER       NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  users               IS 'Platform users. Passwords are always stored as bcrypt hashes.';
COMMENT ON COLUMN users.email         IS 'Case-insensitive unique email (uses CITEXT extension).';
COMMENT ON COLUMN users.password_hash IS 'bcrypt hash — NEVER store plaintext passwords here.';

-- ==============================================================================
-- SECTION 2: REFERENCE / DIMENSION TABLES
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- COUNTRIES — Master dimension for all geographic entities in the OWID dataset
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS countries (
    iso_code            VARCHAR(8)    PRIMARY KEY,
    continent           VARCHAR(50),
    location            VARCHAR(200)  NOT NULL,
    -- Classification
    income_group        VARCHAR(50),                -- World Bank income group
    who_region          VARCHAR(50),                -- WHO region name
    world_bank_region   VARCHAR(100),
    -- Flags
    is_aggregate        BOOLEAN       NOT NULL DEFAULT FALSE,   -- OWID aggregate rows (OWID_WRL etc.)
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
    -- Metadata
    data_source         VARCHAR(100)  DEFAULT 'OWID',
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  countries              IS 'Master country/region dimension. Source: OWID ISO code list.';
COMMENT ON COLUMN countries.iso_code     IS 'ISO 3166-1 alpha-3 code OR OWID custom aggregate code (OWID_WRL etc.).';
COMMENT ON COLUMN countries.is_aggregate IS 'TRUE for OWID aggregate rows like World, Europe, High income etc.';

-- ------------------------------------------------------------------------------
-- DEMOGRAPHICS — Population & socioeconomic indicators per country (slow-changing)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS demographics (
    iso_code                    VARCHAR(8)      PRIMARY KEY REFERENCES countries(iso_code) ON DELETE CASCADE,
    population                  BIGINT,
    population_density          NUMERIC(10,3),  -- people per sq km
    median_age                  NUMERIC(5,2),
    aged_65_older               NUMERIC(6,3),   -- % of population
    aged_70_older               NUMERIC(6,3),
    gdp_per_capita              NUMERIC(12,3),  -- international dollars (PPP)
    extreme_poverty             NUMERIC(6,3),   -- % below $1.90/day
    cardiovasc_death_rate       NUMERIC(8,3),   -- deaths per 100k
    diabetes_prevalence         NUMERIC(6,3),   -- % of population 20–79
    female_smokers              NUMERIC(6,3),   -- % of females
    male_smokers                NUMERIC(6,3),   -- % of males
    handwashing_facilities      NUMERIC(6,3),   -- % with access
    hospital_beds_per_thousand  NUMERIC(6,3),
    life_expectancy             NUMERIC(5,2),
    human_development_index     NUMERIC(5,4),
    -- Audit
    data_year                   SMALLINT,       -- year of demographic snapshot
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  demographics                       IS 'Socioeconomic & health infrastructure indicators per country. One row per country.';
COMMENT ON COLUMN demographics.gdp_per_capita        IS 'GDP per capita in international dollars (2017 PPP). World Bank / IMF.';
COMMENT ON COLUMN demographics.human_development_index IS 'UNDP HDI 0–1 scale. Higher = more developed.';

-- ------------------------------------------------------------------------------
-- CALENDAR — Date dimension table for analytics (pre-populated)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS calendar (
    date_value      DATE        PRIMARY KEY,
    year            SMALLINT    NOT NULL,
    quarter         SMALLINT    NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    month           SMALLINT    NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name      VARCHAR(10) NOT NULL,
    week_of_year    SMALLINT    NOT NULL CHECK (week_of_year BETWEEN 1 AND 53),
    day_of_month    SMALLINT    NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_week     SMALLINT    NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),  -- 0=Sunday
    day_name        VARCHAR(10) NOT NULL,
    is_weekend      BOOLEAN     NOT NULL,
    is_leap_year    BOOLEAN     NOT NULL,
    year_month      CHAR(7)     NOT NULL,    -- 'YYYY-MM' for easy grouping
    year_quarter    CHAR(7)     NOT NULL     -- 'YYYY-Q#'
);

COMMENT ON TABLE calendar IS 'Date dimension table. Pre-populated for 2019-01-01 through 2030-12-31.';

-- ==============================================================================
-- SECTION 3: FACT TABLES
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- DAILY_METRICS — Core epidemiological measurements (cases, deaths, stringency)
-- High-write table — partitioned by year
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_metrics (
    -- Natural composite PK
    iso_code                    VARCHAR(8)      NOT NULL REFERENCES countries(iso_code),
    date                        DATE            NOT NULL REFERENCES calendar(date_value),
    -- Case metrics
    new_cases                   BIGINT,
    new_cases_smoothed          NUMERIC(14,3),  -- 7-day rolling average
    total_cases                 BIGINT,
    new_cases_per_million       NUMERIC(14,3),
    new_cases_smoothed_per_million NUMERIC(14,3),
    total_cases_per_million     NUMERIC(14,3),
    -- Death metrics
    new_deaths                  INTEGER,
    new_deaths_smoothed         NUMERIC(12,3),
    total_deaths                BIGINT,
    new_deaths_per_million      NUMERIC(12,3),
    new_deaths_smoothed_per_million NUMERIC(12,3),
    total_deaths_per_million    NUMERIC(12,3),
    -- Reproduction & spread
    reproduction_rate           NUMERIC(6,3),
    -- Policy & response
    stringency_index            NUMERIC(6,3)    CHECK (stringency_index BETWEEN 0 AND 100),
    -- Audit
    etl_run_id                  UUID,
    loaded_at                   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    -- Composite primary key
    CONSTRAINT pk_daily_metrics PRIMARY KEY (iso_code, date)
);

COMMENT ON TABLE  daily_metrics                   IS 'Core epidemiological fact table. One row per (country, date). Source: OWID.';
COMMENT ON COLUMN daily_metrics.new_cases_smoothed IS '7-day rolling average of new_cases. Pre-computed by OWID.';
COMMENT ON COLUMN daily_metrics.reproduction_rate  IS 'Estimated effective reproduction number (R). Values > 1 indicate growth.';
COMMENT ON COLUMN daily_metrics.stringency_index   IS 'OxCGRT Stringency Index 0–100. Higher = stricter government response.';

-- ------------------------------------------------------------------------------
-- VACCINATIONS — Vaccination program tracking
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vaccinations (
    iso_code                            VARCHAR(8)   NOT NULL REFERENCES countries(iso_code),
    date                                DATE         NOT NULL REFERENCES calendar(date_value),
    -- Raw counts
    total_vaccinations                  BIGINT,
    people_vaccinated                   BIGINT,
    people_fully_vaccinated             BIGINT,
    total_boosters                      BIGINT,
    new_vaccinations                    INTEGER,
    new_vaccinations_smoothed           NUMERIC(14,3),
    -- Per-100 rates
    total_vaccinations_per_hundred      NUMERIC(8,3),
    people_vaccinated_per_hundred       NUMERIC(8,3),
    people_fully_vaccinated_per_hundred NUMERIC(8,3),
    total_boosters_per_hundred          NUMERIC(8,3),
    new_vaccinations_smoothed_per_million NUMERIC(12,3),
    -- Audit
    etl_run_id                          UUID,
    loaded_at                           TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_vaccinations PRIMARY KEY (iso_code, date)
);

COMMENT ON TABLE vaccinations IS 'Vaccination program data per country per day. Source: OWID / Our World in Data.';
COMMENT ON COLUMN vaccinations.people_vaccinated IS 'Cumulative count of people who received at least one dose.';
COMMENT ON COLUMN vaccinations.people_fully_vaccinated IS 'Cumulative count of people who completed primary vaccination series.';

-- ------------------------------------------------------------------------------
-- TESTING — COVID-19 testing metrics
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS testing (
    iso_code                    VARCHAR(8)   NOT NULL REFERENCES countries(iso_code),
    date                        DATE         NOT NULL REFERENCES calendar(date_value),
    -- Raw counts
    new_tests                   INTEGER,
    total_tests                 BIGINT,
    new_tests_smoothed          NUMERIC(12,3),
    total_tests_per_thousand    NUMERIC(12,3),
    new_tests_per_thousand      NUMERIC(10,3),
    new_tests_smoothed_per_thousand NUMERIC(10,3),
    -- Positivity
    positive_rate               NUMERIC(7,5)  CHECK (positive_rate BETWEEN 0 AND 1),
    tests_per_case              NUMERIC(10,3),
    -- Units
    tests_units                 VARCHAR(50),  -- 'people tested', 'tests performed', 'samples tested'
    -- Audit
    etl_run_id                  UUID,
    loaded_at                   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_testing PRIMARY KEY (iso_code, date)
);

COMMENT ON TABLE  testing               IS 'Testing capacity and positivity data per country per day. Source: OWID.';
COMMENT ON COLUMN testing.positive_rate IS 'Share of COVID tests returning positive. Range 0.0–1.0. WHO target < 0.05.';
COMMENT ON COLUMN testing.tests_units   IS 'Unit definition varies by country. Critical for cross-country comparisons.';

-- ------------------------------------------------------------------------------
-- HOSPITALIZATIONS — Hospital and ICU capacity data
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hospitalizations (
    iso_code                            VARCHAR(8)  NOT NULL REFERENCES countries(iso_code),
    date                                DATE        NOT NULL REFERENCES calendar(date_value),
    -- Patient counts
    icu_patients                        INTEGER,
    icu_patients_per_million            NUMERIC(10,3),
    hosp_patients                       INTEGER,
    hosp_patients_per_million           NUMERIC(10,3),
    -- Weekly flows
    weekly_icu_admissions               NUMERIC(12,3),
    weekly_icu_admissions_per_million   NUMERIC(10,3),
    weekly_hosp_admissions              NUMERIC(12,3),
    weekly_hosp_admissions_per_million  NUMERIC(10,3),
    -- Audit
    etl_run_id                          UUID,
    loaded_at                           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_hospitalizations PRIMARY KEY (iso_code, date)
);

COMMENT ON TABLE hospitalizations IS 'Hospital and ICU occupancy metrics per country per day. Source: OWID / national health authorities.';

-- ==============================================================================
-- SECTION 4: OPERATIONAL / AUDIT LAYER
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- ETL_LOGS — Execution log for every ETL pipeline run
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS etl_logs (
    run_id              UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_name       VARCHAR(100)  NOT NULL,
    dag_run_id          VARCHAR(200),           -- Airflow DAG run ID (if triggered by Airflow)
    status              VARCHAR(20)   NOT NULL
                            CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL', 'SKIPPED')),
    -- Row statistics
    rows_downloaded     INTEGER       DEFAULT 0,
    rows_validated      INTEGER       DEFAULT 0,
    rows_rejected       INTEGER       DEFAULT 0,
    rows_inserted       INTEGER       DEFAULT 0,
    rows_updated        INTEGER       DEFAULT 0,
    -- Timing
    started_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    completed_at        TIMESTAMPTZ,
    duration_seconds    NUMERIC(10,2) GENERATED ALWAYS AS (
                            EXTRACT(EPOCH FROM (completed_at - started_at))
                        ) STORED,
    -- Error information
    error_message       TEXT,
    error_traceback     TEXT,
    -- Metadata
    dataset_url         TEXT,
    dataset_checksum    VARCHAR(64),  -- SHA-256 of downloaded file
    dataset_row_count   INTEGER,      -- total rows in source dataset
    source_date_min     DATE,
    source_date_max     DATE,
    metadata            JSONB         DEFAULT '{}'
);

COMMENT ON TABLE  etl_logs              IS 'Complete audit trail for every ETL pipeline execution.';
COMMENT ON COLUMN etl_logs.status       IS 'RUNNING=in progress, SUCCESS=all ok, PARTIAL=loaded with rejected rows, FAILED=aborted, SKIPPED=no new data.';
COMMENT ON COLUMN etl_logs.dataset_checksum IS 'SHA-256 of raw CSV. Detect unchanged datasets to skip re-processing.';

-- ------------------------------------------------------------------------------
-- AUDIT_LOGS — User action audit trail (GDPR-compliant)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id          BIGINT          PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id         UUID            REFERENCES users(user_id) ON DELETE SET NULL,
    username        VARCHAR(100),   -- Denormalized: preserved even if user is deleted
    action          VARCHAR(100)    NOT NULL,  -- e.g. 'LOGIN', 'EXPORT_DATA', 'ETL_TRIGGER'
    resource_type   VARCHAR(100),              -- e.g. 'analytics', 'user', 'etl_log'
    resource_id     VARCHAR(200),              -- PK of the affected resource
    ip_address      INET,
    user_agent      TEXT,
    request_method  VARCHAR(10),
    request_path    TEXT,
    response_status SMALLINT,
    duration_ms     INTEGER,
    metadata        JSONB           DEFAULT '{}',  -- Additional context
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  audit_logs          IS 'Immutable audit trail of all user actions. Append-only — no updates or deletes.';
COMMENT ON COLUMN audit_logs.metadata IS 'JSON blob for arbitrary additional context (e.g. query parameters, filters applied).';

-- ------------------------------------------------------------------------------
-- METADATA — Key-value store for platform configuration and dataset metadata
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS metadata (
    key             VARCHAR(200)    PRIMARY KEY,
    value           TEXT            NOT NULL,
    description     TEXT,
    is_sensitive    BOOLEAN         NOT NULL DEFAULT FALSE,
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_by      UUID            REFERENCES users(user_id) ON DELETE SET NULL
);

COMMENT ON TABLE  metadata            IS 'Platform key-value configuration store. Non-sensitive runtime metadata.';
COMMENT ON COLUMN metadata.is_sensitive IS 'If TRUE, value is masked in API responses and logs.';

-- ==============================================================================
-- SECTION 5: TRIGGERS — Auto-update updated_at timestamps
-- ==============================================================================

CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Apply to all tables with updated_at column
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'roles', 'users', 'countries', 'demographics',
        'daily_metrics', 'vaccinations', 'testing', 'hospitalizations', 'metadata'
    ]
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I;
             CREATE TRIGGER set_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();',
            t, t
        );
    END LOOP;
END;
$$;
