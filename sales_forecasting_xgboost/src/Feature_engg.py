import pandas as pd
import numpy as np

def engineer_features(input_path, output_path):
    df = pd.read_csv(input_path)
    df["year_month"] = pd.to_datetime(df["year_month"])

    # ---------- Model-wise normalization ----------
    model_avg = df.groupby("Model")["Units_Sold"].transform("mean")
    df["sales_vs_model_avg"] = df["Units_Sold"] / model_avg

    # ---------- Momentum features ----------
    df["mom_1_3"] = df["lag_1"] / (df["lag_3"] + 1)
    df["mom_3_6"] = df["lag_3"] / (df["lag_6"] + 1)

    # ---------- Trend features ----------
    df["trend_3"] = df["lag_1"] - df["lag_3"]
    df["trend_6"] = df["lag_1"] - df["lag_6"]

    # ---------- Interaction features ----------
    df["discount_pressure"] = df["Avg_Discount"] * df["Finance_Rate"]
    df["lead_strength"] = df["Lead_Count"] * (
        df["Finance_Intent_Rate"] + df["Exchange_Intent_Rate"]
    )

    # ---------- Seasonality encoding ----------
    df["month"] = df["year_month"].dt.month
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df.drop(columns=["month"], inplace=True)

    df.to_csv(output_path, index=False)
    print(f"✅ Feature engineered dataset saved to: {output_path}")


if __name__ == "__main__":
    engineer_features(
        input_path="data/final_dataset.csv",
        output_path="data/final_dataset_fe.csv"
    )
