import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Sales Forecasting System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 12px;
        border-radius: 5px;
        color: #155724;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 12px;
        border-radius: 5px;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# LOAD MODEL & DATA
# ================================
@st.cache_resource
def load_model():
    try:
        # Try multiple path options
        paths_to_try = [
            "lightgbm_sales_model.pkl",
            os.path.join(os.path.dirname(__file__), "lightgbm_sales_model.pkl"),
            os.path.join(os.path.dirname(__file__), "../lightgbm_sales_model.pkl"),
        ]
        for model_path in paths_to_try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
        # If none found, try default
        return joblib.load("lightgbm_sales_model.pkl")
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        st.info("Make sure lightgbm_sales_model.pkl exists in the project directory")
        st.stop()

@st.cache_data
def load_data():
    try:
        paths_to_try = [
            "data/final_dataset.csv",
            os.path.join(os.path.dirname(__file__), "data/final_dataset.csv"),
            os.path.join(os.path.dirname(__file__), "../data/final_dataset.csv"),
        ]
        for data_path in paths_to_try:
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
                df["year_month"] = pd.to_datetime(df["year_month"])
                df = df.sort_values("year_month").reset_index(drop=True)
                return df
        # If none found, try default
        df = pd.read_csv("data/final_dataset.csv")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()
    
    df["year_month"] = pd.to_datetime(df["year_month"])
    df = df.sort_values("year_month").reset_index(drop=True)
    return df

@st.cache_data
def load_encoder_data():
    """Load unique models to create encoder"""
    try:
        paths_to_try = [
            "data/final_dataset.csv",
            os.path.join(os.path.dirname(__file__), "data/final_dataset.csv"),
            os.path.join(os.path.dirname(__file__), "../data/final_dataset.csv"),
        ]
        for data_path in paths_to_try:
            if os.path.exists(data_path):
                df = pd.read_csv(data_path)
                le = LabelEncoder()
                le.fit(df["Model"].unique())
                return le, df["Model"].unique()
        # If none found, try default
        df = pd.read_csv("data/final_dataset.csv")
    except Exception as e:
        st.error(f"Error loading encoder data: {str(e)}")
        st.stop()
    
    le = LabelEncoder()
    le.fit(df["Model"].unique())
    return le, df["Model"].unique()

# Load resources
try:
    model = load_model()
    df = load_data()
    le, unique_models = load_encoder_data()
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# ================================
# HEADER
# ================================
st.title("🚗 Automobile Sales Forecasting System")
st.markdown("---")

# ================================
# SIDEBAR - MODEL INFO
# ================================
with st.sidebar:
    st.header("📊 Model Information")
    st.info("""
    **Model Details:**
    - Algorithm: LightGBM Regressor
    - Input Features: 16
    - Training Data: DMS + CRM Sales Data
    - Performance: MAPE ≈ 20.39%
    - Update: 2026
    """)
    
    st.markdown("---")
    st.header("📈 Data Statistics")
    st.metric("Total Records", f"{len(df):,}")
    st.metric("Car Models", f"{df['Model'].nunique()}")
    st.metric("Date Range", f"{df['year_month'].min().strftime('%Y-%m')} to {df['year_month'].max().strftime('%Y-%m')}")

# ================================
# TABS
# ================================
tab1, tab2, tab3 = st.tabs(["🔮 Make Prediction", "📊 View Forecasts", "📖 Help & Guide"])

# ================================
# TAB 1: MAKE PREDICTIONS
# ================================
with tab1:
    st.header("Make a Sales Prediction")
    st.markdown("Enter the details below to predict sales for a specific car model.")
    
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚗 Vehicle & Market Info")
        
        # Model selection
        selected_model = st.selectbox(
            "Car Model",
            options=sorted(unique_models),
            help="Select the automobile model for prediction"
        )
        
        # Price
        avg_price = st.number_input(
            "Avg Ex-Showroom Price (₹)",
            min_value=0.0,
            value=1500000.0,
            step=100000.0,
            help="Average ex-showroom price of the vehicle in rupees"
        )
        
        # Discount
        avg_discount = st.number_input(
            "Avg Discount (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            step=0.1,
            help="Average discount percentage offered"
        )
        
        # Finance Rate
        finance_rate = st.number_input(
            "Finance Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=8.5,
            step=0.1,
            help="Interest rate for vehicle financing"
        )
        
        # Exchange Rate
        exchange_rate = st.number_input(
            "Exchange Rate (INR/USD)",
            min_value=0.0,
            value=83.5,
            step=0.1,
            help="Currency exchange rate"
        )
    
    with col2:
        st.subheader("👥 Sales & Lead Info")
        
        # Lead Count
        lead_count = st.number_input(
            "Lead Count",
            min_value=0,
            value=500,
            step=10,
            help="Number of sales leads generated"
        )
        
        # Finance Intent Rate
        finance_intent = st.number_input(
            "Finance Intent Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=65.0,
            step=1.0,
            help="Percentage of leads interested in financing"
        )
        
        # Exchange Intent Rate
        exchange_intent = st.number_input(
            "Exchange Intent Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=45.0,
            step=1.0,
            help="Percentage of leads interested in exchange offers"
        )
        
        # Followup Count
        followup_count = st.number_input(
            "Avg Followup Count",
            min_value=0,
            max_value=20,
            value=5,
            step=1,
            help="Average number of follow-ups per lead"
        )
    
    # Temporal features
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        prediction_year = st.number_input(
            "Prediction Year",
            min_value=2024,
            max_value=2030,
            value=2026,
            help="Year for which to make prediction"
        )
    
    with col4:
        prediction_month = st.number_input(
            "Prediction Month",
            min_value=1,
            max_value=12,
            value=datetime.now().month,
            help="Month for which to make prediction"
        )
    
    with col5:
        # Auto-calculate quarter
        quarter = (prediction_month - 1) // 3 + 1
        st.metric("Quarter", f"Q{quarter}")
    
    with col6:
        # Get historical data for lags
        model_historical = df[df["Model"] == selected_model].sort_values("year_month")
        if not model_historical.empty:
            lag_1_val = model_historical["lag_1"].iloc[-1] if "lag_1" in model_historical.columns else 100
            st.metric("Last Sales (lag_1)", f"{int(lag_1_val)} units")
        else:
            lag_1_val = 100
    
    # Prepare prediction
    if st.button("🎯 Generate Prediction", use_container_width=True, type="primary"):
        try:
            # Get historical data for the model
            model_data = df[df["Model"] == selected_model].sort_values("year_month")
            
            if model_data.empty:
                st.error(f"❌ No historical data found for model: {selected_model}")
            else:
                # Get last known values for lag and rolling features
                last_row = model_data.iloc[-1]
                
                lag_1 = last_row.get("lag_1", 100)
                lag_3 = last_row.get("lag_3", 100)
                lag_6 = last_row.get("lag_6", 100)
                rm_3 = last_row.get("rolling_mean_3", 100)
                rm_6 = last_row.get("rolling_mean_6", 100)
                
                # Encode model
                model_encoded = le.transform([selected_model])[0]
                
                # Create input dataframe
                X_future = pd.DataFrame([{
                    "Model": model_encoded,
                    "Avg_Ex_Showroom_Price": avg_price,
                    "Avg_Discount": avg_discount,
                    "Finance_Rate": finance_rate,
                    "Exchange_Rate": exchange_rate,
                    "Lead_Count": lead_count,
                    "Finance_Intent_Rate": finance_intent,
                    "Exchange_Intent_Rate": exchange_intent,
                    "Avg_Followup_Count": followup_count,
                    "year": prediction_year,
                    "month": prediction_month,
                    "quarter": quarter,
                    "lag_1": lag_1,
                    "lag_3": lag_3,
                    "lag_6": lag_6,
                    "rolling_mean_3": rm_3,
                    "rolling_mean_6": rm_6
                }])
                
                # Make prediction
                prediction = model.predict(X_future)[0]
                prediction = max(0, round(prediction))
                
                # Display result
                st.markdown("---")
                st.success(f"✅ Prediction Complete!")
                
                # Display results in columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "📊 Predicted Sales",
                        f"{int(prediction)} units",
                        delta=f"{int(prediction - lag_1):+d} vs last month",
                        delta_color="normal"
                    )
                
                with col2:
                    st.metric(
                        "🎯 Car Model",
                        selected_model
                    )
                
                with col3:
                    st.metric(
                        "📅 Month",
                        f"{prediction_month}/{prediction_year}"
                    )
                
                with col4:
                    historical_avg = model_data["Units_Sold"].mean() if "Units_Sold" in model_data.columns else prediction
                    st.metric(
                        "📈 vs Historical Avg",
                        f"{(prediction/historical_avg*100):.1f}%"
                    )
                
                # Additional analysis
                st.markdown("---")
                st.subheader("📈 Detailed Analysis")
                
                analysis_col1, analysis_col2 = st.columns(2)
                
                with analysis_col1:
                    st.write("**Input Parameters:**")
                    input_summary = pd.DataFrame({
                        "Parameter": [
                            "Price (₹)",
                            "Discount (%)",
                            "Finance Rate (%)",
                            "Exchange Rate",
                            "Lead Count",
                            "Finance Intent (%)",
                            "Exchange Intent (%)",
                            "Followup Count"
                        ],
                        "Value": [
                            f"{avg_price:,.0f}",
                            f"{avg_discount:.1f}",
                            f"{finance_rate:.1f}",
                            f"{exchange_rate:.2f}",
                            f"{lead_count}",
                            f"{finance_intent:.1f}",
                            f"{exchange_intent:.1f}",
                            f"{followup_count}"
                        ]
                    })
                    st.dataframe(input_summary, use_container_width=True, hide_index=True)
                
                with analysis_col2:
                    st.write("**Model Insights:**")
                    insights = pd.DataFrame({
                        "Metric": [
                            "Historical Average",
                            "Max Historical",
                            "Min Historical",
                            "Current Trend"
                        ],
                        "Value": [
                            f"{int(model_data['Units_Sold'].mean())} units" if "Units_Sold" in model_data.columns else "N/A",
                            f"{int(model_data['Units_Sold'].max())} units" if "Units_Sold" in model_data.columns else "N/A",
                            f"{int(model_data['Units_Sold'].min())} units" if "Units_Sold" in model_data.columns else "N/A",
                            "Stable" if abs(prediction - lag_1) < lag_1 * 0.1 else ("Upward" if prediction > lag_1 else "Downward")
                        ]
                    })
                    st.dataframe(insights, use_container_width=True, hide_index=True)
                
                # Visualization
                if "Units_Sold" in model_data.columns:
                    st.markdown("---")
                    st.subheader("📊 Historical Sales vs Prediction")
                    
                    fig, ax = plt.subplots(figsize=(12, 5))
                    
                    # Plot historical data
                    ax.plot(
                        model_data["year_month"].tail(24),
                        model_data["Units_Sold"].tail(24),
                        marker="o",
                        linewidth=2,
                        markersize=6,
                        label="Historical Sales",
                        color="#1f77b4"
                    )
                    
                    # Add prediction point
                    pred_date = pd.Timestamp(year=prediction_year, month=prediction_month, day=1)
                    ax.scatter([pred_date], [prediction], color="#ff7f0e", s=200, marker="*", 
                              label="Predicted Sales", zorder=5, edgecolors="black", linewidth=2)
                    
                    ax.set_xlabel("Date", fontsize=11)
                    ax.set_ylabel("Units Sold", fontsize=11)
                    ax.set_title(f"{selected_model} - Historical Sales & Prediction", 
                                fontsize=13, fontweight="bold")
                    ax.legend(loc="upper left", fontsize=10)
                    ax.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
        
        except Exception as e:
            st.error(f"❌ Error making prediction: {str(e)}")
            st.info("Please check your inputs and try again.")

# ================================
# TAB 2: VIEW FORECASTS
# ================================
with tab2:
    st.header("📊 Pre-computed Forecasts")
    st.markdown("View 12-month sales forecasts for each car model.")
    
    try:
        # Try to load pre-computed predictions
        paths_to_try = [
            "future_predictions.csv",
            os.path.join(os.path.dirname(__file__), "future_predictions.csv"),
            os.path.join(os.path.dirname(__file__), "../future_predictions.csv"),
        ]
        predictions_df = None
        for pred_path in paths_to_try:
            if os.path.exists(pred_path):
                predictions_df = pd.read_csv(pred_path)
                break
        
        if predictions_df is None:
            st.info("📌 Pre-computed forecasts not available. Use the 'Make Prediction' tab to generate forecasts.")
            st.stop()
        
        # Get unique models from predictions
        models_list = sorted(predictions_df["model"].unique())
        selected_model_forecast = st.selectbox("Select Car Model", models_list, key="forecast_model")
        
        # Filter forecasts
        model_forecast = predictions_df[predictions_df["model"] == selected_model_forecast].copy()
        model_forecast = model_forecast.sort_values("month")
        
        if not model_forecast.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 Avg Monthly Sales",
                    f"{model_forecast['predicted_units'].mean():.0f} units"
                )
            
            with col2:
                peak_month = model_forecast.loc[model_forecast['predicted_units'].idxmax(), 'month']
                st.metric("📈 Peak Month", peak_month)
            
            with col3:
                low_month = model_forecast.loc[model_forecast['predicted_units'].idxmin(), 'month']
                st.metric("📉 Lowest Month", low_month)
            
            with col4:
                st.metric(
                    "📊 Total Forecast",
                    f"{model_forecast['predicted_units'].sum():.0f} units"
                )
            
            st.markdown("---")
            
            # Display table
            st.subheader(f"Monthly Forecast - {selected_model_forecast}")
            forecast_display = model_forecast[["month", "predicted_units"]].copy()
            forecast_display.columns = ["Month", "Predicted Units"]
            st.dataframe(forecast_display, use_container_width=True, hide_index=True)
            
            # Visualization
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(
                model_forecast["month"],
                model_forecast["predicted_units"],
                marker="o",
                linewidth=2.5,
                markersize=8,
                color="#1f77b4"
            )
            ax.fill_between(
                range(len(model_forecast)),
                model_forecast["predicted_units"],
                alpha=0.3,
                color="#1f77b4"
            )
            ax.set_xlabel("Month", fontsize=12)
            ax.set_ylabel("Predicted Units Sold", fontsize=12)
            ax.set_title(f"2026 Sales Forecast - {selected_model_forecast}", 
                        fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning(f"No forecast data available for {selected_model_forecast}")
    
    except FileNotFoundError:
        st.info("📌 Pre-computed forecasts not available. Use the 'Make Prediction' tab to generate forecasts.")

# ================================
# TAB 3: HELP & GUIDE
# ================================
with tab3:
    st.header("📖 Help & Guide")
    
    st.subheader("How to Use This System")
    st.write("""
    ### Step 1: Gather Your Data
    Collect the following information about your target market condition:
    - Car model name
    - Expected price point
    - Planned discount percentage
    - Current finance rates
    - Exchange rates (if applicable)
    - Expected number of leads
    - Anticipated customer interest rates
    - Expected follow-up frequency
    
    ### Step 2: Make a Prediction
    1. Go to the **"Make Prediction"** tab
    2. Select your car model
    3. Enter all the required parameters
    4. Click **"Generate Prediction"** button
    5. View your sales forecast!
    
    ### Step 3: Analyze Results
    - Compare against historical averages
    - Check the trend direction (upward/downward/stable)
    - Review detailed metrics and insights
    - Use for planning and decision-making
    """)
    
    st.markdown("---")
    
    st.subheader("Feature Descriptions")
    
    feature_info = {
        "Price (₹)": "Average ex-showroom price affects customer purchasing power",
        "Discount (%)": "Offering discounts can boost sales volume",
        "Finance Rate (%)": "Lower rates typically increase finance-backed purchases",
        "Exchange Rate": "Affects import costs and pricing strategy",
        "Lead Count": "Number of potential customers in pipeline",
        "Finance Intent (%)": "Percentage of customers interested in financing",
        "Exchange Intent (%)": "Percentage of customers interested in trade-ins",
        "Followup Count": "Number of follow-up interactions per lead"
    }
    
    for feature, description in feature_info.items():
        st.write(f"**{feature}:** {description}")
    
    st.markdown("---")
    
    st.subheader("Model Performance")
    st.info("""
    **Algorithm:** LightGBM (Light Gradient Boosting Machine)
    
    **Performance Metrics:**
    - MAPE (Mean Absolute Percentage Error): ~20.39%
    - Handles seasonal patterns
    - Captures market trends
    - Accounts for promotional activities
    
    **What This Means:**
    The model's predictions are typically within 20% of actual values,
    which is reliable for business planning and forecasting.
    """)
    
    st.markdown("---")
    
    st.subheader("Tips for Better Predictions")
    st.write("""
    1. **Use Recent Data:** Ensure your inputs reflect current market conditions
    2. **Cross-Check Assumptions:** Validate your parameter assumptions with your team
    3. **Monitor Trends:** Track actual vs predicted sales to improve future forecasts
    4. **Scenario Planning:** Try different parameters to see various outcomes
    5. **Regular Updates:** Retrain the model with latest sales data periodically
    """)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    <p>📊 Automobile Sales Forecasting System | Powered by LightGBM | 2026</p>
    </div>
""", unsafe_allow_html=True)
