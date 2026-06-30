import streamlit as st
import pandas as pd
import joblib
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder
import io

# Change to parent directory for file paths
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(page_title="Sales Forecasting", layout="wide")

# --------------------------------
# LOAD MODEL & DATA
# --------------------------------
@st.cache_resource
def load_model():
    return joblib.load("lightgbm_sales_model.pkl")

@st.cache_data
def load_data():
    df = pd.read_csv("data/final_dataset.csv")
    df["year_month"] = pd.to_datetime(df["year_month"])
    df = df.sort_values("year_month").reset_index(drop=True)
    return df

@st.cache_data
def load_predictions():
    return pd.read_csv("future_predictions.csv")

@st.cache_data
def load_encoder():
    """Create LabelEncoder from historical data"""
    df = load_data()
    le = LabelEncoder()
    le.fit(df["Model"].unique())
    return le

model = load_model()
df = load_data()
predictions_df = load_predictions()
label_encoder = load_encoder()

# --------------------------------
# INITIALIZE SESSION STATE
# --------------------------------
if "predictions_df" not in st.session_state:
    st.session_state.predictions_df = None

# --------------------------------
# HELPER FUNCTIONS FOR BATCH PREDICTIONS
# --------------------------------
@st.cache_data
def build_dataset_from_csv(sales_data, leads_data):
    """Process uploaded CSV files similar to build_dataset.py"""
    try:
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
        
        return final_df
    
    except Exception as e:
        raise Exception(f"Error processing data: {str(e)}")

def make_batch_predictions(data_df, model_obj, encoder):
    """Make predictions on a dataframe"""
    try:
        # Create a copy to avoid modifying original
        df_pred = data_df.copy()
        
        # Encode Model column
        df_pred["Model_encoded"] = encoder.transform(df_pred["Model"])
        
        # Select features that model expects (same order as training)
        feature_columns = [
            "Model_encoded", "Avg_Ex_Showroom_Price", "Avg_Discount", "Finance_Rate",
            "Exchange_Rate", "Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate",
            "Avg_Followup_Count", "year", "month", "quarter", "lag_1", "lag_3", 
            "lag_6", "rolling_mean_3", "rolling_mean_6"
        ]
        
        X = df_pred[feature_columns].fillna(0)
        
        # Make predictions
        predictions = model_obj.predict(X)
        
        # Add predictions to dataframe
        df_pred["Predicted_Units"] = np.maximum(predictions, 0).astype(int)
        
        return df_pred
    
    except Exception as e:
        raise Exception(f"Error making predictions: {str(e)}")

def generate_future_predictions(processed_df, model_obj, encoder, months_ahead=12):
    """Generate future predictions for months ahead"""
    try:
        future_predictions = []
        
        # Get latest data per model
        latest_data = processed_df.sort_values("year_month").groupby("Model").tail(6)
        
        for model in latest_data["Model"].unique():
            model_data = latest_data[latest_data["Model"] == model].sort_values("year_month")
            
            if len(model_data) < 3:
                continue
            
            # Get latest month and values
            latest_month = model_data["year_month"].max()
            latest_record = model_data.iloc[-1]
            
            # Get last 6 months for lag calculation
            last_six = model_data["Units_Sold"].tail(6).values
            
            # Generate predictions for next N months
            current_month = latest_month
            prev_units = list(last_six)
            
            for i in range(months_ahead):
                # Move to next month
                current_month = current_month + pd.DateOffset(months=1)
                
                # Create prediction record
                future_record = {
                    "Model": model,
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
                
                # Make prediction
                future_df = pd.DataFrame([future_record])
                future_df["Model_encoded"] = encoder.transform([model])
                
                feature_columns = [
                    "Model_encoded", "Avg_Ex_Showroom_Price", "Avg_Discount", "Finance_Rate",
                    "Exchange_Rate", "Lead_Count", "Finance_Intent_Rate", "Exchange_Intent_Rate",
                    "Avg_Followup_Count", "year", "month", "quarter", "lag_1", "lag_3", 
                    "lag_6", "rolling_mean_3", "rolling_mean_6"
                ]
                
                X_future = future_df[feature_columns].fillna(0)
                pred = model_obj.predict(X_future)[0]
                pred_units = int(np.maximum(pred, 0))
                
                future_record["Predicted_Units"] = pred_units
                future_predictions.append(future_record)
                
                # Update for next iteration
                prev_units.append(pred_units)
                if len(prev_units) > 6:
                    prev_units.pop(0)
        
        return pd.DataFrame(future_predictions)
    
    except Exception as e:
        raise Exception(f"Error generating future predictions: {str(e)}")


st.title("Automobile Sales Forecasting")
st.markdown("**Model:** LightGBM | **Data:** DMS + CRM | **MAPE:** 20.39%")

# --------------------------------
# CREATE TABS
# --------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 View Forecasts", "📤 Batch Predictions", "📈 Historical Data", "📖 Help & Guide"])

# ================================
# TAB 1: FORECAST DISPLAY
# ================================
with tab1:

    # Get unique models
    models = sorted(df["Model"].unique())
    selected_model = st.selectbox("Select Car Model", models)

    # Filter forecasts for selected model
    model_forecast = predictions_df[predictions_df["model"] == selected_model].copy()
    model_forecast = model_forecast.sort_values("month")

    if not model_forecast.empty:
        # Display table
        st.write(f"**{selected_model} - Monthly Forecast**")
        st.dataframe(model_forecast[["month", "predicted_units"]], use_container_width=True)
        
        # Display chart
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(model_forecast["month"], model_forecast["predicted_units"], 
                marker="o", linewidth=2, markersize=8, color="#1f77b4")
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Predicted Units Sold", fontsize=12)
        ax.set_title(f"2026 Sales Forecast - {selected_model}", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Monthly Sales", f"{model_forecast['predicted_units'].mean():.0f} units")
        with col2:
            st.metric("Peak Month", model_forecast.loc[model_forecast['predicted_units'].idxmax(), 'month'])
        with col3:
            st.metric("Lowest Month", model_forecast.loc[model_forecast['predicted_units'].idxmin(), 'month'])
        with col4:
            st.metric("Total 2026 Forecast", f"{model_forecast['predicted_units'].sum():.0f} units")
    else:
        st.warning(f"No forecast data available for {selected_model}")

    # All Models Comparison
    st.subheader("All Models - 2026 Forecast Comparison")
    show_all = st.checkbox("Show All Forecasts Comparison", value=False)

    if show_all:
        all_forecasts = predictions_df.copy()
        
        # Create pivot table for easy comparison
        pivot_data = all_forecasts.pivot(index="month", columns="model", values="predicted_units")
        st.dataframe(pivot_data, use_container_width=True)
        
        # Comparison chart
        fig, ax = plt.subplots(figsize=(14, 6))
        for model in pivot_data.columns:
            ax.plot(pivot_data.index, pivot_data[model], marker="o", label=model, linewidth=2)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Predicted Units Sold", fontsize=12)
        ax.set_title("2026 Sales Forecast - All Models Comparison", fontsize=14, fontweight="bold")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

# ================================
# TAB 2: BATCH PREDICTIONS FROM CSV
# ================================
with tab2:
    st.subheader("📤 Upload Data for Batch Predictions")
    st.markdown("""
    Upload your **CRM Funnel Data** and **DMS Sales Data** CSV files to get predictions for all records.
    
    **Expected Columns:**
    - **Sales Data:** Invoice_ID, Model, Booking_Date, Ex_Showroom_Price, Discount, Finance_Used, Exchange_Used
    - **CRM Data:** Lead_ID, Preferred_Model, Lead_Date, Finance_Intent, Exchange_Intent, Followup_Count
    """)
    
    col_upload1, col_upload2 = st.columns(2)
    
    with col_upload1:
        st.markdown("**Step 1: Upload Sales Data (DMS)**")
        sales_file = st.file_uploader("Upload DMS Sales Data", type="csv", key="sales_data")
    
    with col_upload2:
        st.markdown("**Step 2: Upload Lead Data (CRM)**")
        leads_file = st.file_uploader("Upload CRM Funnel Data", type="csv", key="leads_data")
    
    # Process button
    if sales_file and leads_file:
        if st.button("🚀 Generate Batch Predictions", key="batch_predict_btn"):
            try:
                # Read uploaded files
                sales_df = pd.read_csv(sales_file)
                leads_df = pd.read_csv(leads_file)
                
                with st.spinner("Processing data and making predictions..."):
                    # Build dataset
                    processed_df = build_dataset_from_csv(sales_df, leads_df)
                    
                    # Make predictions
                    predictions = make_batch_predictions(processed_df, model, label_encoder)
                    
                    # Store in session state
                    st.session_state.batch_predictions = predictions
                    
                    st.success("✅ Predictions generated successfully!")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display results if available
    if "batch_predictions" in st.session_state:
        predictions_data = st.session_state.batch_predictions
        
        # Create tabs for different views
        tab_hist, tab_future = st.tabs(["📊 Data Analysis", "🔮 Future Forecasts"])
        
        # ===== TAB: DATA ANALYSIS =====
        with tab_hist:
            st.subheader("📊 Actual vs Predicted Analysis")
            st.markdown("""
            **This section shows:**
            - **Units_Sold**: Actual units from your uploaded data
            - **Predicted_Units**: What the model predicts for that time period
            - **Other columns**: Features extracted from your CRM and Sales data
            
            Compare actual vs predicted to see model accuracy on your historical data.
            """)
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records Processed", len(predictions_data))
            with col2:
                st.metric("Total Predicted Units", f"{predictions_data['Predicted_Units'].sum():.0f}")
            with col3:
                st.metric("Average per Record", f"{predictions_data['Predicted_Units'].mean():.0f}")
            with col4:
                st.metric("Prediction Range", f"{predictions_data['Predicted_Units'].min()}-{predictions_data['Predicted_Units'].max()}")
            
            # Display results table
            st.markdown("**Detailed Data Analysis Table (Actual vs Model Predictions):**")
            display_columns = ["Model", "year_month", "Units_Sold", "Avg_Ex_Showroom_Price", 
                              "Avg_Discount", "Lead_Count", "Finance_Intent_Rate", "Predicted_Units"]
            
            available_cols = [col for col in display_columns if col in predictions_data.columns]
            st.dataframe(predictions_data[available_cols], use_container_width=True, height=400)
            
            # Download results as CSV
            csv_buffer = io.StringIO()
            predictions_data[available_cols].to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📥 Download Data Analysis as CSV",
                data=csv_data,
                file_name="batch_predictions.csv",
                mime="text/csv"
            )
            
            # Visualization by Model
            st.subheader("📈 Analysis by Model (Actual Sales vs Predicted)")
            model_summary = predictions_data.groupby("Model")["Predicted_Units"].agg(
                ["sum", "mean", "count"]
            ).round(0).rename(columns={"sum": "Total Units", "mean": "Avg Units", "count": "Records"})
            
            st.dataframe(model_summary, use_container_width=True)
            
            # Chart
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            # Bar chart by model
            model_totals = predictions_data.groupby("Model")["Predicted_Units"].sum().sort_values(ascending=False)
            axes[0].bar(range(len(model_totals)), model_totals.values, color="#1f77b4")
            axes[0].set_xticks(range(len(model_totals)))
            axes[0].set_xticklabels(model_totals.index, rotation=45, ha="right")
            axes[0].set_ylabel("Total Predicted Units", fontsize=11)
            axes[0].set_title("Model Predictions vs Actual Sales by Car Model", fontsize=12, fontweight="bold")
            axes[0].grid(axis="y", alpha=0.3)
            
            # Distribution chart
            axes[1].hist(predictions_data["Predicted_Units"], bins=20, color="#ff7f0e", alpha=0.7, edgecolor="black")
            axes[1].set_xlabel("Predicted Units", fontsize=11)
            axes[1].set_ylabel("Frequency", fontsize=11)
            axes[1].set_title("Distribution of Model Predictions", fontsize=12, fontweight="bold")
            axes[1].grid(axis="y", alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # ===== TAB: FUTURE FORECASTS =====
        with tab_future:
            st.subheader("🔮 Future Sales Forecasts")
            st.markdown("""
            Generate forward-looking predictions for upcoming months based on your uploaded data.
            The model uses the latest trends and patterns to forecast future sales.
            """)
            
            col_months, col_action = st.columns([1, 2])
            
            with col_months:
                months_ahead = st.slider("Forecast Months Ahead", min_value=1, max_value=24, value=12, step=1)
            
            with col_action:
                st.write("")  # Spacer
                if st.button("🚀 Generate Future Forecasts", key="future_predict_btn"):
                    try:
                        with st.spinner(f"Generating {months_ahead}-month forecast..."):
                            # Generate future predictions
                            future_preds = generate_future_predictions(
                                predictions_data, model, label_encoder, months_ahead
                            )
                            
                            # Store in session state
                            st.session_state.future_predictions = future_preds
                            st.success(f"✅ {months_ahead}-month forecast generated!")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            # Display future forecasts if available
            if "future_predictions" in st.session_state:
                future_data = st.session_state.future_predictions
                
                if not future_data.empty:
                    # Summary metrics
                    st.subheader("📈 Forecast Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Months Forecasted", len(future_data) // len(future_data["Model"].unique()))
                    with col2:
                        st.metric("Total Forecasted Units", f"{future_data['Predicted_Units'].sum():.0f}")
                    with col3:
                        st.metric("Average Units/Month", f"{future_data['Predicted_Units'].mean():.0f}")
                    with col4:
                        st.metric("Forecast Period", f"{future_data['year_month'].min().strftime('%b %Y')} - {future_data['year_month'].max().strftime('%b %Y')}")
                    
                    # Display table
                    st.markdown("**Future Sales Forecast Table:**")
                    future_display = future_data[["Model", "year_month", "Predicted_Units"]].copy()
                    future_display["year_month"] = future_display["year_month"].dt.strftime("%B %Y")
                    future_display = future_display.rename(columns={"year_month": "Month", "Predicted_Units": "Forecasted Units"})
                    
                    st.dataframe(future_display, use_container_width=True, height=400)
                    
                    # Download future forecasts
                    csv_buffer_future = io.StringIO()
                    future_display.to_csv(csv_buffer_future, index=False)
                    csv_future_data = csv_buffer_future.getvalue()
                    
                    st.download_button(
                        label="📥 Download Future Forecasts as CSV",
                        data=csv_future_data,
                        file_name="future_forecasts.csv",
                        mime="text/csv"
                    )
                    
                    # Forecast by model
                    st.subheader("🚗 Forecast by Model")
                    future_by_model = future_data.groupby("Model")["Predicted_Units"].agg(
                        ["sum", "mean"]
                    ).round(0).rename(columns={"sum": "Total Forecasted", "mean": "Avg per Month"})
                    
                    st.dataframe(future_by_model, use_container_width=True)
                    
                    # Visualization
                    st.subheader("📊 Forecast Charts")
                    
                    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
                    
                    # Line chart - All models
                    for model_name in future_data["Model"].unique():
                        model_forecast = future_data[future_data["Model"] == model_name].sort_values("year_month")
                        axes[0].plot(model_forecast["year_month"], model_forecast["Predicted_Units"], 
                                    marker="o", label=model_name, linewidth=2)
                    
                    axes[0].set_xlabel("Month", fontsize=11)
                    axes[0].set_ylabel("Forecasted Units", fontsize=11)
                    axes[0].set_title("Future Sales Forecast - All Models", fontsize=12, fontweight="bold")
                    axes[0].legend(loc="best")
                    axes[0].grid(True, alpha=0.3)
                    plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha="right")
                    
                    # Bar chart - Total by model
                    future_totals = future_data.groupby("Model")["Predicted_Units"].sum().sort_values(ascending=False)
                    axes[1].bar(range(len(future_totals)), future_totals.values, color="#2ca02c")
                    axes[1].set_xticks(range(len(future_totals)))
                    axes[1].set_xticklabels(future_totals.index, rotation=45, ha="right")
                    axes[1].set_ylabel("Total Forecasted Units", fontsize=11)
                    axes[1].set_title("Total Forecast by Model", fontsize=12, fontweight="bold")
                    axes[1].grid(axis="y", alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Detailed table by month
                    st.subheader("📅 Detailed Month-by-Month Forecast")
                    future_pivot = future_data.pivot_table(
                        index="year_month", 
                        columns="Model", 
                        values="Predicted_Units", 
                        aggfunc="sum"
                    ).fillna(0).astype(int)
                    
                    future_pivot.index = future_pivot.index.strftime("%B %Y")
                    st.dataframe(future_pivot, use_container_width=True)
                
                else:
                    st.warning("No future forecast data generated. Please check your input data.")
            else:
                st.info("👆 Click 'Generate Future Forecasts' to create predictions for upcoming months")
    else:
        st.info("👆 Upload both files above and click 'Generate Batch Predictions' to see results")


# ================================
# TAB 3: HISTORICAL DATA
# ================================
with tab3:
    st.subheader("📈 Historical Sales Data")
    
    models = sorted(df["Model"].unique())
    col1, col2 = st.columns([1, 1])
    
    with col1:
        history_model = st.selectbox("Select Model to View History", models)
    
    with col2:
        show_detailed = st.checkbox("Show Detailed Data", value=False)
    
    history_data = df[df["Model"] == history_model].sort_values("year_month")[
        ["year_month", "Units_Sold", "Avg_Ex_Showroom_Price", "Avg_Discount", "Finance_Rate", "Exchange_Rate", "Lead_Count"]
    ]
    
    if not history_data.empty:
        if show_detailed:
            st.dataframe(history_data, use_container_width=True)
        
        # Historical chart
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(history_data["year_month"], history_data["Units_Sold"], 
                marker="o", linewidth=2, markersize=6, color="#ff7f0e", label="Actual Sales")
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Units Sold", fontsize=12)
        ax.set_title(f"Historical Sales - {history_model}", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Sales", f"{history_data['Units_Sold'].mean():.0f} units")
        with col2:
            st.metric("Peak Sales", f"{history_data['Units_Sold'].max():.0f} units")
        with col3:
            st.metric("Min Sales", f"{history_data['Units_Sold'].min():.0f} units")
        with col4:
            st.metric("Total Records", len(history_data))
    else:
        st.warning(f"No historical data for {history_model}")


# ================================
# TAB 4: HELP & GUIDE
# ================================
with tab4:
    st.subheader("📖 Help & Guide")
    
    st.markdown("""
    ## How to Use This Application
    
    ### Tab 1: View Forecasts
    - View pre-computed 2026 sales forecasts for each model
    - Select a specific model to see monthly predictions
    - View all models comparison to identify trends
    
    ### Tab 2: Batch Predictions (NEW!)
    Upload your own data files to get predictions:
    
    **Step 1:** Prepare your data files
    - **Sales Data CSV** should have columns: Invoice_ID, Model, Booking_Date, Ex_Showroom_Price, Discount, Finance_Used, Exchange_Used
    - **CRM Data CSV** should have columns: Lead_ID, Preferred_Model, Lead_Date, Finance_Intent, Exchange_Intent, Followup_Count
    
    **Step 2:** Upload both files
    - Click "Upload DMS Sales Data" and select your sales file
    - Click "Upload CRM Funnel Data" and select your lead file
    
    **Step 3:** Generate Predictions
    - Click "Generate Batch Predictions" button
    - Wait for processing (usually < 10 seconds)
    - View results and download as CSV
    
    ### Tab 3: Historical Data
    - Explore historical sales trends for each model
    - Analyze past performance and patterns
    
    ### Model Information
    - **Algorithm:** LightGBM (500 decision trees)
    - **Accuracy:** MAPE 20.39%
    - **Features:** 16 engineered features (price, discount, finance rate, lead count, temporal features, etc.)
    - **Prediction Speed:** < 1 second per batch
    
    ### Example Data Format
    
    **DMS_Sales_Data_Sample.csv:**
    | Invoice_ID | Model | Booking_Date | Ex_Showroom_Price | Discount | Finance_Used | Exchange_Used |
    |---|---|---|---|---|---|---|
    | INV001 | Baleno | 2026-01-01 | 1500000 | 0.05 | Yes | No |
    | INV002 | Creta | 2026-01-02 | 1800000 | 0.03 | Yes | Yes |
    
    **CRM_Funnel_Data_Sample.csv:**
    | Lead_ID | Preferred_Model | Lead_Date | Finance_Intent | Exchange_Intent | Followup_Count |
    |---|---|---|---|---|---|
    | LEAD001 | Baleno | 2025-12-01 | Yes | No | 3 |
    | LEAD002 | Creta | 2025-12-02 | Yes | Yes | 5 |
    
    ### Tips for Best Results
    1. Ensure dates are in YYYY-MM-DD format
    2. Use consistent model names (e.g., "Baleno", not "baleno" or "BALENO")
    3. Finance_Used and Finance_Intent should be "Yes" or "No"
    4. Lead_Count must have at least one month of lag data for best accuracy
    
    ### Troubleshooting
    - **"Error processing data"**: Check your CSV column names and formats
    - **Missing predictions**: Some models might not have enough historical training data
    - **Unexpected predictions**: Verify your input data matches the expected format
    
    ### Questions?
    Review the MODEL_EXPLANATION.html or MODEL_EXPLANATION.pdf files for detailed technical information about how the model works.
    """)
    
    st.markdown("---")
    st.markdown("**Version:** 2.0 | **Last Updated:** June 9, 2026 | **Status:** Production Ready ✅")