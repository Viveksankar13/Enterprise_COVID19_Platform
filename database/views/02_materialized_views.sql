-- ==============================================================================
-- FILE: 02_materialized_views.sql
-- Enterprise COVID-19 Analytics Platform — Materialized Views
--
-- Materialized views cache expensive query results to disk.
-- They must be manually refreshed after each ETL run.
-- Refresh command: SELECT refresh_all_materialized_views();
-- ==============================================================================

-- ==============================================================================
-- MATVIEW: mv_country_kpis
-- Purpose: Pre-computed KPI snapshot per country (latest data + running metrics).
-- Refresh: After every ETL load (triggered by Airflow DAG task).
-- Query time target: < 5ms (compared to ~800ms for live joins).
-- ==============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_country_kpis AS
SELECT
    snap.iso_code,
    snap.country_name,
    snap.continent,
    snap.population,
    snap.gdp_per_capita,
    snap.median_age,
    snap.human_development_index,
    snap.latest_metrics_date,
    snap.total_cases,
    snap.total_deaths,
    snap.new_cases_7day_avg,
    snap.new_deaths_7day_avg,
    snap.new_cases_per_million,
    snap.new_deaths_per_million,
    snap.total_cases_per_million,
    snap.total_deaths_per_million,
    snap.reproduction_rate,
    snap.stringency_index,
    snap.case_fatality_rate_pct,
    -- Vaccination
    snap.latest_vacc_date,
    snap.people_vaccinated_per_hundred,
    snap.people_fully_vaccinated_per_hundred,
    snap.total_boosters_per_hundred,
    -- Testing
    snap.latest_test_date,
    snap.positive_rate,
    snap.total_tests_per_thousand,
    -- Hospital
    snap.latest_hosp_date,
    snap.icu_patients_per_million,
    snap.hosp_patients_per_million,
    -- Ranking (snapshot — will be recalculated on refresh)
    DENSE_RANK() OVER (ORDER BY snap.total_cases         DESC NULLS LAST) AS rank_total_cases,
    DENSE_RANK() OVER (ORDER BY snap.total_deaths        DESC NULLS LAST) AS rank_total_deaths,
    DENSE_RANK() OVER (ORDER BY snap.total_cases_per_million DESC NULLS LAST) AS rank_cases_per_million,
    NTILE(4)     OVER (ORDER BY snap.total_deaths_per_million DESC NULLS LAST) AS quartile_death_burden,
    NTILE(4)     OVER (ORDER BY snap.people_fully_vaccinated_per_hundred DESC NULLS LAST) AS quartile_vaccination,
    -- Materialisation timestamp
    NOW()   AS materialized_at
FROM v_country_latest_snapshot snap
WHERE snap.is_aggregate = FALSE
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_country_kpis_iso
    ON mv_country_kpis (iso_code);

CREATE INDEX IF NOT EXISTS idx_mv_country_kpis_continent
    ON mv_country_kpis (continent);

CREATE INDEX IF NOT EXISTS idx_mv_country_kpis_total_cases_desc
    ON mv_country_kpis (total_cases DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_mv_country_kpis_rank_total_cases
    ON mv_country_kpis (rank_total_cases);

COMMENT ON MATERIALIZED VIEW mv_country_kpis IS
    'Pre-computed country KPI snapshot. Refreshed after every ETL run. < 5ms query time.';

-- ==============================================================================
-- MATVIEW: mv_global_summary
-- Purpose: Aggregated global statistics for the Executive Dashboard.
-- Refresh: After every ETL load.
-- ==============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_global_summary AS
WITH global_totals AS (
    SELECT
        SUM(kpi.total_cases)                        AS total_cases_worldwide,
        SUM(kpi.total_deaths)                       AS total_deaths_worldwide,
        COUNT(*)                                    AS countries_count,
        SUM(kpi.population)                         AS total_population_covered
    FROM mv_country_kpis kpi
),
latest_daily AS (
    SELECT
        SUM(GREATEST(dm.new_cases,  0))             AS todays_new_cases,
        SUM(GREATEST(dm.new_deaths, 0))             AS todays_new_deaths,
        AVG(dm.reproduction_rate)                   AS avg_reproduction_rate,
        AVG(dm.stringency_index)                    AS avg_stringency_index,
        MAX(dm.date)                                AS data_as_of_date
    FROM daily_metrics dm
    JOIN countries     c ON dm.iso_code = c.iso_code AND c.is_aggregate = FALSE
    WHERE dm.date = (SELECT MAX(date) FROM daily_metrics)
),
vaccination_totals AS (
    SELECT
        SUM(v.people_fully_vaccinated)              AS fully_vaccinated_worldwide,
        AVG(v.people_fully_vaccinated_per_hundred)  AS avg_full_vacc_pct
    FROM vaccinations v
    JOIN countries    c ON v.iso_code = c.iso_code AND c.is_aggregate = FALSE
    WHERE v.date = (SELECT MAX(date) FROM vaccinations)
)
SELECT
    gt.total_cases_worldwide,
    gt.total_deaths_worldwide,
    gt.countries_count,
    gt.total_population_covered,
    ld.todays_new_cases,
    ld.todays_new_deaths,
    ld.avg_reproduction_rate,
    ld.avg_stringency_index,
    ld.data_as_of_date,
    vt.fully_vaccinated_worldwide,
    vt.avg_full_vacc_pct,
    -- Derived KPIs
    ROUND(gt.total_deaths_worldwide::NUMERIC /
          NULLIF(gt.total_cases_worldwide, 0) * 100, 4) AS global_cfr_pct,
    NOW()   AS materialized_at
FROM global_totals gt
CROSS JOIN latest_daily ld
CROSS JOIN vaccination_totals vt
WITH DATA;

COMMENT ON MATERIALIZED VIEW mv_global_summary IS
    'Single-row global summary KPIs. Powers the Executive Dashboard headline cards.';

-- ==============================================================================
-- MATVIEW: mv_monthly_country_trends
-- Purpose: Month-level aggregated metrics per country for Power BI time series.
-- Refresh: After every ETL load (dataset grows by ~30 rows per country per month).
-- ==============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_monthly_country_trends AS
SELECT
    dm.iso_code,
    c.location                          AS country_name,
    c.continent,
    cal.year,
    cal.quarter,
    cal.month,
    cal.month_name,
    cal.year_month,
    cal.year_quarter,
    -- Case aggregates
    SUM(GREATEST(dm.new_cases,  0))     AS monthly_new_cases,
    SUM(GREATEST(dm.new_deaths, 0))     AS monthly_new_deaths,
    AVG(dm.new_cases_smoothed)          AS avg_daily_cases_smoothed,
    AVG(dm.new_deaths_smoothed)         AS avg_daily_deaths_smoothed,
    MAX(dm.new_cases)                   AS peak_daily_cases,
    MAX(dm.new_deaths)                  AS peak_daily_deaths,
    MAX(dm.total_cases)                 AS end_total_cases,
    MAX(dm.total_deaths)                AS end_total_deaths,
    -- Epidemiological
    AVG(dm.reproduction_rate)           AS avg_reproduction_rate,
    AVG(dm.stringency_index)            AS avg_stringency_index,
    -- Vaccination snapshot (last day of month)
    MAX(v.people_fully_vaccinated_per_hundred) AS end_fully_vacc_pct,
    -- Testing
    SUM(GREATEST(t.new_tests,  0))      AS monthly_new_tests,
    AVG(t.positive_rate)                AS avg_positive_rate,
    -- Data quality
    COUNT(*)                            AS days_with_data,
    -- Materialisation
    NOW()                               AS materialized_at
FROM daily_metrics dm
JOIN countries     c   ON dm.iso_code = c.iso_code AND c.is_aggregate = FALSE
JOIN calendar      cal ON dm.date     = cal.date_value
LEFT JOIN vaccinations v ON dm.iso_code = v.iso_code AND dm.date = v.date
LEFT JOIN testing      t ON dm.iso_code = t.iso_code AND dm.date = t.date
GROUP BY
    dm.iso_code, c.location, c.continent,
    cal.year, cal.quarter, cal.month, cal.month_name,
    cal.year_month, cal.year_quarter
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_monthly_country_trends
    ON mv_monthly_country_trends (iso_code, year_month);

CREATE INDEX IF NOT EXISTS idx_mv_monthly_trends_continent_year_month
    ON mv_monthly_country_trends (continent, year_month);

CREATE INDEX IF NOT EXISTS idx_mv_monthly_trends_year_month
    ON mv_monthly_country_trends (year_month);

COMMENT ON MATERIALIZED VIEW mv_monthly_country_trends IS
    'Monthly aggregated metrics per country for Power BI time series. Unique index enables REFRESH CONCURRENTLY.';

-- ==============================================================================
-- MATVIEW: mv_continent_summary
-- Purpose: Continent-level aggregated data for regional analysis views.
-- ==============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_continent_summary AS
SELECT
    c.continent,
    COUNT(DISTINCT kpi.iso_code)                        AS country_count,
    SUM(kpi.population)                                 AS total_population,
    SUM(kpi.total_cases)                                AS total_cases,
    SUM(kpi.total_deaths)                               AS total_deaths,
    ROUND(SUM(kpi.total_cases)::NUMERIC /
          NULLIF(SUM(kpi.population), 0) * 1000000, 2) AS cases_per_million,
    ROUND(SUM(kpi.total_deaths)::NUMERIC /
          NULLIF(SUM(kpi.population), 0) * 1000000, 2) AS deaths_per_million,
    AVG(kpi.people_fully_vaccinated_per_hundred)        AS avg_fully_vacc_pct,
    AVG(kpi.positive_rate)                              AS avg_positive_rate,
    AVG(kpi.reproduction_rate)                          AS avg_reproduction_rate,
    MAX(kpi.latest_metrics_date)                        AS data_as_of_date,
    NOW()                                               AS materialized_at
FROM mv_country_kpis  kpi
JOIN countries         c   ON kpi.iso_code = c.iso_code
WHERE c.continent IS NOT NULL
GROUP BY c.continent
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS uidx_mv_continent_summary_continent
    ON mv_continent_summary (continent);

COMMENT ON MATERIALIZED VIEW mv_continent_summary IS
    'Continent-level aggregated KPIs. Depends on mv_country_kpis — refresh order matters.';

-- ==============================================================================
-- STORED PROCEDURE: refresh_all_materialized_views()
-- Refreshes all materialized views in dependency order.
-- Called by: Airflow DAG task "refresh_materialized_views"
-- ==============================================================================
CREATE OR REPLACE PROCEDURE refresh_all_materialized_views()
LANGUAGE plpgsql
AS $$
DECLARE
    v_start     TIMESTAMPTZ := NOW();
    v_log_msg   TEXT;
BEGIN
    RAISE NOTICE 'Starting materialized view refresh at %', v_start;

    -- Order 1: Base KPIs (no dependencies on other matviews)
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_country_kpis;
    RAISE NOTICE '  ✔ mv_country_kpis refreshed';

    -- Order 2: Monthly trends (independent of mv_country_kpis)
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_country_trends;
    RAISE NOTICE '  ✔ mv_monthly_country_trends refreshed';

    -- Order 3: Continent summary (depends on mv_country_kpis)
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_continent_summary;
    RAISE NOTICE '  ✔ mv_continent_summary refreshed';

    -- Order 4: Global summary (depends on mv_country_kpis)
    REFRESH MATERIALIZED VIEW mv_global_summary;
    RAISE NOTICE '  ✔ mv_global_summary refreshed';

    v_log_msg := format(
        'All materialized views refreshed successfully in %s seconds',
        ROUND(EXTRACT(EPOCH FROM (NOW() - v_start))::NUMERIC, 2)
    );
    RAISE NOTICE '%', v_log_msg;

    -- Insert into metadata for ETL monitoring
    INSERT INTO metadata (key, value, description, updated_at)
    VALUES (
        'last_matview_refresh',
        NOW()::TEXT,
        'Timestamp of last successful materialized view refresh',
        NOW()
    )
    ON CONFLICT (key) DO UPDATE
        SET value = EXCLUDED.value, updated_at = NOW();

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Materialized view refresh failed: % — %', SQLERRM, SQLSTATE;
        RAISE;
END;
$$;

COMMENT ON PROCEDURE refresh_all_materialized_views IS
    'Refreshes all materialized views in dependency order. Safe to call concurrently (uses CONCURRENTLY flag).';
