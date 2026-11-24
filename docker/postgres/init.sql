# ==============================================================================
# POSTGRES INITIALIZATION SCRIPT
# Runs once on first container start to set up the database environment.
# ==============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- Trigram text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";        -- Composite GIN indexes
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query performance

-- Create Airflow database and user
CREATE DATABASE airflow_db;
CREATE USER airflow_user WITH ENCRYPTED PASSWORD 'PLACEHOLDER_REPLACED_BY_ENV';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;

-- Create read-only analytics user (for Power BI / BI tools)
CREATE USER analytics_reader WITH ENCRYPTED PASSWORD 'PLACEHOLDER_REPLACED_BY_ENV';
GRANT CONNECT ON DATABASE covid19_analytics TO analytics_reader;
GRANT USAGE ON SCHEMA public TO analytics_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_reader;

-- Performance tuning
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET track_activity_query_size = 2048;
