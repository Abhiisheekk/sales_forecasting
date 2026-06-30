import pandas as pd

# Load final dataset
df = pd.read_csv("data/final_dataset_fe.csv")

# Convert date column
df["year_month"] = pd.to_datetime(df["year_month"])

# Sort by time (MANDATORY)
df = df.sort_values(["Model", "year_month"])

print(df.shape)
print(df.head())

# Find cutoff date
max_date = df["year_month"].max()
cutoff_date = max_date - pd.DateOffset(months=3)

print("Max date:", max_date)
print("Cutoff date:", cutoff_date)

train_df = df[df["year_month"] <= cutoff_date]
test_df = df[df["year_month"] > cutoff_date]

print("Train shape:", train_df.shape)
print("Test shape:", test_df.shape)

target = "Units_Sold"
drop_cols = [
    "Units_Sold",
    "year_month"   # date not needed directly
]
X_train = train_df.drop(columns=drop_cols)
y_train = train_df[target]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df[target]

print(X_train.shape, y_train.shape)
print(X_test.shape, y_test.shape)

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

X_train["Model"] = le.fit_transform(X_train["Model"])
X_test["Model"] = le.transform(X_test["Model"])

print(X_train.isna().sum().sum())
print(X_test.isna().sum().sum())

import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

# Load dataset
df = pd.read_csv("data/final_dataset.csv")
df["year_month"] = pd.to_datetime(df["year_month"])
df = df.sort_values(["Model", "year_month"])

# Time-based split (last 3 months as test)
max_date = df["year_month"].max()
cutoff_date = max_date - pd.DateOffset(months=3)

train_df = df[df["year_month"] <= cutoff_date]
test_df = df[df["year_month"] > cutoff_date]

target = "Units_Sold"
drop_cols = ["Units_Sold", "year_month"]

X_train = train_df.drop(columns=drop_cols)
y_train = train_df[target]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df[target]

le = LabelEncoder()

X_train["Model"] = le.fit_transform(X_train["Model"])
X_test["Model"] = le.transform(X_test["Model"])

model = lgb.LGBMRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mape = mean_absolute_percentage_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f"MAPE: {mape:.4f}")
print(f"RMSE: {rmse:.2f}")
print(f"RMSE: {rmse:.2f}")

import joblib

joblib.dump(model, "lightgbm_sales_model.pkl")
joblib.dump(le, "model_encoder.pkl")

print("Model saved successfully")
