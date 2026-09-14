import pandas as pd
import numpy as np
import os
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


# ============================================
# CONFIGURATION
# ============================================

DATA_FILE = "data/processed/AgriTwin-Yield-Dataset.csv"
MODEL_DIR = "backend/models"
MODEL_FILE = os.path.join(MODEL_DIR, "yield_prediction_model.pkl")


# ============================================
# LOAD DATA
# ============================================

print("Loading dataset...")

df = pd.read_csv(DATA_FILE)

print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================
# REMOVE INVALID RECORDS
# ============================================

df = df[df["yield_kg_per_ha"] >= 0]
df = df[df["area_1000_ha"] >= 0]

print("\nRows after cleaning:", len(df))


# ============================================
# FEATURES & TARGET
# ============================================

features = [
    "district_code",
    "state_code",
    "year",
    "crop",
    "district",
    "state_name",
    "area_1000_ha",
    "rainfall_mm",
    "avg_temp_c",
    "max_temp_c",
    "min_temp_c"
]

target = "yield_kg_per_ha"


X = df[features]
y = df[target]


# ============================================
# TIME-BASED TRAIN / TEST SPLIT
# ============================================

train_df = df[df["year"] <= 2014]
test_df = df[df["year"] >= 2015]

X_train = train_df[features]
y_train = train_df[target]

X_test = test_df[features]
y_test = test_df[target]


print("\n========================================")
print("TRAIN / TEST SPLIT")
print("========================================")

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))

print(
    "Training years:",
    train_df["year"].min(),
    "to",
    train_df["year"].max()
)

print(
    "Testing years:",
    test_df["year"].min(),
    "to",
    test_df["year"].max()
)


# ============================================
# CATEGORICAL FEATURES
# ============================================

categorical_features = [
    "crop",
    "district",
    "state_name"
]

numeric_features = [
    "district_code",
    "state_code",
    "year",
    "area_1000_ha",
    "rainfall_mm",
    "avg_temp_c",
    "max_temp_c",
    "min_temp_c"
]


# ============================================
# PREPROCESSING
# ============================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ============================================
# XGBOOST MODEL
# ============================================

model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)


# ============================================
# COMPLETE PIPELINE
# ============================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================
# TRAIN
# ============================================

print("\n========================================")
print("TRAINING XGBOOST MODEL")
print("========================================")

pipeline.fit(X_train, y_train)

print("Training completed.")


# ============================================
# PREDICTION
# ============================================

print("\nGenerating predictions...")

y_pred = pipeline.predict(X_test)


# ============================================
# EVALUATION
# ============================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n========================================")
print("MODEL PERFORMANCE")
print("========================================")

print(f"MAE  : {mae:.2f} kg/ha")
print(f"RMSE : {rmse:.2f} kg/ha")
print(f"R²   : {r2:.4f}")


# ============================================
# SAMPLE PREDICTIONS
# ============================================

results = test_df[
    [
        "district",
        "year",
        "crop",
        "yield_kg_per_ha"
    ]
].copy()

results["predicted_yield_kg_per_ha"] = y_pred

print("\n========================================")
print("SAMPLE PREDICTIONS")
print("========================================")

print(
    results.head(15).to_string(
        index=False
    )
)


# ============================================
# SAVE MODEL
# ============================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_FILE
)


print("\n========================================")
print("MODEL SAVED")
print("========================================")

print(
    "Model:",
    MODEL_FILE
)