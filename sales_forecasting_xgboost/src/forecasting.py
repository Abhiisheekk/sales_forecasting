import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder

# Load trained model
model = joblib.load("lightgbm_sales_model.pkl")

# Load final dataset and create encoder
df = pd.read_csv("data/final_dataset.csv")
df["year_month"] = pd.to_datetime(df["year_month"])

# Create and fit encoder with models from data
le = LabelEncoder()
le.fit(df["Model"].unique())

def get_last_known_row(df, model_name):
    model_df = df[df["Model"] == model_name].sort_values("year_month")
    
    if model_df.empty:
        raise ValueError("Model not found in data")

    return model_df.iloc[-1]

def forecast_sales(model_name, months_ahead=1):
    history_row = get_last_known_row(df, model_name)

    forecasts = []

    lag_1 = history_row["lag_1"]
    lag_3 = history_row["lag_3"]
    lag_6 = history_row["lag_6"]
    rm3 = history_row["rolling_mean_3"]
    rm6 = history_row["rolling_mean_6"]

    avg_price = history_row["Avg_Ex_Showroom_Price"]
    avg_discount = history_row["Avg_Discount"]
    finance_rate = history_row["Finance_Rate"]
    exchange_rate = history_row["Exchange_Rate"]

    lead_count = history_row["Lead_Count"]
    finance_intent = history_row["Finance_Intent_Rate"]
    exchange_intent = history_row["Exchange_Intent_Rate"]
    followup = history_row["Avg_Followup_Count"]

    model_encoded = le.transform([model_name])[0]

    last_date = history_row["year_month"]

    for step in range(months_ahead):
        next_date = last_date + pd.DateOffset(months=1)

        X_future = pd.DataFrame([{
            "Model": model_encoded,
            "Avg_Ex_Showroom_Price": avg_price,
            "Avg_Discount": avg_discount,
            "Finance_Rate": finance_rate,
            "Exchange_Rate": exchange_rate,
            "Lead_Count": lead_count,
            "Finance_Intent_Rate": finance_intent,
            "Exchange_Intent_Rate": exchange_intent,
            "Avg_Followup_Count": followup,
            "year": next_date.year,
            "month": next_date.month,
            "quarter": next_date.quarter,
            "lag_1": lag_1,
            "lag_3": lag_3,
            "lag_6": lag_6,
            "rolling_mean_3": rm3,
            "rolling_mean_6": rm6
        }])

        pred = model.predict(X_future)[0]
        pred = max(0, round(pred))  # sales can't be negative

        forecasts.append({
            "month": next_date.strftime("%Y-%m"),
            "predicted_units": pred
        })

        # Update lags
        lag_6 = lag_3
        lag_3 = lag_1
        lag_1 = pred

        rm3 = (rm3 * 2 + pred) / 3
        rm6 = (rm6 * 5 + pred) / 6

        last_date = next_date

    return forecasts

if __name__ == "__main__":
    # Get unique models from data
    models = df["Model"].unique()
    
    all_forecasts = []
    
    # Generate 12-month forecasts for all models
    for model_name in models:
        forecasts = forecast_sales(model_name, months_ahead=12)
        for forecast in forecasts:
            forecast["model"] = model_name
            all_forecasts.append(forecast)
    
    # Save to CSV
    predictions_df = pd.DataFrame(all_forecasts)
    predictions_df = predictions_df[["model", "month", "predicted_units"]]
    predictions_df.to_csv("future_predictions.csv", index=False)
    
    print("Next year forecasts for all models saved to future_predictions.csv")
    print(predictions_df.head(15))