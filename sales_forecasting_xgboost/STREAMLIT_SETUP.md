# Streamlit Setup Guide

## Quick Start

This guide will help you run the interactive Streamlit interface for the Sales Forecasting model.

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation & Running

#### Step 1: Install Dependencies
Navigate to the project directory and install required packages:

```bash
pip install -r requirements.txt
```

#### Step 2: Run the Streamlit App

From the project root directory, run:

```bash
streamlit run streamlit_app.py
```

Or from the `src` directory:

```bash
cd src
streamlit run ../streamlit_app.py
```

#### Step 3: Access the Interface
- The app will automatically open in your default browser
- If not, visit: `http://localhost:8501`

### Features

#### 🔮 Make Prediction Tab
- **Input vehicle parameters** (model, price, discount, etc.)
- **Get real-time predictions** for sales units
- **View detailed analysis** with historical comparisons
- **See visualizations** of predictions vs historical data

#### 📊 View Forecasts Tab
- **Pre-computed 12-month forecasts** for all models
- **Interactive model selection**
- **Summary statistics** (average, peak, lowest months)
- **Time-series visualization**

#### 📖 Help & Guide Tab
- **Feature descriptions** and explanations
- **Model performance metrics**
- **Tips for better predictions**
- **Usage guidelines**

### Key Input Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| Car Model | Selection | Choose from available models |
| Price (₹) | 0+ | Average ex-showroom price |
| Discount (%) | 0-100 | Discount percentage offered |
| Finance Rate (%) | 0-15 | Interest rate for financing |
| Exchange Rate | 0+ | INR/USD conversion rate |
| Lead Count | 0+ | Number of potential customers |
| Finance Intent (%) | 0-100 | % leads interested in financing |
| Exchange Intent (%) | 0-100 | % leads interested in exchange |
| Followup Count | 0-20 | Average follow-ups per lead |

### Understanding Predictions

The model predicts **Units Sold** based on:
- Historical sales patterns
- Market conditions (price, discounts, rates)
- Customer interest indicators
- Temporal features (month, quarter, year)
- Lag and rolling average features

### Troubleshooting

**Issue: Model file not found**
```
Solution: Ensure lightgbm_sales_model.pkl is in the project root directory
```

**Issue: Data file not found**
```
Solution: Ensure data/final_dataset.csv exists in the project directory
```

**Issue: Port already in use**
```
Solution: Run with a different port:
streamlit run streamlit_app.py --server.port 8502
```

**Issue: ModuleNotFoundError**
```
Solution: Reinstall requirements:
pip install -r requirements.txt --upgrade
```

### Performance Tips

1. **First Load**: The app caches data on first run for faster subsequent access
2. **Multiple Predictions**: Make as many predictions as needed - they run instantly
3. **Export Results**: Copy-paste predictions table to Excel if needed
4. **Share Results**: Take screenshots of visualizations for presentations

### Project Structure

```
sales_forecasting_xgboost/
├── streamlit_app.py              # Main Streamlit interface
├── requirements.txt              # Python dependencies
├── lightgbm_sales_model.pkl      # Trained model
├── model_encoder.pkl             # Feature encoder
├── future_predictions.csv        # Pre-computed forecasts
├── data/
│   ├── final_dataset.csv         # Complete dataset
│   ├── final_dataset_fe.csv      # Feature engineered dataset
│   └── [other data files]
└── src/
    ├── train_model.py            # Model training script
    ├── forecasting.py            # Forecasting functions
    └── [other source files]
```

### Next Steps

1. **Make Your First Prediction** - Go to "Make Prediction" tab
2. **Explore the Data** - Check "View Forecasts" for historical patterns
3. **Learn More** - Read the "Help & Guide" tab for tips
4. **Integrate with Your Workflow** - Export predictions for analysis

### Contact & Support

For issues or questions:
- Check the Help & Guide tab in the app
- Review the model documentation
- Verify all data files are present

---

**Version:** 1.0  
**Last Updated:** 2026-06-08  
**Model:** LightGBM Sales Forecasting
