import pandas as pd
import glob
import os


# ============================================================
# PATHS
# ============================================================

CROP_FILE = "data/processed/ICRISAT-Long-Format.csv"

BASE_PATH = (
    "data/external/ICRISAT-Environment/"
    "RR_IND_2025_488/Reproducbility Package/"
    "raw/DLD/Unapportioned/"
)

OUTPUT_FILE = "data/processed/AgriTwin-Yield-Dataset.csv"


# ============================================================
# HELPER FUNCTION
# ============================================================

def find_file(filename):
    pattern = f"data/external/ICRISAT-Environment/**/*{filename}"
    files = glob.glob(pattern, recursive=True)

    if not files:
        raise FileNotFoundError(
            f"Could not find: {filename}"
        )

    return files[0]


# ============================================================
# LOAD CROP DATA
# ============================================================

print("Loading crop dataset...")

crop_df = pd.read_csv(CROP_FILE)

print("Crop rows:", len(crop_df))


# ============================================================
# LOAD WEATHER DATA
# ============================================================

print("\nLoading precipitation...")

precip_file = find_file(
    "Environment_Precipitation.csv"
)

precip_df = pd.read_csv(precip_file)


print("Loading maximum temperature...")

tmax_file = find_file(
    "Environment_Temperature Maximum.csv"
)

tmax_df = pd.read_csv(tmax_file)


print("Loading minimum temperature...")

tmin_file = find_file(
    "Environment_Temperature Minimum.csv"
)

tmin_df = pd.read_csv(tmin_file)


# ============================================================
# PRECIPITATION FEATURE ENGINEERING
# ============================================================

precip_months = [
    col for col in precip_df.columns
    if "PERCIPITATION" in col
]

precip_df["rainfall_mm"] = precip_df[
    precip_months
].sum(axis=1)


# Keep only required columns

precip_df = precip_df[
    [
        "Dist Code",
        "Year",
        "rainfall_mm"
    ]
]


# ============================================================
# MAXIMUM TEMPERATURE
# ============================================================

tmax_months = [
    col for col in tmax_df.columns
    if "MAXIMUM" in col
]

tmax_df["max_temp_c"] = tmax_df[
    tmax_months
].mean(axis=1)


tmax_df = tmax_df[
    [
        "Dist Code",
        "Year",
        "max_temp_c"
    ]
]


# ============================================================
# MINIMUM TEMPERATURE
# ============================================================

tmin_months = [
    col for col in tmin_df.columns
    if "MINIMUM" in col
]

tmin_df["min_temp_c"] = tmin_df[
    tmin_months
].mean(axis=1)


tmin_df = tmin_df[
    [
        "Dist Code",
        "Year",
        "min_temp_c"
    ]
]


# ============================================================
# MERGE WEATHER DATA
# ============================================================

print("\nMerging weather datasets...")

weather_df = precip_df.merge(
    tmax_df,
    on=["Dist Code", "Year"],
    how="inner"
)

weather_df = weather_df.merge(
    tmin_df,
    on=["Dist Code", "Year"],
    how="inner"
)


# ============================================================
# AVERAGE TEMPERATURE
# ============================================================

weather_df["avg_temp_c"] = (
    weather_df["max_temp_c"]
    + weather_df["min_temp_c"]
) / 2


# ============================================================
# RENAME CROP KEY
# ============================================================

crop_df = crop_df.rename(
    columns={
        "district_code": "Dist Code",
        "year": "Year"
    }
)


# ============================================================
# MERGE CROP + WEATHER
# ============================================================

print("Merging crop + weather data...")

final_df = crop_df.merge(
    weather_df,
    on=["Dist Code", "Year"],
    how="inner"
)


# ============================================================
# REMOVE PRODUCTION
# ============================================================

# Production is not used as an input feature
# because it is directly related to area and yield.

final_df = final_df.drop(
    columns=["production_1000_tons"]
)


# ============================================================
# FINAL COLUMN NAMES
# ============================================================

final_df = final_df.rename(
    columns={
        "Dist Code": "district_code",
        "Year": "year"
    }
)


final_df = final_df[
    [
        "district_code",
        "state_code",
        "state_name",
        "district",
        "year",
        "crop",
        "area_1000_ha",
        "rainfall_mm",
        "avg_temp_c",
        "max_temp_c",
        "min_temp_c",
        "yield_kg_per_ha"
    ]
]


# ============================================================
# CLEAN DATA
# ============================================================

final_df = final_df.drop_duplicates()

final_df = final_df.dropna()


# ============================================================
# SORT
# ============================================================

final_df = final_df.sort_values(
    [
        "district",
        "year",
        "crop"
    ]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# REPORT
# ============================================================

print("\n========================================")
print("FINAL ML DATASET CREATED")
print("========================================")

print("Rows:", len(final_df))
print("Columns:", len(final_df.columns))

print("\nColumns:")
print(final_df.columns.tolist())

print("\nYear range:")
print(
    final_df["year"].min(),
    "to",
    final_df["year"].max()
)

print("\nCrops:")
print(final_df["crop"].nunique())

print("\nMissing values:")
print(final_df.isnull().sum())

print("\nFirst 10 rows:")
print(final_df.head(10).to_string(index=False))

print("\nSaved to:")
print(OUTPUT_FILE)