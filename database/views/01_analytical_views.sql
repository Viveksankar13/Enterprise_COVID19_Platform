-- ==============================================================================
-- FILE: 01_analytical_views.sql
-- Enterprise COVID-19 Analytics Platform — Standard Analytical Views
--
-- Views here use CTEs + Window Functions and are used by the FastAPI backend.
-- They read from base tables and refresh automatically with each query.
-- Heavy views that are queried repeatedly should become materialized (see 02_).
-- ==============================================================================

-- ==============================================================================
-- VIEW: v_country_latest_snapshot
-- Purpose: Most recent available data point per country across all fact tables.
-- Used by: Executive Dashboard KPI cards, Country Overview API
-- ==============================================================================
CREATE OR REPLACE VIEW v_country_latest_snapshot AS
WITH latest_dates AS (
    -- Find the latest date with data for each fact table per country
    SELECT iso_code, MAX(date) AS latest_metrics_date  FROM daily_metrics    GROUP BY iso_code
),
latest_vacc AS (
    SELECT iso_code, MAX(date) AS latest_vacc_date     FROM vaccinations      GROUP BY iso_code
),
latest_test AS (
    SELECT iso_code, MAX(date) AS latest_test_date     FROM testing           GROUP BY iso_code
),
latest_hosp AS (
    SELECT iso_code, MAX(date) AS latest_hosp_date     FROM hospitalizations  GROUP BY iso_code
)
SELECT
    c.iso_code,
    c.location                          AS country_name,
    c.continent,
    c.is_aggregate,
    -- Demographics
    d.population,
    d.gdp_per_capita,
    d.median_age,
    d.life_expectancy,
    d.human_development_index,
    -- Latest case metrics
    ld.latest_metrics_date,
    dm.total_cases,
    dm.total_deaths,
    dm.new_cases_smoothed               AS new_cases_7day_avg,
    dm.new_deaths_smoothed              AS new_deaths_7day_avg,
    dm.new_cases_per_million,
    dm.new_deaths_per_million,
    dm.total_cases_per_million,
    dm.total_deaths_per_million,
    dm.reproduction_rate,
    dm.stringency_index,
    -- Case Fatality Rate
    CASE
        WHEN COALESCE(dm.total_cases, 0) = 0 THEN NULL
        ELSE ROUND(dm.total_deaths::NUMERIC / dm.total_cases * 100, 4)
    END                                 AS case_fatality_rate_pct,
    -- Latest vaccination metrics
    lv.latest_vacc_date,
    v.people_vaccinated_per_hundred,
    v.people_fully_vaccinated_per_hundred,
    v.total_boosters_per_hundred,
    -- Latest testing metrics
    lt.latest_test_date,
    t.positive_rate,
    t.total_tests_per_thousand,
    -- Latest hospital metrics
    lh.latest_hosp_date,
    h.icu_patients_per_million,
    h.hosp_patients_per_million
FROM countries c
LEFT JOIN demographics        d  ON c.iso_code = d.iso_code
LEFT JOIN latest_dates        ld ON c.iso_code = ld.iso_code
LEFT JOIN daily_metrics       dm ON ld.iso_code = dm.iso_code AND ld.latest_metrics_date = dm.date
LEFT JOIN latest_vacc         lv ON c.iso_code = lv.iso_code
LEFT JOIN vaccinations        v  ON lv.iso_code = v.iso_code AND lv.latest_vacc_date = v.date
LEFT JOIN latest_test         lt ON c.iso_code = lt.iso_code
LEFT JOIN testing             t  ON lt.iso_code = t.iso_code AND lt.latest_test_date = t.date
LEFT JOIN latest_hosp         lh ON c.iso_code = lh.iso_code
LEFT JOIN hospitalizations    h  ON lh.iso_code = h.iso_code AND lh.latest_hosp_date = h.date;

COMMENT ON VIEW v_country_latest_snapshot IS
    'One row per country with its most recent data point from all fact tables. Powers KPI cards and country overview.';

-- ==============================================================================
-- VIEW: v_daily_trends_with_rolling_averages
-- Purpose: Daily metrics with 7-day and 14-day rolling averages computed in SQL.
-- Window functions: AVG OVER (PARTITION BY ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
-- Used by: Trend Analysis page, Area Charts
-- ==============================================================================
CREATE OR REPLACE VIEW v_daily_trends_with_rolling_averages AS
SELECT
    dm.iso_code,
    c.location          AS country_name,
    c.continent,
    dm.date,
    cal.year,
    cal.month,
    cal.year_month,
    cal.year_quarter,
    -- Raw metrics
    dm.new_cases,
    dm.new_deaths,
    dm.total_cases,
    dm.total_deaths,
    dm.reproduction_rate,
    dm.stringency_index,
    -- OWID pre-smoothed (7-day)
    dm.new_cases_smoothed,
    dm.new_deaths_smoothed,
    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: 7-Day Rolling Average (SQL-computed)
    -- ─────────────────────────────────────────────────────────────────────────
    ROUND(AVG(dm.new_cases) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2)               AS new_cases_7day_ma,

    ROUND(AVG(dm.new_deaths) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2)               AS new_deaths_7day_ma,

    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: 14-Day Rolling Average
    -- ─────────────────────────────────────────────────────────────────────────
    ROUND(AVG(dm.new_cases) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
        ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
    ), 2)               AS new_cases_14day_ma,

    ROUND(AVG(dm.new_deaths) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
        ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
    ), 2)               AS new_deaths_14day_ma,

    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: Running Totals (cumulative sum)
    -- ─────────────────────────────────────────────────────────────────────────
    SUM(COALESCE(dm.new_cases,  0)) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS running_total_cases,

    SUM(COALESCE(dm.new_deaths, 0)) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS running_total_deaths,

    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: Week-over-Week change (LAG 7 days)
    -- ─────────────────────────────────────────────────────────────────────────
    dm.new_cases_smoothed - LAG(dm.new_cases_smoothed, 7) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS cases_wow_change,

    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: Previous day value (LAG 1 day)
    -- ─────────────────────────────────────────────────────────────────────────
    LAG(dm.new_cases, 1) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS prev_day_cases,

    LAG(dm.new_deaths, 1) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS prev_day_deaths,

    -- ─────────────────────────────────────────────────────────────────────────
    -- Window Function: LEAD — next day (for forecast context)
    -- ─────────────────────────────────────────────────────────────────────────
    LEAD(dm.new_cases_smoothed, 7) OVER (
        PARTITION BY dm.iso_code
        ORDER BY dm.date
    )                   AS cases_7day_forward,

    -- Per-million for normalization
    dm.new_cases_per_million,
    dm.new_deaths_per_million,
    dm.total_cases_per_million,
    dm.total_deaths_per_million
FROM daily_metrics dm
JOIN countries     c   ON dm.iso_code = c.iso_code
JOIN calendar      cal ON dm.date     = cal.date_value;

COMMENT ON VIEW v_daily_trends_with_rolling_averages IS
    'Daily metrics with 7/14-day rolling averages, running totals, WoW change, LAG/LEAD using window functions.';

-- ==============================================================================
-- VIEW: v_country_rankings
-- Purpose: Rank countries by key metrics using DENSE_RANK and NTILE.
-- Window functions: DENSE_RANK, NTILE, ROW_NUMBER — PARTITION BY continent
-- Used by: Country Comparison, Leaderboard tables
-- ==============================================================================
CREATE OR REPLACE VIEW v_country_rankings AS
WITH latest AS (
    SELECT * FROM v_country_latest_snapshot
    WHERE is_aggregate = FALSE AND population > 1000000  -- exclude micro-states
)
SELECT
    iso_code,
    country_name,
    continent,
    population,
    total_cases,
    total_deaths,
    total_cases_per_million,
    total_deaths_per_million,
    case_fatality_rate_pct,
    new_cases_7day_avg,
    people_fully_vaccinated_per_hundred,
    positive_rate,
    icu_patients_per_million,
    -- ─────────────────────────────────────────────────────────────────────────
    -- GLOBAL RANKINGS (all countries)
    -- ─────────────────────────────────────────────────────────────────────────
    DENSE_RANK() OVER (ORDER BY total_cases          DESC NULLS LAST) AS rank_total_cases,
    DENSE_RANK() OVER (ORDER BY total_deaths         DESC NULLS LAST) AS rank_total_deaths,
    DENSE_RANK() OVER (ORDER BY total_cases_per_million DESC NULLS LAST) AS rank_cases_per_million,
    DENSE_RANK() OVER (ORDER BY total_deaths_per_million DESC NULLS LAST) AS rank_deaths_per_million,
    DENSE_RANK() OVER (ORDER BY case_fatality_rate_pct DESC NULLS LAST) AS rank_case_fatality_rate,
    DENSE_RANK() OVER (ORDER BY people_fully_vaccinated_per_hundred DESC NULLS LAST) AS rank_vaccination,
    DENSE_RANK() OVER (ORDER BY positive_rate        DESC NULLS LAST) AS rank_positivity_rate,
    -- ─────────────────────────────────────────────────────────────────────────
    -- CONTINENTAL RANKINGS
    -- ─────────────────────────────────────────────────────────────────────────
    DENSE_RANK() OVER (
        PARTITION BY continent
        ORDER BY total_cases_per_million DESC NULLS LAST
    )                                           AS rank_cases_per_million_continent,
    DENSE_RANK() OVER (
        PARTITION BY continent
        ORDER BY people_fully_vaccinated_per_hundred DESC NULLS LAST
    )                                           AS rank_vaccination_continent,
    -- ─────────────────────────────────────────────────────────────────────────
    -- NTILE QUARTILES (4 buckets: 1=best, 4=worst for burden metrics)
    -- ─────────────────────────────────────────────────────────────────────────
    NTILE(4) OVER (ORDER BY total_cases_per_million  DESC NULLS LAST) AS quartile_case_burden,
    NTILE(4) OVER (ORDER BY total_deaths_per_million DESC NULLS LAST) AS quartile_death_burden,
    NTILE(4) OVER (ORDER BY people_fully_vaccinated_per_hundred ASC NULLS LAST) AS quartile_vax_coverage,
    -- ─────────────────────────────────────────────────────────────────────────
    -- ROW_NUMBER for pagination
    -- ─────────────────────────────────────────────────────────────────────────
    ROW_NUMBER() OVER (ORDER BY total_cases DESC NULLS LAST) AS row_num_by_total_cases
FROM latest;

COMMENT ON VIEW v_country_rankings IS
    'Country rankings using DENSE_RANK, NTILE, ROW_NUMBER partitioned globally and by continent.';

-- ==============================================================================
-- VIEW: v_monthly_aggregates
-- Purpose: Month-level aggregated statistics for time-series charts.
-- Used by: Trend Analysis, Power BI Monthly dashboard
-- ==============================================================================
CREATE OR REPLACE VIEW v_monthly_aggregates AS
SELECT
    dm.iso_code,
    c.location      AS country_name,
    c.continent,
    cal.year,
    cal.month,
    cal.month_name,
    cal.year_month,
    -- Sum/average within the month
    SUM(GREATEST(dm.new_cases, 0))     AS monthly_cases,
    SUM(GREATEST(dm.new_deaths, 0))    AS monthly_deaths,
    AVG(dm.new_cases_smoothed)         AS avg_daily_cases_smoothed,
    AVG(dm.new_deaths_smoothed)        AS avg_daily_deaths_smoothed,
    AVG(dm.reproduction_rate)          AS avg_reproduction_rate,
    AVG(dm.stringency_index)           AS avg_stringency_index,
    -- Max within month
    MAX(dm.new_cases)                  AS peak_daily_cases,
    MAX(dm.new_deaths)                 AS peak_daily_deaths,
    -- End-of-month cumulative totals (LAST_VALUE via MAX over ordered rows)
    MAX(dm.total_cases)                AS end_of_month_total_cases,
    MAX(dm.total_deaths)               AS end_of_month_total_deaths,
    -- Data completeness
    COUNT(*)                           AS days_with_data,
    COUNT(dm.new_cases)                AS days_with_cases_data,
    COUNT(dm.new_deaths)               AS days_with_deaths_data
FROM daily_metrics dm
JOIN countries     c   ON dm.iso_code = c.iso_code
JOIN calendar      cal ON dm.date     = cal.date_value
GROUP BY
    dm.iso_code, c.location, c.continent,
    cal.year, cal.month, cal.month_name, cal.year_month;

COMMENT ON VIEW v_monthly_aggregates IS
    'Monthly-aggregated case, death, and policy metrics per country. Powers time-series charts.';

-- ==============================================================================
-- VIEW: v_vaccination_progress
-- Purpose: Vaccination milestone tracking with week-over-week acceleration.
-- Used by: Vaccination Analytics page
-- ==============================================================================
CREATE OR REPLACE VIEW v_vaccination_progress AS
SELECT
    v.iso_code,
    c.location                          AS country_name,
    c.continent,
    d.population,
    v.date,
    v.people_vaccinated,
    v.people_fully_vaccinated,
    v.total_boosters,
    v.new_vaccinations_smoothed,
    v.people_vaccinated_per_hundred,
    v.people_fully_vaccinated_per_hundred,
    v.total_boosters_per_hundred,
    -- Vaccination milestones
    CASE
        WHEN v.people_vaccinated_per_hundred >= 25  THEN TRUE ELSE FALSE
    END                                 AS reached_25pct_first_dose,
    CASE
        WHEN v.people_vaccinated_per_hundred >= 50  THEN TRUE ELSE FALSE
    END                                 AS reached_50pct_first_dose,
    CASE
        WHEN v.people_fully_vaccinated_per_hundred >= 50 THEN TRUE ELSE FALSE
    END                                 AS reached_50pct_full,
    CASE
        WHEN v.people_fully_vaccinated_per_hundred >= 70 THEN TRUE ELSE FALSE
    END                                 AS reached_herd_immunity_threshold,
    -- 7-day vaccination rate acceleration
    v.new_vaccinations_smoothed - LAG(v.new_vaccinations_smoothed, 7) OVER (
        PARTITION BY v.iso_code
        ORDER BY v.date
    )                                   AS vacc_rate_wow_change,
    -- Estimated days to 70% full vaccination (simple linear projection)
    CASE
        WHEN COALESCE(v.new_vaccinations_smoothed, 0) = 0
          OR COALESCE(d.population, 0) = 0 THEN NULL
        WHEN v.people_fully_vaccinated_per_hundred >= 70 THEN 0
        ELSE ROUND(
            ((0.70 * d.population) - COALESCE(v.people_fully_vaccinated, 0))
            / NULLIF(v.new_vaccinations_smoothed, 0)
        )
    END                                 AS est_days_to_70pct_full_vacc
FROM vaccinations v
JOIN countries    c ON v.iso_code = c.iso_code
LEFT JOIN demographics d ON v.iso_code = d.iso_code;

COMMENT ON VIEW v_vaccination_progress IS
    'Vaccination milestones, WoW acceleration, and linear projections to 70% coverage threshold.';

-- ==============================================================================
-- VIEW: v_testing_quality
-- Purpose: Testing volume and positivity with WHO benchmark alerts.
-- Used by: Testing Dashboard
-- ==============================================================================
CREATE OR REPLACE VIEW v_testing_quality AS
SELECT
    t.iso_code,
    c.location              AS country_name,
    c.continent,
    t.date,
    t.new_tests,
    t.total_tests,
    t.new_tests_smoothed,
    t.total_tests_per_thousand,
    t.positive_rate,
    t.tests_per_case,
    t.tests_units,
    -- WHO 5% positivity threshold alert
    CASE
        WHEN t.positive_rate > 0.05  THEN 'HIGH_POSITIVITY'
        WHEN t.positive_rate > 0.03  THEN 'MODERATE_POSITIVITY'
        WHEN t.positive_rate IS NULL  THEN 'NO_DATA'
        ELSE 'ACCEPTABLE'
    END                     AS positivity_alert_level,
    -- Rolling 7-day positivity (smoother signal)
    ROUND(AVG(t.positive_rate) OVER (
        PARTITION BY t.iso_code
        ORDER BY t.date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 5)                   AS positive_rate_7day_ma,
    -- Testing intensity vs. prior week
    t.new_tests_smoothed - LAG(t.new_tests_smoothed, 7) OVER (
        PARTITION BY t.iso_code
        ORDER BY t.date
    )                       AS testing_wow_change
FROM testing t
JOIN countries c ON t.iso_code = c.iso_code;

COMMENT ON VIEW v_testing_quality IS
    'Testing volume, 7-day positivity MA, WHO threshold alerts, and WoW testing change.';

-- ==============================================================================
-- VIEW: v_excess_burden
-- Purpose: CFR, excess metrics and burden severity classification.
-- Used by: Mortality Analytics, Executive Dashboard
-- ==============================================================================
CREATE OR REPLACE VIEW v_excess_burden AS
WITH cfr_data AS (
    SELECT
        dm.iso_code,
        dm.date,
        dm.new_cases_smoothed,
        dm.new_deaths_smoothed,
        dm.total_cases,
        dm.total_deaths,
        dm.new_cases_per_million,
        dm.new_deaths_per_million,
        -- 14-day lagged CFR (deaths lag cases by ~14 days)
        CASE
            WHEN LAG(dm.new_cases_smoothed, 14) OVER (
                     PARTITION BY dm.iso_code ORDER BY dm.date
                 ) <= 0 THEN NULL
            ELSE ROUND(
                dm.new_deaths_smoothed /
                NULLIF(LAG(dm.new_cases_smoothed, 14) OVER (
                    PARTITION BY dm.iso_code ORDER BY dm.date
                ), 0) * 100, 4)
        END AS cfr_14day_lag
    FROM daily_metrics dm
)
SELECT
    cf.iso_code,
    c.location              AS country_name,
    c.continent,
    d.population,
    d.human_development_index,
    d.median_age,
    cf.date,
    cf.new_cases_smoothed,
    cf.new_deaths_smoothed,
    cf.total_cases,
    cf.total_deaths,
    cf.new_cases_per_million,
    cf.new_deaths_per_million,
    cf.cfr_14day_lag,
    -- Burden severity score (composite)
    CASE
        WHEN cf.new_cases_per_million > 1000 AND cf.cfr_14day_lag > 2.0 THEN 'CRITICAL'
        WHEN cf.new_cases_per_million > 500  AND cf.cfr_14day_lag > 1.0 THEN 'SEVERE'
        WHEN cf.new_cases_per_million > 100  THEN 'MODERATE'
        WHEN cf.new_cases_per_million > 10   THEN 'LOW'
        ELSE 'MINIMAL'
    END                     AS burden_severity
FROM cfr_data cf
JOIN countries     c  ON cf.iso_code = c.iso_code
LEFT JOIN demographics d  ON cf.iso_code = d.iso_code;

COMMENT ON VIEW v_excess_burden IS
    '14-day lagged CFR, burden severity classification using composite scoring. Powers Mortality Analytics.';

-- ==============================================================================
-- VIEW: v_global_daily_summary
-- Purpose: World-level aggregated metrics by day.
-- Used by: Executive Dashboard global KPI cards
-- ==============================================================================
CREATE OR REPLACE VIEW v_global_daily_summary AS
SELECT
    dm.date,
    cal.year,
    cal.month,
    cal.year_month,
    -- Global sums (exclude aggregate rows to avoid double-counting)
    SUM(GREATEST(dm.new_cases,  0))     AS global_new_cases,
    SUM(GREATEST(dm.new_deaths, 0))     AS global_new_deaths,
    SUM(dm.total_cases)                 AS global_total_cases,
    SUM(dm.total_deaths)                AS global_total_deaths,
    COUNT(DISTINCT dm.iso_code)         AS countries_reporting,
    -- Average of country-level metrics (weighted by presence only)
    AVG(dm.reproduction_rate)           AS avg_reproduction_rate,
    AVG(dm.stringency_index)            AS avg_stringency_index,
    -- Vaccination global totals
    SUM(v.new_vaccinations)             AS global_new_vaccinations,
    SUM(v.total_vaccinations)           AS global_total_vaccinations,
    SUM(v.people_fully_vaccinated)      AS global_people_fully_vaccinated,
    -- Testing global totals
    SUM(t.new_tests)                    AS global_new_tests
FROM daily_metrics dm
JOIN countries     c   ON dm.iso_code = c.iso_code AND c.is_aggregate = FALSE
JOIN calendar      cal ON dm.date     = cal.date_value
LEFT JOIN vaccinations    v   ON dm.iso_code = v.iso_code AND dm.date = v.date
LEFT JOIN testing          t   ON dm.iso_code = t.iso_code AND dm.date = t.date
GROUP BY dm.date, cal.year, cal.month, cal.year_month;

COMMENT ON VIEW v_global_daily_summary IS
    'World-level daily aggregates (non-aggregate countries only) for global KPI dashboard.';

-- ==============================================================================
-- VIEW: v_etl_pipeline_health
-- Purpose: ETL run summary for the Admin / Pipeline Health page.
-- Used by: Admin Dashboard, Pipeline Health API
-- ==============================================================================
CREATE OR REPLACE VIEW v_etl_pipeline_health AS
WITH ranked_runs AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY pipeline_name
            ORDER BY started_at DESC
        ) AS run_rank
    FROM etl_logs
)
SELECT
    el.run_id,
    el.pipeline_name,
    el.status,
    el.started_at,
    el.completed_at,
    EXTRACT(EPOCH FROM (el.completed_at - el.started_at))::INTEGER AS duration_seconds,
    el.rows_downloaded,
    el.rows_validated,
    el.rows_rejected,
    el.rows_inserted,
    el.rows_updated,
    el.dataset_row_count,
    el.source_date_min,
    el.source_date_max,
    el.error_message,
    -- Is this the most recent run for this pipeline?
    (rr.run_rank = 1)                   AS is_latest_run,
    -- Rejection rate
    CASE
        WHEN COALESCE(el.rows_downloaded, 0) = 0 THEN NULL
        ELSE ROUND(
            el.rows_rejected::NUMERIC / el.rows_downloaded * 100, 2
        )
    END                                 AS rejection_rate_pct,
    -- SLA breach flag (ETL taking > 30 minutes)
    (EXTRACT(EPOCH FROM (el.completed_at - el.started_at)) > 1800) AS sla_breached
FROM etl_logs      el
JOIN ranked_runs   rr ON el.run_id = rr.run_id;

COMMENT ON VIEW v_etl_pipeline_health IS
    'ETL run history with rejection rates, SLA breach flags, and latest-run indicators.';
