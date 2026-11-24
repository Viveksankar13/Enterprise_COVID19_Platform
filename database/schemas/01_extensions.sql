-- ==============================================================================
-- FILE: 01_extensions.sql
-- Enterprise COVID-19 Analytics Platform — PostgreSQL Extensions
-- Executed first during database initialization.
-- ==============================================================================

-- UUID generation (used as PKs for users, etl_logs, audit_logs)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigram indexes for fast ILIKE / full-text search on country names
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- GIN index support for composite indexes
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Query performance tracking (visible in pg_stat_statements)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Enable case-insensitive text domain (used for email columns)
CREATE EXTENSION IF NOT EXISTS "citext";

-- Comment on database
COMMENT ON DATABASE covid19_analytics IS
  'Enterprise COVID-19 Analytics Platform — Primary OLTP + Analytical database.
   Schema version: 1.0.0 | Owner: Data Engineering Team';
