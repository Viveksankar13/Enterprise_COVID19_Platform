-- ==============================================================================
-- FILE: 03_kpi_views.sql
-- Enterprise COVID-19 Analytics Platform — Business KPI Views
-- Advanced analytics using recursive CTEs and complex window patterns.
-- ==============================================================================

-- ==============================================================================
-- VIEW: v_wave_detection
-- Purpose: Identify epidemic waves using threshold-based detection.
-- Logic: A "wave" begins when 7-day avg cases cross a threshold (50/million)
--        and ends when they drop back below it.
-- Uses: Recursive CTE + Window Functions
-- ==============================================================================
CREATE OR REPLACE VIEW v_wave_detection AS
WITH smoothed AS (
    SELECT
        dm.iso_code,
        c.location          AS country_name,
        d.population,
        dm.date,
        dm.new_cases_smoothed,
        dm.new_cases_per_million,
        COALESCE(dm.new_cases_smoothed / NULLIF(d.population, 0) * 1000000, 0)
                            AS cases_per_million_smoothed
    FROM daily_metrics dm
    JOIN countries     c   ON dm.iso_code = c.iso_code
    LEFT JOIN demographics d ON dm.iso_code = d.iso_code
    WHERE dm.new_cases_smoothed IS NOT NULL
),
wave_flags AS (
    SELECT
        iso_code,
        country_name,
        date,
        cases_per_million_smoothed,
        -- Flag each day as in-wave or not
        CASE WHEN cases_per_million_smoothed >= 50 THEN 1 ELSE 0 END AS in_wave,
        -- Detect wave start: current day is in-wave, previous day was not
        CASE
            WHEN cases_per_million_smoothed >= 50
             AND LAG(cases_per_million_smoothed, 1, 0) OVER (
                     PARTITION BY iso_code ORDER BY date) < 50
            THEN 1 ELSE 0
        END                 AS wave_start,
        -- Detect wave end: current day is not in-wave, previous day was
        CASE
            WHEN cases_per_million_smoothed < 50
             AND LAG(cases_per_million_smoothed, 1, 0) OVER (
                     PARTITION BY iso_code ORDER BY date) >= 50
            THEN 1 ELSE 0
        END                 AS wave_end
    FROM smoothed
),
wave_numbered AS (
    SELECT
        *,
        -- Cumulative sum of wave starts = wave number for each country
        SUM(wave_start) OVER (
            PARTITION BY iso_code
            ORDER BY date
        )                   AS wave_number
    FROM wave_flags
)
SELECT
    iso_code,
    country_name,
    date,
    wave_number,
    in_wave,
    wave_start          AS is_wave_start,
    wave_end            AS is_wave_end,
    cases_per_million_smoothed,
    -- Peak within each wave (using window over wave_number partition)
    MAX(cases_per_million_smoothed) OVER (
        PARTITION BY iso_code, wave_number
    )                   AS wave_peak_cases_per_million,
    -- Days since wave start
    date - FIRST_VALUE(date) OVER (
        PARTITION BY iso_code, wave_number
        ORDER BY date
    )                   AS days_into_wave
FROM wave_numbered
WHERE in_wave = 1;

COMMENT ON VIEW v_wave_detection IS
    'Epidemic wave detection using threshold (50 cases/M/day) with LAG/LEAD and cumulative sum wave numbering.';

-- ==============================================================================
-- VIEW: v_vaccination_equity
-- Purpose: Measure vaccination inequality across income groups.
-- Uses: Window functions + demographic joins
-- ==============================================================================
CREATE OR REPLACE VIEW v_vaccination_equity AS
WITH latest_vacc AS (
    SELECT DISTINCT ON (v.iso_code)
        v.iso_code,
        v.date,
        v.people_fully_vaccinated_per_hundred,
        v.people_vaccinated_per_hundred,
        v.total_boosters_per_hundred
    FROM vaccinations v
    ORDER BY v.iso_code, v.date DESC
)
SELECT
    c.iso_code,
    c.location          AS country_name,
    c.continent,
    c.income_group,
    d.population,
    d.gdp_per_capita,
    d.human_development_index,
    lv.date             AS vaccination_data_date,
    lv.people_vaccinated_per_hundred,
    lv.people_fully_vaccinated_per_hundred,
    lv.total_boosters_per_hundred,
    -- Income group averages (for equity gap calculation)
    AVG(lv.people_fully_vaccinated_per_hundred) OVER (
        PARTITION BY c.income_group
    )                   AS income_group_avg_full_vacc,
    -- Equity gap: country vs. income group average
    lv.people_fully_vaccinated_per_hundred
    - AVG(lv.people_fully_vaccinated_per_hundred) OVER (
        PARTITION BY c.income_group
    )                   AS equity_gap_vs_income_group,
    -- Continent average
    AVG(lv.people_fully_vaccinated_per_hundred) OVER (
        PARTITION BY c.continent
    )                   AS continent_avg_full_vacc,
    -- Rank within income group
    DENSE_RANK() OVER (
        PARTITION BY c.income_group
        ORDER BY lv.people_fully_vaccinated_per_hundred DESC NULLS LAST
    )                   AS rank_in_income_group,
    -- Global percentile
    NTILE(10) OVER (
        ORDER BY lv.people_fully_vaccinated_per_hundred DESC NULLS LAST
    )                   AS vacc_decile_global
FROM countries         c
JOIN latest_vacc       lv ON c.iso_code = lv.iso_code
LEFT JOIN demographics d  ON c.iso_code = d.iso_code
WHERE c.is_aggregate = FALSE;

COMMENT ON VIEW v_vaccination_equity IS
    'Vaccination equity analysis by income group — gap vs. group average, decile ranking, continental average.';

-- ==============================================================================
-- VIEW: v_top_countries_by_metric
-- Purpose: Dynamic top-N country rankings for a given metric (parameterized
--          via wrapper function). This view provides all rankings; the API
--          applies LIMIT after filtering by metric column.
-- ==============================================================================
CREATE OR REPLACE VIEW v_top_countries_by_metric AS
SELECT
    kpi.iso_code,
    kpi.country_name,
    kpi.continent,
    kpi.population,
    kpi.total_cases,
    kpi.total_deaths,
    kpi.total_cases_per_million,
    kpi.total_deaths_per_million,
    kpi.case_fatality_rate_pct,
    kpi.new_cases_7day_avg,
    kpi.new_deaths_7day_avg,
    kpi.people_fully_vaccinated_per_hundred,
    kpi.positive_rate,
    kpi.icu_patients_per_million,
    kpi.reproduction_rate,
    kpi.stringency_index,
    -- All rankings pre-computed
    kpi.rank_total_cases,
    kpi.rank_total_deaths,
    kpi.rank_cases_per_million,
    kpi.quartile_death_burden,
    kpi.quartile_vaccination,
    kpi.latest_metrics_date
FROM mv_country_kpis kpi
WHERE kpi.population > 1000000;  -- Exclude micro-states from league tables

COMMENT ON VIEW v_top_countries_by_metric IS
    'Pre-ranked country metrics for leaderboard API. Apply ORDER BY + LIMIT in API layer.';

-- ==============================================================================
-- VIEW: v_stringency_vs_cases
-- Purpose: Correlation analysis between policy stringency and case trends.
-- Used by: Scatter chart on Policy Analysis page
-- ==============================================================================
CREATE OR REPLACE VIEW v_stringency_vs_cases AS
WITH monthly AS (
    SELECT
        dm.iso_code,
        cal.year_month,
        AVG(dm.stringency_index)       AS avg_stringency,
        AVG(dm.new_cases_per_million)  AS avg_new_cases_per_million,
        AVG(dm.new_deaths_per_million) AS avg_new_deaths_per_million,
        AVG(dm.reproduction_rate)      AS avg_reproduction_rate
    FROM daily_metrics dm
    JOIN calendar cal ON dm.date = cal.date_value
    WHERE dm.stringency_index IS NOT NULL
    GROUP BY dm.iso_code, cal.year_month
)
SELECT
    m.iso_code,
    c.location              AS country_name,
    c.continent,
    d.income_group,
    m.year_month,
    m.avg_stringency,
    m.avg_new_cases_per_million,
    m.avg_new_deaths_per_million,
    m.avg_reproduction_rate,
    -- 1-month lagged cases (stringency effect takes ~4 weeks)
    LAG(m.avg_new_cases_per_million, 1) OVER (
        PARTITION BY m.iso_code
        ORDER BY m.year_month
    )                       AS cases_1month_prior,
    -- Compare this month stringency to previous
    m.avg_stringency - LAG(m.avg_stringency, 1) OVER (
        PARTITION BY m.iso_code
        ORDER BY m.year_month
    )                       AS stringency_change_mom
FROM monthly m
JOIN countries     c ON m.iso_code = c.iso_code
LEFT JOIN countries d ON m.iso_code = d.iso_code
WHERE c.is_aggregate = FALSE;

COMMENT ON VIEW v_stringency_vs_cases IS
    'Monthly stringency vs. case burden with 1-month LAG for policy effect analysis.';

-- ==============================================================================
-- FUNCTION: get_country_trend(p_iso_code, p_start_date, p_end_date, p_metric)
-- Purpose: Parameterized trend retrieval. Called by FastAPI analytics endpoints.
-- Returns: Table of (date, metric_value, rolling_7day_avg, pct_change_wow)
-- ==============================================================================
CREATE OR REPLACE FUNCTION get_country_trend(
    p_iso_code      VARCHAR(8),
    p_start_date    DATE,
    p_end_date      DATE,
    p_metric        VARCHAR(50)  DEFAULT 'new_cases_smoothed'
)
RETURNS TABLE (
    date                DATE,
    metric_value        NUMERIC,
    rolling_7day_avg    NUMERIC,
    pct_change_wow      NUMERIC,
    cumulative_total    NUMERIC
)
LANGUAGE plpgsql
STABLE  -- No side effects, same result for same inputs within transaction
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        $sql$
        WITH base AS (
            SELECT
                dm.date,
                dm.%I::NUMERIC                           AS metric_value
            FROM daily_metrics dm
            WHERE dm.iso_code = %L
              AND dm.date BETWEEN %L AND %L
            ORDER BY dm.date
        )
        SELECT
            b.date,
            b.metric_value,
            ROUND(AVG(b.metric_value) OVER (
                ORDER BY b.date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 3)                                        AS rolling_7day_avg,
            ROUND(
                (b.metric_value
                 - LAG(b.metric_value, 7) OVER (ORDER BY b.date))
                / NULLIF(ABS(LAG(b.metric_value, 7) OVER (ORDER BY b.date)), 0)
                * 100, 2
            )                                           AS pct_change_wow,
            SUM(GREATEST(b.metric_value, 0)) OVER (
                ORDER BY b.date
            )                                           AS cumulative_total
        FROM base b
        $sql$,
        p_metric, p_iso_code, p_start_date, p_end_date
    );
END;
$$;

COMMENT ON FUNCTION get_country_trend IS
    'Parameterized trend function. Returns daily metric with 7-day MA, WoW %, and running total. Called by FastAPI.';
