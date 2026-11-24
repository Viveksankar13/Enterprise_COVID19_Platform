"""
Alembic migration: 001_initial_schema

Creates the complete initial database schema for the Enterprise COVID-19
Analytics Platform, including all tables, indexes, constraints, and seeds.

Revision ID : 001_initial_schema
Revises     : (none — initial migration)
Create Date : 2026-07-07
"""

from __future__ import annotations

import os
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID

# ─────────────────────────────────────────────────────────────────────────────
# Revision Identifiers
# ─────────────────────────────────────────────────────────────────────────────
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None

# Path to SQL scripts (relative to the migration's env.py)
DB_DIR = Path(__file__).parents[3] / "database"


def _execute_sql_file(relative_path: str) -> None:
    """Execute a SQL file from the database directory."""
    sql_path = DB_DIR / relative_path
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    sql = sql_path.read_text(encoding="utf-8")
    op.execute(sa.text(sql))


def upgrade() -> None:
    """
    Apply the initial schema.

    Execution order:
    1. Extensions (uuid-ossp, pg_trgm, etc.)
    2. Tables (DDL in dependency order)
    3. Constraints (CHECK constraints)
    4. Indexes (B-Tree, BRIN, GIN, covering)
    5. Views (analytical, materialized, KPI)
    6. Seeds (calendar, roles, metadata)
    """

    # ── 1. Extensions ────────────────────────────────────────────────────────
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "btree_gin"'))
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "citext"'))
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"'))

    # ── 2. Core Tables ───────────────────────────────────────────────────────
    # SECURITY LAYER
    op.create_table(
        "roles",
        sa.Column("role_id",     sa.SmallInteger(), primary_key=True, autoincrement=True),
        sa.Column("name",        sa.String(50),     nullable=False,   unique=True),
        sa.Column("description", sa.Text(),         nullable=True),
        sa.Column("is_active",   sa.Boolean(),      nullable=False,   server_default=sa.text("TRUE")),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "permissions",
        sa.Column("permission_id", sa.Integer(),    primary_key=True, autoincrement=True),
        sa.Column("role_id",       sa.SmallInteger(), sa.ForeignKey("roles.role_id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource",      sa.String(100),  nullable=False),
        sa.Column("action",        sa.String(50),   nullable=False),
        sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("role_id", "resource", "action", name="uq_permissions_role_resource_action"),
    )

    op.create_table(
        "users",
        sa.Column("user_id",       UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email",         sa.String(255),    nullable=False,  unique=True),
        sa.Column("username",      sa.String(100),    nullable=False,  unique=True),
        sa.Column("full_name",     sa.String(200),    nullable=True),
        sa.Column("password_hash", sa.Text(),         nullable=False),
        sa.Column("role_id",       sa.SmallInteger(), sa.ForeignKey("roles.role_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("is_active",     sa.Boolean(),      nullable=False,  server_default=sa.text("TRUE")),
        sa.Column("is_verified",   sa.Boolean(),      nullable=False,  server_default=sa.text("FALSE")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("login_count",   sa.Integer(),      nullable=False,  server_default=sa.text("0")),
        sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",    sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # REFERENCE LAYER
    op.create_table(
        "countries",
        sa.Column("iso_code",          sa.String(8),   primary_key=True),
        sa.Column("continent",         sa.String(50),  nullable=True),
        sa.Column("location",          sa.String(200), nullable=False),
        sa.Column("income_group",      sa.String(50),  nullable=True),
        sa.Column("who_region",        sa.String(50),  nullable=True),
        sa.Column("world_bank_region", sa.String(100), nullable=True),
        sa.Column("is_aggregate",      sa.Boolean(),   nullable=False, server_default=sa.text("FALSE")),
        sa.Column("is_active",         sa.Boolean(),   nullable=False, server_default=sa.text("TRUE")),
        sa.Column("data_source",       sa.String(100), nullable=True,  server_default=sa.text("'OWID'")),
        sa.Column("created_at",        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",        sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "demographics",
        sa.Column("iso_code",                   sa.String(8),     sa.ForeignKey("countries.iso_code", ondelete="CASCADE"), primary_key=True),
        sa.Column("population",                 sa.BigInteger(),  nullable=True),
        sa.Column("population_density",         sa.Numeric(10,3), nullable=True),
        sa.Column("median_age",                 sa.Numeric(5,2),  nullable=True),
        sa.Column("aged_65_older",              sa.Numeric(6,3),  nullable=True),
        sa.Column("aged_70_older",              sa.Numeric(6,3),  nullable=True),
        sa.Column("gdp_per_capita",             sa.Numeric(12,3), nullable=True),
        sa.Column("extreme_poverty",            sa.Numeric(6,3),  nullable=True),
        sa.Column("cardiovasc_death_rate",      sa.Numeric(8,3),  nullable=True),
        sa.Column("diabetes_prevalence",        sa.Numeric(6,3),  nullable=True),
        sa.Column("female_smokers",             sa.Numeric(6,3),  nullable=True),
        sa.Column("male_smokers",               sa.Numeric(6,3),  nullable=True),
        sa.Column("handwashing_facilities",     sa.Numeric(6,3),  nullable=True),
        sa.Column("hospital_beds_per_thousand", sa.Numeric(6,3),  nullable=True),
        sa.Column("life_expectancy",            sa.Numeric(5,2),  nullable=True),
        sa.Column("human_development_index",    sa.Numeric(5,4),  nullable=True),
        sa.Column("data_year",                  sa.SmallInteger(), nullable=True),
        sa.Column("updated_at",                 sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "calendar",
        sa.Column("date_value",  sa.Date(),         primary_key=True),
        sa.Column("year",        sa.SmallInteger(), nullable=False),
        sa.Column("quarter",     sa.SmallInteger(), nullable=False),
        sa.Column("month",       sa.SmallInteger(), nullable=False),
        sa.Column("month_name",  sa.String(10),     nullable=False),
        sa.Column("week_of_year",sa.SmallInteger(), nullable=False),
        sa.Column("day_of_month",sa.SmallInteger(), nullable=False),
        sa.Column("day_of_week", sa.SmallInteger(), nullable=False),
        sa.Column("day_name",    sa.String(10),     nullable=False),
        sa.Column("is_weekend",  sa.Boolean(),      nullable=False),
        sa.Column("is_leap_year",sa.Boolean(),      nullable=False),
        sa.Column("year_month",  sa.String(7),      nullable=False),
        sa.Column("year_quarter",sa.String(7),      nullable=False),
    )

    # FACT TABLES
    op.create_table(
        "daily_metrics",
        sa.Column("iso_code",                       sa.String(8),     sa.ForeignKey("countries.iso_code"), primary_key=True),
        sa.Column("date",                           sa.Date(),        sa.ForeignKey("calendar.date_value"), primary_key=True),
        sa.Column("new_cases",                      sa.BigInteger(),  nullable=True),
        sa.Column("new_cases_smoothed",             sa.Numeric(14,3), nullable=True),
        sa.Column("total_cases",                    sa.BigInteger(),  nullable=True),
        sa.Column("new_cases_per_million",          sa.Numeric(14,3), nullable=True),
        sa.Column("new_cases_smoothed_per_million", sa.Numeric(14,3), nullable=True),
        sa.Column("total_cases_per_million",        sa.Numeric(14,3), nullable=True),
        sa.Column("new_deaths",                     sa.Integer(),     nullable=True),
        sa.Column("new_deaths_smoothed",            sa.Numeric(12,3), nullable=True),
        sa.Column("total_deaths",                   sa.BigInteger(),  nullable=True),
        sa.Column("new_deaths_per_million",         sa.Numeric(12,3), nullable=True),
        sa.Column("new_deaths_smoothed_per_million",sa.Numeric(12,3), nullable=True),
        sa.Column("total_deaths_per_million",       sa.Numeric(12,3), nullable=True),
        sa.Column("reproduction_rate",              sa.Numeric(6,3),  nullable=True),
        sa.Column("stringency_index",               sa.Numeric(6,3),  nullable=True),
        sa.Column("etl_run_id",                     UUID(as_uuid=True), nullable=True),
        sa.Column("loaded_at",                      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",                     sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "vaccinations",
        sa.Column("iso_code",                             sa.String(8),     sa.ForeignKey("countries.iso_code"), primary_key=True),
        sa.Column("date",                                 sa.Date(),        sa.ForeignKey("calendar.date_value"), primary_key=True),
        sa.Column("total_vaccinations",                   sa.BigInteger(),  nullable=True),
        sa.Column("people_vaccinated",                    sa.BigInteger(),  nullable=True),
        sa.Column("people_fully_vaccinated",              sa.BigInteger(),  nullable=True),
        sa.Column("total_boosters",                       sa.BigInteger(),  nullable=True),
        sa.Column("new_vaccinations",                     sa.Integer(),     nullable=True),
        sa.Column("new_vaccinations_smoothed",            sa.Numeric(14,3), nullable=True),
        sa.Column("total_vaccinations_per_hundred",       sa.Numeric(8,3),  nullable=True),
        sa.Column("people_vaccinated_per_hundred",        sa.Numeric(8,3),  nullable=True),
        sa.Column("people_fully_vaccinated_per_hundred",  sa.Numeric(8,3),  nullable=True),
        sa.Column("total_boosters_per_hundred",           sa.Numeric(8,3),  nullable=True),
        sa.Column("new_vaccinations_smoothed_per_million",sa.Numeric(12,3), nullable=True),
        sa.Column("etl_run_id",                           UUID(as_uuid=True), nullable=True),
        sa.Column("loaded_at",                            sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",                           sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "testing",
        sa.Column("iso_code",                      sa.String(8),     sa.ForeignKey("countries.iso_code"), primary_key=True),
        sa.Column("date",                          sa.Date(),        sa.ForeignKey("calendar.date_value"), primary_key=True),
        sa.Column("new_tests",                     sa.Integer(),     nullable=True),
        sa.Column("total_tests",                   sa.BigInteger(),  nullable=True),
        sa.Column("new_tests_smoothed",            sa.Numeric(12,3), nullable=True),
        sa.Column("total_tests_per_thousand",      sa.Numeric(12,3), nullable=True),
        sa.Column("new_tests_per_thousand",        sa.Numeric(10,3), nullable=True),
        sa.Column("new_tests_smoothed_per_thousand",sa.Numeric(10,3),nullable=True),
        sa.Column("positive_rate",                 sa.Numeric(7,5),  nullable=True),
        sa.Column("tests_per_case",                sa.Numeric(10,3), nullable=True),
        sa.Column("tests_units",                   sa.String(50),    nullable=True),
        sa.Column("etl_run_id",                    UUID(as_uuid=True), nullable=True),
        sa.Column("loaded_at",                     sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",                    sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "hospitalizations",
        sa.Column("iso_code",                          sa.String(8),     sa.ForeignKey("countries.iso_code"), primary_key=True),
        sa.Column("date",                              sa.Date(),        sa.ForeignKey("calendar.date_value"), primary_key=True),
        sa.Column("icu_patients",                      sa.Integer(),     nullable=True),
        sa.Column("icu_patients_per_million",          sa.Numeric(10,3), nullable=True),
        sa.Column("hosp_patients",                     sa.Integer(),     nullable=True),
        sa.Column("hosp_patients_per_million",         sa.Numeric(10,3), nullable=True),
        sa.Column("weekly_icu_admissions",             sa.Numeric(12,3), nullable=True),
        sa.Column("weekly_icu_admissions_per_million", sa.Numeric(10,3), nullable=True),
        sa.Column("weekly_hosp_admissions",            sa.Numeric(12,3), nullable=True),
        sa.Column("weekly_hosp_admissions_per_million",sa.Numeric(10,3), nullable=True),
        sa.Column("etl_run_id",                        UUID(as_uuid=True), nullable=True),
        sa.Column("loaded_at",                         sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",                        sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # OPERATIONAL LAYER
    op.create_table(
        "etl_logs",
        sa.Column("run_id",            UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("pipeline_name",     sa.String(100),    nullable=False),
        sa.Column("dag_run_id",        sa.String(200),    nullable=True),
        sa.Column("status",            sa.String(20),     nullable=False, server_default=sa.text("'RUNNING'")),
        sa.Column("rows_downloaded",   sa.Integer(),      nullable=False, server_default=sa.text("0")),
        sa.Column("rows_validated",    sa.Integer(),      nullable=False, server_default=sa.text("0")),
        sa.Column("rows_rejected",     sa.Integer(),      nullable=False, server_default=sa.text("0")),
        sa.Column("rows_inserted",     sa.Integer(),      nullable=False, server_default=sa.text("0")),
        sa.Column("rows_updated",      sa.Integer(),      nullable=False, server_default=sa.text("0")),
        sa.Column("started_at",        sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at",      sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message",     sa.Text(),         nullable=True),
        sa.Column("error_traceback",   sa.Text(),         nullable=True),
        sa.Column("dataset_url",       sa.Text(),         nullable=True),
        sa.Column("dataset_checksum",  sa.String(64),     nullable=True),
        sa.Column("dataset_row_count", sa.Integer(),      nullable=True),
        sa.Column("source_date_min",   sa.Date(),         nullable=True),
        sa.Column("source_date_max",   sa.Date(),         nullable=True),
        sa.Column("metadata",          JSONB,             nullable=False, server_default=sa.text("'{}'")),
    )

    op.create_table(
        "audit_logs",
        sa.Column("log_id",         sa.BigInteger(),   primary_key=True, autoincrement=True),
        sa.Column("user_id",        UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
        sa.Column("username",       sa.String(100),    nullable=True),
        sa.Column("action",         sa.String(100),    nullable=False),
        sa.Column("resource_type",  sa.String(100),    nullable=True),
        sa.Column("resource_id",    sa.String(200),    nullable=True),
        sa.Column("ip_address",     INET,              nullable=True),
        sa.Column("user_agent",     sa.Text(),         nullable=True),
        sa.Column("request_method", sa.String(10),     nullable=True),
        sa.Column("request_path",   sa.Text(),         nullable=True),
        sa.Column("response_status",sa.SmallInteger(), nullable=True),
        sa.Column("duration_ms",    sa.Integer(),      nullable=True),
        sa.Column("metadata",       JSONB,             nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at",     sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "metadata",
        sa.Column("key",          sa.String(200), primary_key=True),
        sa.Column("value",        sa.Text(),      nullable=False),
        sa.Column("description",  sa.Text(),      nullable=True),
        sa.Column("is_sensitive", sa.Boolean(),   nullable=False, server_default=sa.text("FALSE")),
        sa.Column("updated_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_by",   UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
    )

    # ── 3. Indexes ────────────────────────────────────────────────────────────
    # Core indexes (the SQL file has all indexes including GIN and BRIN)
    op.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS idx_countries_continent
            ON countries (continent) WHERE continent IS NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_countries_active_not_aggregate
            ON countries (iso_code) WHERE is_active = TRUE AND is_aggregate = FALSE;

        CREATE INDEX IF NOT EXISTS idx_daily_metrics_date
            ON daily_metrics (date);

        CREATE INDEX IF NOT EXISTS idx_daily_metrics_date_brin
            ON daily_metrics USING BRIN (date) WITH (pages_per_range = 32);

        CREATE INDEX IF NOT EXISTS idx_daily_metrics_trend_covering
            ON daily_metrics (iso_code, date)
            INCLUDE (new_cases, new_cases_smoothed, new_deaths, new_deaths_smoothed,
                     total_cases, total_deaths, reproduction_rate, stringency_index);

        CREATE INDEX IF NOT EXISTS idx_vaccinations_date_brin
            ON vaccinations USING BRIN (date) WITH (pages_per_range = 32);

        CREATE INDEX IF NOT EXISTS idx_testing_date_brin
            ON testing USING BRIN (date) WITH (pages_per_range = 32);

        CREATE INDEX IF NOT EXISTS idx_hospitalizations_date_brin
            ON hospitalizations USING BRIN (date) WITH (pages_per_range = 32);

        CREATE INDEX IF NOT EXISTS idx_etl_logs_started_at_desc
            ON etl_logs (started_at DESC);

        CREATE INDEX IF NOT EXISTS idx_etl_logs_status
            ON etl_logs (status, started_at DESC);

        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at_brin
            ON audit_logs USING BRIN (created_at) WITH (pages_per_range = 64);

        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id
            ON audit_logs (user_id, created_at DESC) WHERE user_id IS NOT NULL;
    """))

    # ── 4. Auto-update triggers ───────────────────────────────────────────────
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION trigger_set_updated_at()
        RETURNS TRIGGER LANGUAGE plpgsql AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$;
    """))
    for table in ["roles", "users", "countries", "demographics",
                  "daily_metrics", "vaccinations", "testing", "hospitalizations", "metadata"]:
        op.execute(sa.text(f"""
            DROP TRIGGER IF EXISTS set_updated_at ON {table};
            CREATE TRIGGER set_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
        """))

    # ── 5. Calendar seed ─────────────────────────────────────────────────────
    op.execute(sa.text("""
        INSERT INTO calendar (
            date_value, year, quarter, month, month_name, week_of_year,
            day_of_month, day_of_week, day_name, is_weekend, is_leap_year,
            year_month, year_quarter
        )
        SELECT
            d::DATE,
            EXTRACT(YEAR FROM d)::SMALLINT,
            EXTRACT(QUARTER FROM d)::SMALLINT,
            EXTRACT(MONTH FROM d)::SMALLINT,
            TO_CHAR(d, 'Month'),
            EXTRACT(WEEK FROM d)::SMALLINT,
            EXTRACT(DAY FROM d)::SMALLINT,
            EXTRACT(DOW FROM d)::SMALLINT,
            TO_CHAR(d, 'Day'),
            EXTRACT(DOW FROM d) IN (0, 6),
            EXTRACT(YEAR FROM d) % 4 = 0 AND (
                EXTRACT(YEAR FROM d) % 100 != 0 OR
                EXTRACT(YEAR FROM d) % 400 = 0
            ),
            TO_CHAR(d, 'YYYY-MM'),
            TO_CHAR(d, 'YYYY') || '-Q' || EXTRACT(QUARTER FROM d)::TEXT
        FROM generate_series('2019-01-01'::DATE, '2030-12-31'::DATE, '1 day'::INTERVAL) AS gs(d)
        ON CONFLICT (date_value) DO NOTHING;
    """))

    # ── 6. RBAC seed ─────────────────────────────────────────────────────────
    op.execute(sa.text("""
        INSERT INTO roles (name, description) VALUES
            ('admin',    'Full platform access'),
            ('analyst',  'Read dashboards, run queries, export data'),
            ('viewer',   'Read-only dashboard access'),
            ('api_user', 'Programmatic API access')
        ON CONFLICT (name) DO NOTHING;
    """))


def downgrade() -> None:
    """
    Drop all tables in reverse dependency order.

    WARNING: This is a DESTRUCTIVE operation — all data will be lost.
    """
    # Drop triggers first
    for table in ["roles", "users", "countries", "demographics",
                  "daily_metrics", "vaccinations", "testing", "hospitalizations", "metadata"]:
        op.execute(sa.text(f"DROP TRIGGER IF EXISTS set_updated_at ON {table};"))

    op.execute(sa.text("DROP FUNCTION IF EXISTS trigger_set_updated_at() CASCADE;"))

    # Drop fact tables
    op.drop_table("hospitalizations")
    op.drop_table("testing")
    op.drop_table("vaccinations")
    op.drop_table("daily_metrics")

    # Drop operational tables
    op.drop_table("audit_logs")
    op.drop_table("etl_logs")
    op.drop_table("metadata")

    # Drop dimension tables
    op.drop_table("demographics")
    op.drop_table("calendar")
    op.drop_table("countries")

    # Drop security tables
    op.drop_table("permissions")
    op.drop_table("users")
    op.drop_table("roles")

    # Drop extensions
    op.execute(sa.text('DROP EXTENSION IF EXISTS "citext" CASCADE'))
    op.execute(sa.text('DROP EXTENSION IF EXISTS "btree_gin" CASCADE'))
    op.execute(sa.text('DROP EXTENSION IF EXISTS "pg_trgm" CASCADE'))
    op.execute(sa.text('DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE'))
