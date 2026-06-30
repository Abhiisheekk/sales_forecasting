# 📈 Sales Forecasting Using XGBoost

A Machine Learning project that predicts future sales using the XGBoost algorithm. The project includes data preprocessing, feature engineering, model training, future forecasting, batch prediction, and an interactive Streamlit web application for visualization and prediction.

---

## 🚀 Project Overview

This project demonstrates an end-to-end sales forecasting pipeline using historical sales data. It leverages machine learning techniques to generate accurate forecasts that can assist businesses in inventory planning, demand forecasting, and strategic decision-making.

The application allows users to:

- Predict future sales
- Generate forecasts for multiple future dates
- Perform batch predictions using CSV files
- Visualize sales trends
- Interact with the model through a Streamlit dashboard

---

## 🏗️ Project Architecture

```
Sales Forecasting
│
├── Data Collection
│
├── Data Preprocessing
│
├── Feature Engineering
│
├── Model Training (XGBoost)
│
├── Model Evaluation
│
├── Future Sales Prediction
│
└── Streamlit Dashboard
```

---

## 📂 Project Structure

```
sales_forecasting_xgboost
│
├── data/
│   ├── raw_data
│   └── processed_data
│
├── src/
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   └── prediction.py
│
├── streamlit_app.py
├── requirements.txt
├── xgboost_sales_model.pkl
├── lightgbm_sales_model.pkl
├── README.md
└── ...
```

---

## 🛠️ Technologies Used

- Python
- XGBoost
- LightGBM
- Pandas
- NumPy
- Scikit-Learn
- Matplotlib
- Streamlit
- Joblib

---

## 📊 Machine Learning Pipeline

### Data Preprocessing

- Missing value handling
- Data cleaning
- Feature encoding
- Date formatting

### Feature Engineering

- Lag Features
- Rolling Statistics
- Calendar Features
- Time-based Features

### Model Training

- XGBoost Regressor
- Hyperparameter Optimization
- Model Serialization

### Model Evaluation

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)

---

## 📈 Features

- Historical sales analysis
- Future sales forecasting
- Batch prediction using CSV files
- Interactive visualizations
- Download prediction results
- User-friendly Streamlit interface

---

## 💻 Installation

Clone the repository

```bash
git clone https://github.com/Abhiisheekk/sales_forecasting.git
```

Move into the project directory

```bash
cd sales_forecasting_xgboost
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Launch the Streamlit app

```bash
streamlit run streamlit_app.py
```

The application will open automatically in your browser.

---

## 📷 Application Preview

> Add screenshots of your Streamlit dashboard here.

Example:

```
images/dashboard.png
images/prediction.png
images/charts.png
```

---

## 📁 Sample Outputs

- Future Sales Forecast
- Batch Prediction Report
- Sales Trend Visualization
- Forecast Charts

---

## 📊 Business Applications

- Retail Sales Forecasting
- Inventory Management
- Demand Planning
- Supply Chain Optimization
- Revenue Forecasting
- Production Planning

---

## 🔮 Future Improvements

- LSTM and Deep Learning Models
- Prophet Time Series Forecasting
- Real-Time Data Integration
- Cloud Deployment
- API Integration
- Automated Model Retraining

---

## 👨‍💻 Author

**Abhishek**

Computer Science Engineering Student

Interested in

- Data Analytics
- Machine Learning
- Data Engineering
- Business Intelligence

---

## ⭐ If you found this project useful, consider giving it a star!
