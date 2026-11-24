-- ==============================================================================
-- FILE: calendar.sql (seed)
-- Enterprise COVID-19 Analytics Platform — Calendar Dimension Seed
-- Generates all dates from 2019-01-01 to 2030-12-31.
-- Run once during initial DB setup.
-- ==============================================================================

INSERT INTO calendar (
    date_value,
    year,
    quarter,
    month,
    month_name,
    week_of_year,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend,
    is_leap_year,
    year_month,
    year_quarter
)
SELECT
    d::DATE                                         AS date_value,
    EXTRACT(YEAR    FROM d)::SMALLINT               AS year,
    EXTRACT(QUARTER FROM d)::SMALLINT               AS quarter,
    EXTRACT(MONTH   FROM d)::SMALLINT               AS month,
    TO_CHAR(d, 'Month')                             AS month_name,
    EXTRACT(WEEK    FROM d)::SMALLINT               AS week_of_year,
    EXTRACT(DAY     FROM d)::SMALLINT               AS day_of_month,
    EXTRACT(DOW     FROM d)::SMALLINT               AS day_of_week,
    TO_CHAR(d, 'Day')                               AS day_name,
    EXTRACT(DOW FROM d) IN (0, 6)                   AS is_weekend,
    EXTRACT(YEAR FROM d) % 4 = 0 AND (
        EXTRACT(YEAR FROM d) % 100 != 0 OR
        EXTRACT(YEAR FROM d) % 400 = 0
    )                                               AS is_leap_year,
    TO_CHAR(d, 'YYYY-MM')                           AS year_month,
    TO_CHAR(d, 'YYYY') || '-Q' ||
        EXTRACT(QUARTER FROM d)::TEXT               AS year_quarter
FROM generate_series(
    '2019-01-01'::DATE,
    '2030-12-31'::DATE,
    '1 day'::INTERVAL
) AS gs(d)
ON CONFLICT (date_value) DO NOTHING;

-- Verify
SELECT
    MIN(date_value) AS first_date,
    MAX(date_value) AS last_date,
    COUNT(*)        AS total_days
FROM calendar;
