# Streamlit Sales Forecasting Interface - User Guide

## Overview

The **Automobile Sales Forecasting Streamlit Interface** is an interactive web application that allows you to:
- ✅ Enter real-time sales data and parameters
- 🔮 Get instant sales predictions
- 📊 View pre-computed 12-month forecasts
- 📈 Analyze historical trends and patterns
- 📖 Learn model features and best practices

## Getting Started

### Quick Start (Easiest Method)

**Windows Users:**
```bash
# Simply double-click:
run_app.bat
```

**Mac/Linux Users:**
```bash
python run_app.py
```

**Or manually from terminal:**
```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start the app
streamlit run streamlit_app.py
```

The app will open automatically at `http://localhost:8501`

---

## User Interface Guide

### 📍 Sidebar (Left Panel)

The sidebar displays:
- **Model Information**: Algorithm details and performance metrics
- **Data Statistics**: Overview of the training dataset
  - Total records
  - Number of car models
  - Date range

### 🔳 Main Tabs

The interface is organized into 3 tabs:

---

## Tab 1: 🔮 Make Prediction

### How to Use

This tab allows you to input custom parameters and get instant sales predictions.

#### Step 1: Select Car Model
```
📍 Dropdown: "Car Model"
└─ Choose the vehicle model you want to forecast
```

#### Step 2: Enter Vehicle & Market Information

**Left Column:**
- **Avg Ex-Showroom Price (₹)**: The base price of the vehicle
  - Range: Any positive number
  - Example: 1,500,000 for luxury vehicle
  - Impact: Higher prices typically reduce sales volume

- **Avg Discount (%)**: Percentage discount offered
  - Range: 0-100%
  - Example: 5% for modest discount
  - Impact: Higher discounts boost sales

- **Finance Rate (%)**: Interest rate for loans
  - Range: 0-15%
  - Example: 8.5% for competitive rate
  - Impact: Lower rates increase financed purchases

- **Exchange Rate (INR/USD)**: Currency conversion
  - Example: 83.5 for current rate
  - Impact: Affects import costs and pricing

#### Step 3: Enter Sales & Lead Information

**Right Column:**
- **Lead Count**: Number of potential customers
  - Example: 500 leads
  - Impact: More leads typically increase sales

- **Finance Intent Rate (%)**: % of leads interested in loans
  - Range: 0-100%
  - Example: 65%
  - Impact: Higher intent improves conversion

- **Exchange Intent Rate (%)**: % of leads interested in trade-ins
  - Range: 0-100%
  - Example: 45%
  - Impact: Trade-in offers can boost sales

- **Avg Followup Count**: Follow-ups per lead
  - Range: 0-20
  - Example: 5 follow-ups
  - Impact: More follow-ups improve closure rates

#### Step 4: Enter Time Period

**Bottom Row:**
- **Prediction Year**: Year for forecast (2024-2030)
- **Prediction Month**: Month for forecast (1-12)
- **Quarter**: Auto-calculated (Q1-Q4)
- **Last Sales**: Shows historical context

#### Step 5: Generate Prediction

Click the **"🎯 Generate Prediction"** button (blue button).

### Results Display

After prediction, you'll see:

#### 📊 Key Metrics (4 Cards)
1. **Predicted Sales**: Main prediction with trend indicator
2. **Car Model**: Selected model confirmation
3. **Month**: Prediction date
4. **vs Historical Avg**: How prediction compares to average

#### 📈 Detailed Analysis

**Left Section - Input Parameters Table:**
Shows all your input values for reference

**Right Section - Model Insights:**
- Historical average sales
- Maximum historical sales
- Minimum historical sales
- Current trend direction

#### 📊 Visualization (Chart)

Shows:
- Blue line: Last 24 months of actual sales
- Orange star: Your prediction point
- X-axis: Time
- Y-axis: Units sold

### Interpreting Results

| Scenario | Meaning | Action |
|----------|---------|--------|
| Prediction > Historical Avg | Above average | Good market conditions |
| Prediction < Historical Avg | Below average | Challenging market |
| Upward Trend | Sales increasing | Momentum is positive |
| Downward Trend | Sales decreasing | May need adjustment |
| Stable Trend | Consistent sales | Predictable market |

---

## Tab 2: 📊 View Forecasts

This tab shows pre-computed 12-month forecasts.

### How to Use

1. **Select Model**: Choose a car model from dropdown
2. **View Metrics**: 4 cards showing:
   - Average monthly forecast
   - Peak sales month
   - Lowest sales month
   - Total annual forecast

3. **Review Table**: Month-by-month predictions
4. **Analyze Chart**: Visualize sales pattern with filled area

### When to Use

- 📋 Review multiple scenarios
- 🎯 Strategic planning
- 📊 Comparing models
- 💼 Reporting to stakeholders

---

## Tab 3: 📖 Help & Guide

Complete reference guide including:

### Feature Descriptions
Detailed explanation of each parameter and its impact.

### Model Performance
- Algorithm: LightGBM
- Accuracy: ~20.39% MAPE
- What it means: Predictions typically within 20% of actual

### Usage Tips
Best practices for accurate predictions:
1. Use recent market data
2. Validate assumptions with team
3. Monitor actual vs predicted
4. Try scenario analysis
5. Retrain periodically

---

## Common Use Cases

### 🎯 Use Case 1: Monthly Sales Planning

**Scenario**: Plan next month's targets

**Steps**:
1. Go to "Make Prediction" tab
2. Enter expected market conditions
3. Set month to next month
4. Generate prediction
5. Use as sales target

### 🎯 Use Case 2: Scenario Analysis

**Scenario**: What if we increase discount by 5%?

**Steps**:
1. First prediction: Current discount (e.g., 5%)
2. Second prediction: Higher discount (e.g., 10%)
3. Compare results
4. Decide on strategy

### 🎯 Use Case 3: Price Sensitivity

**Scenario**: Impact of pricing strategy

**Steps**:
1. Predict with current price
2. Predict with +10% price
3. Predict with -10% price
4. Analyze demand elasticity

### 🎯 Use Case 4: Lead Generation ROI

**Scenario**: Should we increase lead generation?

**Steps**:
1. Predict with current leads
2. Predict with 50% more leads
3. Calculate additional revenue
4. Compare with marketing cost

---

## Tips for Best Results

### ✅ DO:
- Use data from last 2-3 months for reference
- Validate numbers with your team
- Document assumptions made
- Track actual vs predicted sales
- Update regularly with new data

### ❌ DON'T:
- Use unrealistic parameters
- Ignore market trends
- Make predictions without recent data
- Trust predictions alone for major decisions
- Forget to account for seasonality

---

## Troubleshooting

### Issue: App won't start
**Solution**: 
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Try again
streamlit run streamlit_app.py
```

### Issue: "Model file not found"
**Solution**: Ensure these files exist in project root:
- `lightgbm_sales_model.pkl`
- `data/final_dataset.csv`

### Issue: Slow predictions
**Solution**: 
- App caches data automatically
- First prediction is slightly slower
- Subsequent predictions are instant

### Issue: Port already in use
**Solution**:
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop the app |
| `R` | Rerun the app |
| `Ctrl+R` | Clear cache |

---

## Data Export

### To Export Prediction Results:

1. **For Metrics**: Take screenshot of cards
2. **For Table**: Copy-paste to Excel
3. **For Chart**: Right-click chart → Save image

### To Export Forecast Data:

1. Go to "View Forecasts" tab
2. Display the table
3. Select and copy
4. Paste into Excel/Google Sheets

---

## Advanced Usage

### Running with Custom Settings

```bash
# Run on specific port
streamlit run streamlit_app.py --server.port 8502

# Run headless (no browser)
streamlit run streamlit_app.py --logger.level=error --client.showErrorDetails=false

# Run with custom configuration
streamlit run streamlit_app.py --config.magicEnabled=false
```

### Sharing the App

**Share locally**:
```bash
# Get your IP address
ipconfig
# Share: http://<your-ip>:8501
```

**Deploy to cloud**:
- Streamlit Cloud (free)
- Heroku
- AWS
- Google Cloud
- Azure

---

## Model Information

### Algorithm: LightGBM (Light Gradient Boosting)

**Why LightGBM?**
- ⚡ Fast training and prediction
- 🎯 Excellent accuracy
- 📊 Handles categorical features well
- 💾 Memory efficient

### Input Features (16 total)
1. **Model** (categorical)
2. **Avg_Ex_Showroom_Price** (numeric)
3. **Avg_Discount** (numeric)
4. **Finance_Rate** (numeric)
5. **Exchange_Rate** (numeric)
6. **Lead_Count** (numeric)
7. **Finance_Intent_Rate** (numeric)
8. **Exchange_Intent_Rate** (numeric)
9. **Avg_Followup_Count** (numeric)
10. **year** (temporal)
11. **month** (temporal)
12. **quarter** (temporal)
13. **lag_1** (previous month sales)
14. **lag_3** (sales 3 months ago)
15. **lag_6** (sales 6 months ago)
16. **rolling_mean_3** (avg of last 3 months)
17. **rolling_mean_6** (avg of last 6 months)

### Output
- **Units_Sold** (numeric): Predicted number of units sold

---

## Performance Metrics

| Metric | Value | Interpretation |
|--------|-------|-----------------|
| MAPE | 20.39% | Predictions within 20% of actual |
| RMSE | Variable | Error in absolute units |
| R² Score | High | Model explains variation well |

---

## Support & Feedback

- 📧 Questions? Check the Help tab in-app
- 🐛 Found a bug? Verify file paths and dependencies
- 💡 Suggestions? Document and share with team

---

## Project Files

```
sales_forecasting_xgboost/
│
├── streamlit_app.py              ← Main app (run this)
├── run_app.py                    ← Python launcher
├── run_app.bat                   ← Windows launcher
├── requirements.txt              ← Dependencies
│
├── STREAMLIT_SETUP.md            ← Setup guide
├── STREAMLIT_USER_GUIDE.md       ← This file
│
├── lightgbm_sales_model.pkl      ← Pre-trained model
├── model_encoder.pkl             ← Feature encoder
├── future_predictions.csv        ← Pre-computed forecasts
│
└── data/
    ├── final_dataset.csv         ← Training data
    ├── final_dataset_fe.csv      ← Feature engineered data
    └── [other data files]
```

---

## Version Information

- **Version**: 1.0
- **Last Updated**: 2026-06-08
- **Streamlit**: 1.41.1+
- **Python**: 3.8+
- **Model**: LightGBM Sales Forecasting

---

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  QUICK PREDICTION CHECKLIST                 │
├─────────────────────────────────────────────┤
│ ☐ Select car model                          │
│ ☐ Enter vehicle price                       │
│ ☐ Enter expected discount                   │
│ ☐ Enter finance rate                        │
│ ☐ Enter exchange rate                       │
│ ☐ Enter lead count                          │
│ ☐ Enter finance interest %                  │
│ ☐ Enter exchange interest %                 │
│ ☐ Enter followup count                      │
│ ☐ Select prediction year/month              │
│ ☐ Click "Generate Prediction"               │
│ ☐ Review results and insights               │
│ ☐ Export/Share if needed                    │
└─────────────────────────────────────────────┘
```

---

**Happy Forecasting! 🚗📊**
