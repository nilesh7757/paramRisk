"""
Sample Historical Climate Dataset Generator
Generates realistic 30-year climate records (1995-2025) for Gujarat agricultural districts
reflecting historical IMD/ERA5 climate statistics (monsoon deficits and heatwaves).
"""

import csv
import random

def generate_historical_dataset(filepath: str = "data/historical_climate_data.csv"):
    districts = ["Rajkot", "Porbandar", "Junagadh", "Ahmedabad"]
    start_year = 1995
    end_year = 2025

    # Random seed for reproducible dataset
    random.seed(101)

    fieldnames = [
        "year",
        "district",
        "monsoon_sowing_rainfall_mm",
        "consecutive_dry_days",
        "max_summer_temp_c",
        "historical_yield_loss_pct"
    ]

    records = []

    for year in range(start_year, end_year + 1):
        # Known historical drought/El Nino years: 2000, 2002, 2009, 2012, 2018, 2023
        is_drought_year = year in [2000, 2002, 2009, 2012, 2018, 2023]
        # Known heatwave years: 2010, 2016, 2022, 2024
        is_heatwave_year = year in [2010, 2016, 2022, 2024]

        for dist in districts:
            if is_drought_year:
                rainfall = round(random.uniform(65.0, 140.0), 1)
                dry_days = random.randint(18, 32)
                yield_loss = round(random.uniform(35.0, 75.0), 1)
            else:
                rainfall = round(random.uniform(160.0, 420.0), 1)
                dry_days = random.randint(4, 14)
                yield_loss = round(random.uniform(0.0, 15.0), 1)

            if is_heatwave_year:
                max_temp = round(random.uniform(43.5, 47.8), 1)
            else:
                max_temp = round(random.uniform(39.0, 42.8), 1)

            records.append({
                "year": year,
                "district": dist,
                "monsoon_sowing_rainfall_mm": rainfall,
                "consecutive_dry_days": dry_days,
                "max_summer_temp_c": max_temp,
                "historical_yield_loss_pct": yield_loss
            })

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Dataset successfully generated with {len(records)} records at: {filepath}")

if __name__ == "__main__":
    generate_historical_dataset()
