import pandas as pd


def build_dataset():
    # Load raw data
    sales_df = pd.read_csv("data/DMS_Sales_Data_Sample.csv")
    leads_df = pd.read_csv("data/CRM_Funnel_Data_Sample - Copy.csv")

    # Convert dates
    sales_df["Booking_Date"] = pd.to_datetime(sales_df["Booking_Date"])
    leads_df["Lead_Date"] = pd.to_datetime(leads_df["Lead_Date"])

    # Create Year-Month
    sales_df["year_month"] = sales_df["Booking_Date"].dt.to_period("M")
    leads_df["year_month"] = leads_df["Lead_Date"].dt.to_period("M")

    # Convert Yes/No to 1/0 for Finance and Exchange
    sales_df["Finance_Used_Numeric"] = (sales_df["Finance_Used"] == "Yes").astype(int)
    sales_df["Exchange_Used_Numeric"] = (sales_df["Exchange_Used"] == "Yes").astype(int)

    # Aggregate SALES data
    sales_monthly = (
        sales_df
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

    # Convert Finance and Exchange Intent to numeric (Yes=1, No=0)
    leads_df["Finance_Intent_Numeric"] = (leads_df["Finance_Intent"] == "Yes").astype(int)
    leads_df["Exchange_Intent_Numeric"] = (leads_df["Exchange_Intent"] == "Yes").astype(int)

    # Aggregate LEAD data
    leads_monthly = (
        leads_df
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

    # Drop rows with missing lags
    final_df = final_df.dropna().reset_index(drop=True)

    # Save final dataset
    final_df.to_csv("data/final_dataset.csv", index=False)

    print("✅ Final dataset created:", final_df.shape)


if __name__ == "__main__":
    build_dataset()