"""
Test script to demonstrate batch predictions with sample data
Run this to see how the new batch prediction feature works
"""

import sys
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder

print("=" * 70)
print("🧪 TESTING BATCH PREDICTIONS WITH SAMPLE DATA")
print("=" * 70)

# Load model and encoder
print("\n1️⃣ Loading Model...")
model = joblib.load("lightgbm_sales_model.pkl")
print("✅ Model loaded successfully")

# Load historical data for encoder
print("\n2️⃣ Loading Historical Data...")
df_historical = pd.read_csv("data/final_dataset.csv")
le = LabelEncoder()
le.fit(df_historical["Model"].unique())
print(f"✅ Encoder fitted with {len(le.classes_)} models: {list(le.classes_)}")

# Load sample data
print("\n3️⃣ Loading Sample Data...")
sales_data = pd.read_csv("data/DMS_Sales_Data_Sample.csv")
leads_data = pd.read_csv("data/CRM_Funnel_Data_Sample - Copy.csv")
print(f"✅ Sales data: {len(sales_data)} records")
print(f"✅ Leads data: {len(leads_data)} records")

# Process data
print("\n4️⃣ Processing Data...")
# Convert dates
sales_data["Booking_Date"] = pd.to_datetime(sales_data["Booking_Date"])
leads_data["Lead_Date"] = pd.to_datetime(leads_data["Lead_Date"])

# Create Year-Month
sales_data["year_month"] = sales_data["Booking_Date"].dt.to_period("M")
leads_data["year_month"] = leads_data["Lead_Date"].dt.to_period("M")

# Convert Yes/No to 1/0
sales_data["Finance_Used_Numeric"] = (sales_data["Finance_Used"] == "Yes").astype(int)
sales_data["Exchange_Used_Numeric"] = (sales_data["Exchange_Used"] == "Yes").astype(int)

# Aggregate SALES data
sales_monthly = (
    sales_data
    .groupby(["Model", "year_month"])
    .agg(
        Units_Sold=("Invoice_ID", "count"),
        Avg_Ex_Showroom_Price=("Ex_Showroom_Price", "mean"),
        Avg_Discount=("Discount", "mean"),
        Finance_Rate=("Finance_Used_Numeric", "mean"),
        Exchange_Rate=("Exchange_Used_Numeric", "mean")
    )
    .reset_index()
)

sales_monthly["year_month"] = sales_monthly["year_month"].dt.to_timestamp()

# Convert Finance and Exchange Intent to numeric
leads_data["Finance_Intent_Numeric"] = (leads_data["Finance_Intent"] == "Yes").astype(int)
leads_data["Exchange_Intent_Numeric"] = (leads_data["Exchange_Intent"] == "Yes").astype(int)

# Aggregate LEAD data
leads_monthly = (
    leads_data
    .groupby(["Preferred_Model", "year_month"])
    .agg(
        Lead_Count=("Lead_ID", "count"),
        Finance_Intent_Rate=("Finance_Intent_Numeric", "mean"),
        Exchange_Intent_Rate=("Exchange_Intent_Numeric", "mean"),
        Avg_Followup_Count=("Followup_Count", "mean")
    )
    .reset_index()
    .rename(columns={"Preferred_Model": "Model"})
)

leads_monthly["year_month"] = leads_monthly["year_month"].dt.to_timestamp()

# Merge datasets
final_df = pd.merge(
    sales_monthly,
    leads_monthly,
    on=["Model", "year_month"],
    how="left"
)

# Fill missing lead values
lead_cols = [
    "Lead_Count",
    "Finance_Intent_Rate",
    "Exchange_Intent_Rate",
    "Avg_Followup_Count"
]
final_df[lead_cols] = final_df[lead_cols].fillna(0)

# Time features
final_df["year"] = final_df["year_month"].dt.year
final_df["month"] = final_df["year_month"].dt.month
final_df["quarter"] = final_df["year_month"].dt.quarter

# Lag features
final_df = final_df.sort_values(["Model", "year_month"])

for lag in [1, 3, 6]:
    final_df[f"lag_{lag}"] = (
        final_df
        .groupby("Model")["Units_Sold"]
        .shift(lag)
    )

final_df["rolling_mean_3"] = (
    final_df
    .groupby("Model")["Units_Sold"]
    .shift(1)
    .rolling(3)
    .mean()
)

final_df["rolling_mean_6"] = (
    final_df
    .groupby("Model")["Units_Sold"]
    .shift(1)
    .rolling(6)
    .mean()
)

final_df = final_df.fillna(0)
print(f"✅ Data processed: {len(final_df)} monthly records")

# Make predictions
print("\n5️⃣ Making Predictions...")
df_pred = final_df.copy()
df_pred["Model_encoded"] = le.transform(df_pred["Model"])

feature_columns = [
    "Model_encoded", "Avg_Ex_Showroom_Price", "Avg_Discount", "Finance_Rate",
    "Exchange_Rate", "Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate",
    "Avg_Followup_Count", "year", "month", "quarter", "lag_1", "lag_3", 
    "lag_6", "rolling_mean_3", "rolling_mean_6"
]

X = df_pred[feature_columns].fillna(0)
predictions = model.predict(X)
df_pred["Predicted_Units"] = np.maximum(predictions, 0).astype(int)

print(f"✅ Predictions generated for {len(df_pred)} records")

# Display results
print("\n" + "=" * 70)
print("📊 PREDICTION RESULTS SUMMARY")
print("=" * 70)

# Summary statistics
print(f"\n📈 Overall Statistics:")
print(f"   • Total Records Processed: {len(df_pred)}")
print(f"   • Total Predicted Units: {df_pred['Predicted_Units'].sum()}")
print(f"   • Average Units per Record: {df_pred['Predicted_Units'].mean():.1f}")
print(f"   • Prediction Range: {df_pred['Predicted_Units'].min()}-{df_pred['Predicted_Units'].max()}")

# By Model
print(f"\n🚗 Predictions by Model:")
model_summary = df_pred.groupby("Model").agg({
    "Predicted_Units": ["sum", "mean", "count"]
}).round(1)
model_summary.columns = ["Total Units", "Avg Units", "Records"]
model_summary = model_summary.astype({"Records": int})
print(model_summary.to_string())

# By Year-Month
print(f"\n📅 Predictions by Month (Top 10):")
monthly_summary = df_pred.groupby("year_month")["Predicted_Units"].sum().sort_values(ascending=False).head(10)
for idx, (month, units) in enumerate(monthly_summary.items(), 1):
    print(f"   {idx}. {month.strftime('%Y-%m')}: {int(units)} units")

# Sample predictions
print(f"\n📋 Sample Predictions (First 10 records):")
sample_cols = ["Model", "year_month", "Units_Sold", "Avg_Ex_Showroom_Price", "Avg_Discount", "Lead_Count", "Predicted_Units"]
print(df_pred[sample_cols].head(10).to_string(index=False))

# Save results
output_file = "batch_predictions_sample.csv"
df_pred[["Model", "year_month", "Units_Sold", "Avg_Ex_Showroom_Price", 
          "Avg_Discount", "Finance_Rate", "Lead_Count", "Predicted_Units"]].to_csv(output_file, index=False)
print(f"\n💾 Results saved to: {output_file}")

print("\n" + "=" * 70)
print("✅ BATCH PREDICTION TEST COMPLETED SUCCESSFULLY!")
print("=" * 70)
print("\n🎯 Next Steps:")
print("   1. Open the Streamlit app: http://localhost:8501")
print("   2. Go to '📤 Batch Predictions' tab")
print("   3. Upload your own CSV files")
print("   4. Click 'Generate Batch Predictions' to see results")
print("\n")
