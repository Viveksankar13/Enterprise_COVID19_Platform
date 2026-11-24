import logging
from typing import Dict, Tuple
import pandas as pd

logger = logging.getLogger("etl.cleaner")


class DataCleaner:
    """
    Cleans raw OWID data and normalizes it into 6 separate pandas DataFrames
    matching the normalized database schema structure.
    """

    def clean_and_normalize(
        self, df: pd.DataFrame
    ) -> Tuple[
        pd.DataFrame,  # countries
        pd.DataFrame,  # demographics
        pd.DataFrame,  # daily_metrics
        pd.DataFrame,  # vaccinations
        pd.DataFrame,  # testing
        pd.DataFrame,  # hospitalizations
    ]:
        logger.info("Starting cleaning and database normalization.")

        # Ensure date format is standard
        df["date"] = pd.to_datetime(df["date"]).dt.date

        # Fill text NaNs where appropriate
        df["continent"] = df["continent"].fillna("Aggregate")
        if "income_group" not in df.columns:
            df["income_group"] = "Unknown"
        else:
            df["income_group"] = df["income_group"].fillna("Unknown")

        # ── 1. Countries Dimension ──
        # Determine aggregate rows (OWID_ custom prefixes)
        df["is_aggregate"] = df["iso_code"].str.startswith("OWID_") | (df["iso_code"] == "WRL")
        
        countries_cols = ["iso_code", "continent", "location", "income_group", "is_aggregate"]
        countries_df = df[countries_cols].drop_duplicates(subset=["iso_code"]).copy()
        countries_df["is_active"] = True
        countries_df["data_source"] = "OWID"

        # ── 2. Demographics Dimension ──
        demographics_cols = [
            "iso_code", "population", "population_density", "median_age",
            "aged_65_older", "aged_70_older", "gdp_per_capita", "extreme_poverty",
            "cardiovasc_death_rate", "diabetes_prevalence", "female_smokers",
            "male_smokers", "handwashing_facilities", "hospital_beds_per_thousand",
            "life_expectancy", "human_development_index"
        ]
        # Keep one demographic snapshot per country (the latest row)
        demographics_df = df.sort_values("date").drop_duplicates(subset=["iso_code"], keep="last")[demographics_cols].copy()
        demographics_df["data_year"] = 2023  # Reference baseline year

        # ── 3. Daily Metrics Facts ──
        daily_metrics_cols = [
            "iso_code", "date", "new_cases", "new_cases_smoothed", "total_cases",
            "new_cases_per_million", "new_cases_smoothed_per_million", "total_cases_per_million",
            "new_deaths", "new_deaths_smoothed", "total_deaths",
            "new_deaths_per_million", "new_deaths_smoothed_per_million", "total_deaths_per_million",
            "reproduction_rate", "stringency_index"
        ]
        daily_metrics_df = df[df["iso_code"].isin(countries_df["iso_code"])][daily_metrics_cols].copy()

        # ── 4. Vaccinations Facts ──
        vaccinations_cols = [
            "iso_code", "date", "total_vaccinations", "people_vaccinated",
            "people_fully_vaccinated", "total_boosters", "new_vaccinations",
            "new_vaccinations_smoothed", "total_vaccinations_per_hundred",
            "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred",
            "total_boosters_per_hundred", "new_vaccinations_smoothed_per_million"
        ]
        # Drop rows where all vaccination metrics are null to save space
        vacc_df = df[vaccinations_cols].dropna(subset=vaccinations_cols[2:], how="all").copy()

        # ── 5. Testing Facts ──
        testing_cols = [
            "iso_code", "date", "new_tests", "total_tests", "new_tests_smoothed",
            "total_tests_per_thousand", "new_tests_per_thousand", "new_tests_smoothed_per_thousand",
            "positive_rate", "tests_per_case", "tests_units"
        ]
        testing_df = df[testing_cols].dropna(subset=testing_cols[2:-1], how="all").copy()

        # ── 6. Hospitalizations Facts ──
        hospitalizations_cols = [
            "iso_code", "date", "icu_patients", "icu_patients_per_million",
            "hosp_patients", "hosp_patients_per_million", "weekly_icu_admissions",
            "weekly_icu_admissions_per_million", "weekly_hosp_admissions",
            "weekly_hosp_admissions_per_million"
        ]
        hosp_df = df[hospitalizations_cols].dropna(subset=hospitalizations_cols[2:], how="all").copy()

        logger.info(
            f"Normalization completed:\n"
            f"  Countries:      {len(countries_df)} rows\n"
            f"  Demographics:   {len(demographics_df)} rows\n"
            f"  Daily Metrics:  {len(daily_metrics_df)} rows\n"
            f"  Vaccinations:   {len(vacc_df)} rows\n"
            f"  Testing:        {len(testing_df)} rows\n"
            f"  Hospital:       {len(hosp_df)} rows"
        )

        return countries_df, demographics_df, daily_metrics_df, vacc_df, testing_df, hosp_df
