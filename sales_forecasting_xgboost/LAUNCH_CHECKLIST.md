# ✅ Pre-Launch Checklist

Before running the Streamlit app, verify these items:

## 📋 System Requirements

- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip package manager available (`pip --version`)
- [ ] 2GB+ free disk space
- [ ] Modern web browser (Chrome, Firefox, Edge, Safari)
- [ ] Internet connection (for first-time package installation)

## 📁 Project Files

Verify these files exist in the project root:

### Model & Data Files
- [ ] `lightgbm_sales_model.pkl` (Trained model)
- [ ] `model_encoder.pkl` (Feature encoder)
- [ ] `future_predictions.csv` (Pre-computed forecasts)

### Data Files
- [ ] `data/final_dataset.csv` (Main training data)
- [ ] `data/final_dataset_fe.csv` (Feature engineered data)
- [ ] `data/CRM_Funnel_Data_Sample - Copy.csv`
- [ ] `data/DMS_Sales_Data_Sample.csv`

### Configuration Files
- [ ] `requirements.txt` (Dependencies list)
- [ ] `streamlit_app.py` (Main app file)

### Documentation Files
- [ ] `README.md` (Project overview)
- [ ] `STREAMLIT_SETUP.md` (Setup instructions)
- [ ] `STREAMLIT_USER_GUIDE.md` (User manual)

### Source Files (Optional)
- [ ] `src/app.py`
- [ ] `src/train_model.py`
- [ ] `src/forecasting.py`
- [ ] `src/Feature_engg.py`
- [ ] `src/build_dataset.py`

## 🔧 Installation

- [ ] Ran: `pip install -r requirements.txt`
- [ ] No errors during installation
- [ ] All packages installed successfully

## 🧪 Verification Commands

Run these to verify setup:

```bash
# Check Python
python --version
# Expected: Python 3.8+

# Check pip
pip --version
# Expected: pip version

# Check Streamlit
pip show streamlit
# Expected: Location and version info

# Check model files
ls -la lightgbm_sales_model.pkl
# Expected: File exists with size > 1MB

# Check data files
ls -la data/final_dataset.csv
# Expected: File exists with size > 1MB
```

- [ ] All verification commands passed

## 🚀 Launch Test

```bash
# From project root directory
streamlit run streamlit_app.py
```

- [ ] App started without errors
- [ ] Browser opened automatically
- [ ] Dashboard loaded successfully
- [ ] All tabs visible (Make Prediction, View Forecasts, Help & Guide)

## ✨ Feature Verification

### Make Prediction Tab
- [ ] Car Model dropdown works
- [ ] All input fields accept values
- [ ] "Generate Prediction" button clickable
- [ ] Predictions generate successfully
- [ ] Results display properly
- [ ] Charts render correctly

### View Forecasts Tab
- [ ] Model selection dropdown works
- [ ] Forecast data displays
- [ ] Summary metrics show
- [ ] Chart visualizes correctly
- [ ] Table displays forecast data

### Help & Guide Tab
- [ ] Information displays properly
- [ ] All sections readable
- [ ] No formatting issues

## 🔍 Data Validation

- [ ] At least 10 car models available
- [ ] Date range: 2+ years of data
- [ ] No corrupted data files
- [ ] Feature columns present in dataset
- [ ] Target variable (Units_Sold) exists

## 📊 Model Validation

- [ ] Model file loads without errors
- [ ] Encoder file loads without errors
- [ ] Predictions are numeric (not NaN)
- [ ] Predictions are non-negative
- [ ] Predictions are reasonable range

## 🌐 Browser & Display

- [ ] App displays in sidebar correctly
- [ ] Input fields styled properly
- [ ] Buttons responsive
- [ ] Charts display without scaling issues
- [ ] Text is readable (no overlaps)
- [ ] Mobile responsive (optional)

## 📝 Documentation

- [ ] Setup guide is clear
- [ ] User guide covers all features
- [ ] Troubleshooting section helpful
- [ ] File paths are correct
- [ ] Commands are copy-paste ready

## ✅ Ready to Use?

If all checkboxes are marked:

### ✨ Your Streamlit app is ready!

**Quick Start:**
```bash
streamlit run streamlit_app.py
```

**Next Steps:**
1. Go to "Make Prediction" tab
2. Select a car model
3. Enter sample parameters
4. Click "Generate Prediction"
5. Review results

## ❌ Issues Found?

### If checkboxes are unchecked:

1. **Missing Files**: Download from project repository
2. **Installation Errors**: Run `pip install -r requirements.txt --upgrade`
3. **Python Version**: Upgrade to Python 3.8+
4. **Port Issues**: Use different port:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```
5. **Other Issues**: Check STREAMLIT_SETUP.md Troubleshooting section

## 🆘 Emergency Reset

If everything fails, try:

```bash
# Clean installation
pip uninstall -r requirements.txt -y
pip cache purge
pip install -r requirements.txt

# Clear Streamlit cache
streamlit cache clear

# Try again
streamlit run streamlit_app.py
```

## 📞 Support Resources

- 📖 [Streamlit Documentation](https://docs.streamlit.io/)
- 🐍 [Python Documentation](https://docs.python.org/)
- 🔗 [LightGBM Documentation](https://lightgbm.readthedocs.io/)
- 🐧 [Pandas Documentation](https://pandas.pydata.org/)

---

**Last Updated**: 2026-06-08  
**Streamlit Version**: 1.41.1+  
**Python Version**: 3.8+

**Status**: ✅ Ready to Launch
