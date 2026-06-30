# 🚗 Automobile Sales Forecasting using LightGBM & Streamlit

An end-to-end machine learning pipeline for forecasting automobile sales based on historical DMS and CRM data. The system combines sales transactions, lead information, and customer behavior to predict monthly sales for all car models.

---

## 📌 Project Overview

**Objective**: Predict monthly automobile sales units for 2026 using historical sales and lead data.

**Data Sources**:
- **DMS Sales Data**: Invoice records with pricing, discounts, financing, and exchange information
- **CRM Funnel Data**: Lead records with finance/exchange intents and follow-up counts

**Model**: LightGBM Regressor with MAPE of **20.39%** on test data

---

## 🏗️ Project Structure

```
src/
├── app.py              # Streamlit web application for interactive forecasting
├── build_dataset.py    # Data loading and aggregation from DMS/CRM sources
├── Feature_engg.py     # Advanced feature engineering (momentum, trends, seasonality)
├── train_model.py      # Model training with LightGBM and evaluation
└── forecasting.py      # 12-month ahead recursive forecasting for all models
data/
├── DMS_Sales_Data_Sample.csv          # Raw sales transaction data
├── CRM_Funnel_Data_Sample - Copy.csv  # Raw lead data
├── final_dataset.csv                  # Merged and aggregated data
└── final_dataset_fe.csv               # Data with engineered features
future_predictions.csv                 # 2026 monthly forecasts for all models
```

---

## 🔧 Pipeline Workflow

### 1. **Data Preparation** (`build_dataset.py`)
- Load DMS sales and CRM lead data
- Convert dates and create year-month periods
- Aggregate sales by model/month:
  - `Units_Sold`: Count of invoices
  - `Avg_Ex_Showroom_Price`: Average selling price
  - `Avg_Discount`: Average discount given
  - `Finance_Rate`: Percentage of purchases with financing
  - `Exchange_Rate`: Percentage with exchange
- Aggregate leads by model/month:
  - `Lead_Count`: Number of leads
  - `Finance_Intent_Rate`: % of leads interested in financing
  - `Exchange_Intent_Rate`: % of leads interested in exchange
  - `Avg_Followup_Count`: Average follow-ups per lead
- Merge sales and leads on Model + Year_Month
- Create temporal features: `year`, `month`, `quarter`
- Create lag features: `lag_1`, `lag_3`, `lag_6` (previous month sales)
- Create rolling averages: `rolling_mean_3`, `rolling_mean_6`

### 2. **Feature Engineering** (`Feature_engg.py`)
Advanced features extracted from base features:
- **Normalization**: `sales_vs_model_avg` (sales relative to model average)
- **Momentum Features**: `mom_1_3`, `mom_3_6` (growth rate between lag periods)
- **Trend Features**: `trend_3`, `trend_6` (slope of recent sales)
- **Interaction Features**:
  - `discount_pressure`: Discount × Finance_Rate
  - `lead_strength`: Lead_Count × (Finance_Intent + Exchange_Intent)
- **Seasonality Encoding**: `month_sin`, `month_cos` (cyclical month encoding)

### 3. **Model Training** (`train_model.py`)
- **Train-Test Split**: Time-based split (last 3 months as test)
- **Model**: LightGBM Regressor
  - n_estimators: 500
  - learning_rate: 0.05
  - max_depth: 6
  - num_leaves: 31
  - subsample: 0.8 (row sampling)
  - colsample_bytree: 0.8 (feature sampling)
- **Evaluation Metrics**:
  - MAPE (Mean Absolute Percentage Error): **20.39%**
  - RMSE (Root Mean Squared Error)
- **Encoding**: LabelEncoder for categorical Model variable

### 4. **Forecasting** (`forecasting.py`)
- **Method**: Recursive multi-step forecasting
  - Predicts month t+1 using features including predictions from month t
  - Updates lag and rolling average features with predictions
  - Repeats for 12 months ahead
- **For each model**: Generates 12-month forecast (Jan 2026 - Dec 2026)
- **Output**: `future_predictions.csv` with columns:
  - `model`: Car model name
  - `month`: YYYY-MM format
  - `predicted_units`: Forecasted monthly sales

### 5. **Interactive Dashboard** (`app.py`)
Streamlit web app features:
- **Model Selection**: Dropdown to choose car model
- **2026 Forecast Table**: Monthly predictions with predicted units
- **Forecast Visualization**: Line chart showing sales trend
- **Summary Metrics**:
  - Average monthly sales
  - Peak month
  - Lowest month
  - Total annual forecast
- **Historical Data Display**: Option to view historical sales by model

---

## 📊 Key Features

| Feature | Details |
|---------|---------|
| **Data Integration** | Merges DMS sales with CRM lead data |
| **Time-Series Features** | Lag features (lag_1/3/6), rolling averages (3/6-month) |
| **Business Features** | Pricing, discounts, finance rates, lead metrics, follow-ups |
| **Advanced Features** | Momentum, trend, seasonality, interaction features |
| **Model** | LightGBM with 500 trees, max_depth=6 |
| **Performance** | MAPE: 20.39% on 3-month test set |
| **Forecast Horizon** | 12-month (full year 2026) |
| **Deployment** | Interactive Streamlit web app |
---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Windows/macOS/Linux

### Installation

1. **Navigate to project directory**:
```bash
cd sales_forecasting_xgboost
```

2. **Create virtual environment**:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run data preparation pipeline**:
```bash
# Step 1: Build dataset from raw data
python src/build_dataset.py

# Step 2: Engineer features
python src/Feature_engg.py

# Step 3: Train model
python src/train_model.py

# Step 4: Generate forecasts
python src/forecasting.py
```

5. **Launch Streamlit app**:
```bash
python -m streamlit run src/app.py
```
Opens at `http://localhost:8501`

---

## 📊 Feature Dictionary

### Sales Features
- `Units_Sold`: Monthly vehicle units sold (target variable)
- `Avg_Ex_Showroom_Price`: Average ex-showroom price
- `Avg_Discount`: Average discount percentage offered
- `Finance_Rate`: Proportion of sales with financing
- `Exchange_Rate`: Proportion of sales with exchange

### Lead Features
- `Lead_Count`: Number of leads generated
- `Finance_Intent_Rate`: % of leads interested in financing
- `Exchange_Intent_Rate`: % of leads interested in exchange
- `Avg_Followup_Count`: Average follow-ups per lead

### Temporal Features
- `year`, `month`, `quarter`: Time decomposition
- `lag_1`, `lag_3`, `lag_6`: Sales from previous months
- `rolling_mean_3`, `rolling_mean_6`: 3 & 6-month rolling averages
- `month_sin`, `month_cos`: Cyclical encoding of month

### Derived Features
- `sales_vs_model_avg`: Normalized sales vs model average
- `mom_1_3`, `mom_3_6`: Momentum indicators (growth rates)
- `trend_3`, `trend_6`: Trend indicators (sales velocity)
- `discount_pressure`: Interaction of discount and financing
- `lead_strength`: Combined lead quality metric

---

## 💻 Running the Pipeline

### Full Execution (Data → Forecast)
```bash
# Build dataset from raw sources
python src/build_dataset.py
# Output: data/final_dataset.csv

# Engineer features
python src/Feature_engg.py
# Output: data/final_dataset_fe.csv

# Train model and evaluate
python src/train_model.py
# Output: lightgbm_sales_model.pkl
# Displays: MAPE, RMSE metrics

# Generate 2026 forecasts
python src/forecasting.py
# Output: future_predictions.csv

# View interactive dashboard
python -m streamlit run src/app.py
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 3.0.0 | Data manipulation & aggregation |
| numpy | 2.4.1 | Numerical operations |
| lightgbm | 3.1.3 | LightGBM gradient boosting |
| scikit-learn | 1.8.0 | Preprocessing, metrics, encoding |
| streamlit | Latest | Interactive web dashboard |
| joblib | 1.5.3 | Model serialization |
| matplotlib | Included | Visualization in Streamlit |

---

## 📋 Model Performance

**Test Set Metrics** (Last 3 months of data):
- **MAPE**: 20.39% (Mean Absolute Percentage Error)
- **RMSE**: Calculated in `train_model.py` output

**Forecast Coverage**: All 32 car models, 12-month horizon (Jan-Dec 2026)

---

## 🎯 Streamlit App Features

**Main Interface**:
- Model dropdown selector
- 2026 monthly forecast table
- Sales trend visualization
- Summary KPIs:
  - Average monthly sales
  - Peak month
  - Lowest month
  - Total annual forecast
- Historical data toggle

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FileNotFoundError` | Ensure `data/` folder contains CSV files |
| `Streamlit port error` | Change port: `streamlit run app.py --server.port 8502` |
| `No forecast data` | Run `python src/forecasting.py` to generate predictions |

---

## 📈 Model Architecture

```
Raw Data (DMS + CRM)
        ↓
    [build_dataset.py]
        ↓
Aggregated Dataset
        ↓
    [Feature_engg.py]
        ↓
Engineered Features
        ↓
    [train_model.py] ← LightGBM (500 trees, max_depth=6)
        ↓
Trained Model + Metrics
        ↓
    [forecasting.py] ← Recursive 12-month forecast
        ↓
future_predictions.csv
        ↓
    [app.py] ← Streamlit Dashboard
```

---

## 💡 Key Insights

1. **Recursive Forecasting**: Uses predicted values from month t as input for month t+1
2. **Lead-Sales Correlation**: Lead counts and finance intents strongly influence sales
3. **Seasonality**: Month encoding (sin/cos) captures annual patterns
4. **Model Variance**: Different car models have distinct sales patterns (lag features help)
5. **Business Impact**: Discount pressure and lead strength drive sales variance

---

## 🔧 Customization

### Adjust Forecast Horizon
In [src/forecasting.py](src/forecasting.py):
```python
# Change months_ahead parameter
forecasts = forecast_sales(model_name, months_ahead=24)  # 24-month forecast
```

### Change Train-Test Split
In [src/train_model.py](src/train_model.py):
```python
# Modify cutoff date
cutoff_date = max_date - pd.DateOffset(months=6)  # Use 6 months as test
```

### Tune Hyperparameters
In [src/train_model.py](src/train_model.py):
```python
model = lgb.LGBMRegressor(
    n_estimators=1000,      # More trees for better fit
    learning_rate=0.01,     # Lower learning rate for stability
    max_depth=8,            # Deeper trees for complex patterns
    num_leaves=50           # More leaves per tree
)
```

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Verify all dependencies are installed
3. Ensure data files exist in `data/` folder
4. Run scripts in sequence as documented

---

## 📄 License

This project is provided as-is for educational and commercial use.
)
```

### Adjust Festival Logic
In `src/predict_future.py`:
```python
festival = 1 if month_val in [10, 11] else 0  # Modify festival months
```

---

## 📝 Data Format

### Input Data Format (raw CSV)
Required columns:
```
date, units_sold, brand, model, city, segment, fuel_type, status,
ex_showroom_price, discount, dealer_stock, waiting_days, 
marketing_spend, festival, enquiry
```

---

## ⚠️ Important Notes

1. **Model Persistence**: Trained model is serialized as `.pkl` file - keep it safe
2. **Data Consistency**: Ensure feature order matches training data in predictions
3. **Missing Values**: Lag features create NaN values for initial rows - automatically dropped
4. **Business Assumptions**: Fixed marketing spend and enquiry values in forecasts can be customized

---

## 🤝 Contributing

To improve this project:
1. Experiment with different algorithms (LSTM, Prophet)
2. Add more sophisticated feature engineering
3. Implement cross-validation for robust evaluation
4. Add data validation and error handling

---

## 📞 Support & Troubleshooting

### Issue: Model file not found
**Solution**: Run training script first: `python src/train_model.py`

### Issue: Streamlit port already in use
**Solution**: `streamlit run app.py --server.port 8502`

### Issue: Dependency errors
**Solution**: Update pip and reinstall: `pip install --upgrade -r requirements.txt`

---

## 📄 License

This project is provided as-is for educational and business forecasting purposes.

---

## 📧 Project Details

**Created**: January 2026  
**Framework**: lightgbm+ Streamlit  
**Data Type**: Time-Series (Automobile Sales)  
**Prediction Type**: Regression (Units Sold)  
**Model Type**: Recursive Time-Series Forecasting
