import pandas as pd
import os

INPUT_FILE = "data/raw/ICRISAT-District-Level-Data.csv"
OUTPUT_FILE = "data/processed/ICRISAT-Long-Format.csv"

print("Loading ICRISAT dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Original rows: {len(df)}")
print(f"Original columns: {len(df.columns)}")


# Find all crops automatically
crops = []

for column in df.columns:

    if column.endswith(" AREA (1000 ha)"):

        crop = column.replace(" AREA (1000 ha)", "")

        production_col = f"{crop} PRODUCTION (1000 tons)"
        yield_col = f"{crop} YIELD (Kg per ha)"

        if production_col in df.columns and yield_col in df.columns:
            crops.append(crop)


print(f"\nCrops detected: {len(crops)}")
print(crops)


# Convert wide format → long format
all_crops = []

for crop in crops:

    area_col = f"{crop} AREA (1000 ha)"
    production_col = f"{crop} PRODUCTION (1000 tons)"
    yield_col = f"{crop} YIELD (Kg per ha)"

    temp = df[
        [
            "Dist Code",
            "Year",
            "State Code",
            "State Name",
            "Dist Name",
            area_col,
            production_col,
            yield_col
        ]
    ].copy()

    temp.columns = [
        "district_code",
        "year",
        "state_code",
        "state_name",
        "district",
        "area_1000_ha",
        "production_1000_tons",
        "yield_kg_per_ha"
    ]

    temp["crop"] = crop

    all_crops.append(temp)


# Combine all crops
long_df = pd.concat(all_crops, ignore_index=True)


# Put columns in final order
long_df = long_df[
    [
        "district_code",
        "state_code",
        "state_name",
        "district",
        "year",
        "crop",
        "area_1000_ha",
        "production_1000_tons",
        "yield_kg_per_ha"
    ]
]


# Remove rows where crop has no yield value
long_df = long_df.dropna(
    subset=["yield_kg_per_ha"]
)


# Sort
long_df = long_df.sort_values(
    ["district", "year", "crop"]
).reset_index(drop=True)


# Save
os.makedirs("data/processed", exist_ok=True)

long_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\n================================")
print("CONVERSION COMPLETED")
print("================================")

print(f"Rows: {len(long_df)}")
print(f"Columns: {len(long_df.columns)}")

print(f"\nSaved to:")
print(OUTPUT_FILE)

print("\nFirst 10 rows:")
print(long_df.head(10).to_string(index=False))

print("\nMissing values:")
print(long_df.isnull().sum())

print("\nYear range:")
print(long_df["year"].min(), "to", long_df["year"].max())