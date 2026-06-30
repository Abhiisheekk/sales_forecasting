"""
Demonstration of Future Sales Forecasts Feature
Shows how predictions extend forward in time with future timeline
"""

import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

print("\n" + "="*80)
print("🔮 FUTURE SALES FORECASTS - DEMONSTRATION")
print("="*80)

# Load model and data
print("\n1️⃣ Loading model and preparing data...")
model = joblib.load("lightgbm_sales_model.pkl")
df = pd.read_csv("data/final_dataset.csv")
df["year_month"] = pd.to_datetime(df["year_month"])

le = LabelEncoder()
le.fit(df["Model"].unique())
print("✅ Model loaded successfully")

# Load sample processed data
print("\n2️⃣ Processing uploaded data...")
sales_data = pd.read_csv("data/DMS_Sales_Data_Sample.csv")
leads_data = pd.read_csv("data/CRM_Funnel_Data_Sample - Copy.csv")

# Convert and process
sales_data["Booking_Date"] = pd.to_datetime(sales_data["Booking_Date"])
leads_data["Lead_Date"] = pd.to_datetime(leads_data["Lead_Date"])

sales_data["year_month"] = sales_data["Booking_Date"].dt.to_period("M").dt.to_timestamp()
leads_data["year_month"] = leads_data["Lead_Date"].dt.to_period("M").dt.to_timestamp()

sales_data["Finance_Used_Numeric"] = (sales_data["Finance_Used"] == "Yes").astype(int)
sales_data["Exchange_Used_Numeric"] = (sales_data["Exchange_Used"] == "Yes").astype(int)

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

leads_data["Finance_Intent_Numeric"] = (leads_data["Finance_Intent"] == "Yes").astype(int)
leads_data["Exchange_Intent_Numeric"] = (leads_data["Exchange_Intent"] == "Yes").astype(int)

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

final_df = pd.merge(sales_monthly, leads_monthly, on=["Model", "year_month"], how="left")
final_df[["Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate", "Avg_Followup_Count"]] = \
    final_df[["Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate", "Avg_Followup_Count"]].fillna(0)

final_df["year"] = final_df["year_month"].dt.year
final_df["month"] = final_df["year_month"].dt.month
final_df["quarter"] = final_df["year_month"].dt.quarter

final_df = final_df.sort_values(["Model", "year_month"])

for lag in [1, 3, 6]:
    final_df[f"lag_{lag}"] = final_df.groupby("Model")["Units_Sold"].shift(lag)

final_df["rolling_mean_3"] = final_df.groupby("Model")["Units_Sold"].shift(1).rolling(3).mean()
final_df["rolling_mean_6"] = final_df.groupby("Model")["Units_Sold"].shift(1).rolling(6).mean()
final_df = final_df.fillna(0)

print(f"✅ Data processed: {len(final_df)} monthly records")

# Generate FUTURE predictions
print("\n3️⃣ Generating FUTURE sales forecasts (12 months ahead)...")

future_predictions = []
latest_data = final_df.sort_values("year_month").groupby("Model").tail(6)

for model_name in sorted(latest_data["Model"].unique()):
    model_data = latest_data[latest_data["Model"] == model_name].sort_values("year_month")
    
    if len(model_data) < 3:
        continue
    
    latest_month = model_data["year_month"].max()
    latest_record = model_data.iloc[-1]
    last_six = model_data["Units_Sold"].tail(6).values
    
    current_month = latest_month
    prev_units = list(last_six)
    
    for i in range(12):  # 12 months forecast
        current_month = current_month + pd.DateOffset(months=1)
        
        future_record = {
            "Model": model_name,
            "year_month": current_month,
            "year": current_month.year,
            "month": current_month.month,
            "quarter": (current_month.month - 1) // 3 + 1,
            "Avg_Ex_Showroom_Price": latest_record["Avg_Ex_Showroom_Price"],
            "Avg_Discount": latest_record["Avg_Discount"],
            "Finance_Rate": latest_record["Finance_Rate"],
            "Exchange_Rate": latest_record["Exchange_Rate"],
            "Lead_Count": latest_record["Lead_Count"],
            "Finance_Intent_Rate": latest_record["Finance_Intent_Rate"],
            "Exchange_Intent_Rate": latest_record["Exchange_Intent_Rate"],
            "Avg_Followup_Count": latest_record["Avg_Followup_Count"],
            "lag_1": prev_units[-1] if len(prev_units) >= 1 else latest_record["Units_Sold"],
            "lag_3": prev_units[-3] if len(prev_units) >= 3 else latest_record["Units_Sold"],
            "lag_6": prev_units[-6] if len(prev_units) >= 6 else latest_record["Units_Sold"],
            "rolling_mean_3": np.mean(prev_units[-3:]) if len(prev_units) >= 3 else latest_record["Units_Sold"],
            "rolling_mean_6": np.mean(prev_units[-6:]) if len(prev_units) >= 6 else latest_record["Units_Sold"],
        }
        
        future_df = pd.DataFrame([future_record])
        future_df["Model_encoded"] = le.transform([model_name])
        
        feature_columns = [
            "Model_encoded", "Avg_Ex_Showroom_Price", "Avg_Discount", "Finance_Rate",
            "Exchange_Rate", "Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate",
            "Avg_Followup_Count", "year", "month", "quarter", "lag_1", "lag_3", 
            "lag_6", "rolling_mean_3", "rolling_mean_6"
        ]
        
        X_future = future_df[feature_columns].fillna(0)
        pred = model.predict(X_future)[0]
        pred_units = int(np.maximum(pred, 0))
        
        future_record["Predicted_Units"] = pred_units
        future_predictions.append(future_record)
        
        prev_units.append(pred_units)
        if len(prev_units) > 6:
            prev_units.pop(0)

future_df_result = pd.DataFrame(future_predictions)
print(f"✅ {len(future_df_result)} future predictions generated!")

# Display RESULTS
print("\n" + "="*80)
print("📊 FUTURE FORECASTS SUMMARY")
print("="*80)

print(f"\n⏰ Forecast Period:")
print(f"   From: {future_df_result['year_month'].min().strftime('%B %Y')}")
print(f"   To:   {future_df_result['year_month'].max().strftime('%B %Y')}")
print(f"   Duration: 12 months")

print(f"\n📈 Total Future Forecast:")
print(f"   Total Units (12 months): {future_df_result['Predicted_Units'].sum()}")
print(f"   Average per Month: {future_df_result['Predicted_Units'].mean():.1f} units")
print(f"   Min Month Forecast: {future_df_result['Predicted_Units'].min()} units")
print(f"   Max Month Forecast: {future_df_result['Predicted_Units'].max()} units")

print(f"\n🚗 Future Forecasts by Model:")
model_forecast = future_df_result.groupby("Model")["Predicted_Units"].agg(["sum", "mean"]).round(0)
model_forecast.columns = ["Total (12 months)", "Avg/Month"]
print(model_forecast.to_string())

print(f"\n📅 Monthly Forecast Timeline:")
print(f"\n{'Month':<15} {'Baleno':<12} {'City':<12} {'Creta':<12} {'Nexon':<12} {'Swift':<12} {'Venue':<12} {'TOTAL':<10}")
print("-" * 95)

monthly_pivot = future_df_result.pivot_table(
    index="year_month",
    columns="Model",
    values="Predicted_Units",
    aggfunc="sum"
).fillna(0).astype(int)

for month, row in monthly_pivot.iterrows():
    month_str = month.strftime("%b %Y")
    print(f"{month_str:<15}", end="")
    for model in ["Baleno", "City", "Creta", "Nexon", "Swift", "Venue"]:
        val = int(row.get(model, 0))
        print(f"{val:<12}", end="")
    total = int(row.sum())
    print(f"{total:<10}")

print("\n" + "="*80)
print("✅ FUTURE FORECAST GENERATION COMPLETE!")
print("="*80)

print("""
📊 How to Use in Streamlit App:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Go to "📤 Batch Predictions" tab
2. Upload your DMS Sales Data CSV
3. Upload your CRM Funnel Data CSV
4. Click "🚀 Generate Batch Predictions"
5. Click "🔮 Future Forecasts" tab in the results
6. Select number of months to forecast (1-24)
7. Click "🚀 Generate Future Forecasts"
8. View charts, tables, and download predictions!

✨ You now have FUTURE sales predictions with dates! ✨
""")

# Save for reference
future_df_result[["Model", "year_month", "Predicted_Units"]].to_csv(
    "future_forecasts_sample.csv", index=False
)
print("💾 Future forecasts saved to: future_forecasts_sample.csv")
