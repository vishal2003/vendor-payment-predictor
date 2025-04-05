# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Page Configuration
st.set_page_config(page_title="Vendor Payment Delay Predictor", layout="centered")

# ---------- Load & Preprocess Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv('vendor_payments.csv', parse_dates=['Invoice_Date', 'Payment_Due_Date', 'Payment_Date'])

    # Rename 'Amount' to 'Invoice_Amount'
    if 'Amount' in df.columns:
        df.rename(columns={'Amount': 'Invoice_Amount'}, inplace=True)
    else:
        st.error("❌ 'Amount' column not found in CSV.")
        st.stop()

    # Calculate Delay
    df['Delay_Days'] = (df['Payment_Date'] - df['Payment_Due_Date']).dt.days
    df['is_delayed'] = df['Delay_Days'].apply(lambda x: 1 if x > 0 else 0)

    # One-hot encoding
    df = pd.get_dummies(df, columns=['Payment_Method', 'Department'], drop_first=True)

    return df

df = load_data()

# ---------- Model Training ----------
feature_cols = ['Invoice_Amount'] + [col for col in df.columns if col.startswith('Payment_Method_') or col.startswith('Department_')]
X = df[feature_cols]
y = df['Delay_Days']

model = RandomForestRegressor(random_state=42, n_estimators=100)
model.fit(X, y)

# ---------- UI Design ----------
st.title("📊 Vendor Payment Delay Predictor")
st.markdown("Use this tool to predict whether a vendor payment will be delayed based on historical trends.")

# Load for dropdown options
raw_df = pd.read_csv('vendor_payments.csv')
payment_methods = sorted(raw_df['Payment_Method'].dropna().unique())
departments = sorted(raw_df['Department'].dropna().unique())

# ---------- User Inputs ----------
st.markdown("### 🔍 Enter Invoice Details")
col1, col2 = st.columns(2)
with col1:
    payment_method = st.selectbox("💳 Select Payment Method", payment_methods)
with col2:
    department = st.selectbox("🏢 Select Department", departments)

invoice_amount = st.number_input("💰 Invoice Amount (in ₹)", value=1000.0, min_value=0.0, step=100.0)

# ---------- Prepare Input for Prediction ----------
input_data = {col: 0 for col in feature_cols}
input_data['Invoice_Amount'] = invoice_amount

pm_col = f'Payment_Method_{payment_method}'
dept_col = f'Department_{department}'

if pm_col in input_data:
    input_data[pm_col] = 1
if dept_col in input_data:
    input_data[dept_col] = 1

input_df = pd.DataFrame([input_data])

# ---------- Predict & Show Result ----------
if st.button("🚀 Predict Delay"):
    delay_pred = model.predict(input_df)[0]
    delay_pred = round(delay_pred, 2)

    st.markdown("### 📈 Prediction Result")

    if delay_pred <= 0:
        st.success(f"✅ Payment is likely to be **on-time or early**!\n\n🕒 Predicted Delay: `{delay_pred}` days")
    else:
        st.warning(f"⚠️ Expected Delay: **{delay_pred} days**\n\n📌 Consider reviewing payment schedule or method.")

    st.markdown("---")
    st.markdown("📌 _Prediction based on historical data & vendor behavior patterns_")
