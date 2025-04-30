# --- pages/4_Predict_Volume.py ---
# 🔮 Predict Volume for a Specific Date

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import yfinance as yf
from features import get_features_for_date

st.set_page_config(page_title="Predict Volume", layout="wide")
st.title("🔮 Predict Trading Volume")

# --- Load trained models ---
with open('models/best_model_spy.pkl', 'rb') as f:
    model_spy = pickle.load(f)
with open('models/best_model_sso.pkl', 'rb') as f:
    model_sso = pickle.load(f)
with open('models/best_model_upro.pkl', 'rb') as f:
    model_upro = pickle.load(f)

# --- Select prediction date ---
target_date = st.date_input("Select a date to predict:", value=pd.to_datetime("2025-04-25"))

# --- Predict button ---
if st.button("Predict Volume"):
    with st.spinner("Predicting..."):
        date_str = target_date.strftime("%Y-%m-%d")

        # --- Get features
        try:
            features_spy = get_features_for_date(date_str, ticker="SPY").astype(float)
            features_sso = get_features_for_date(date_str, ticker="SSO").astype(float)
            features_upro = get_features_for_date(date_str, ticker="UPRO").astype(float)
        except Exception as e:
            st.error(f"❌ Failed to fetch features: {e}")
            st.stop()

        # --- Lag return function with fallback lookback
        def get_lag_return(ticker, date_str, lookback_days=5):
            dt = pd.to_datetime(date_str)
            for delta in range(1, lookback_days + 1):
                start = dt - pd.Timedelta(days=delta)
                end = dt + pd.Timedelta(days=1)
                prices = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), progress=False)["Close"]
                returns = np.log(prices).diff()
                if not returns.dropna().empty:
                    return returns.dropna().iloc[-1]
            raise ValueError(f"Unable to find lag return for {ticker} on {date_str}")

        try:
            lag_return_spy = get_lag_return("SPY", date_str)
            lag_return_sso = get_lag_return("SSO", date_str)
            lag_return_upro = get_lag_return("UPRO", date_str)
        except Exception as e:
            st.error(f"❌ Lag return error: {e}")
            st.stop()

        # --- Inject lag return
        features_spy["lag_return"] = lag_return_spy
        features_sso["lag_return"] = lag_return_sso
        features_upro["lag_return"] = lag_return_upro

        # --- Final feature list
        ml_features_clean = [
            'lag_vol', 'lag_return', 'rolling_std_5d', 'lag_vix',
            'NFP_surprise_z', 'ISM_surprise_z', 'CPI_surprise_z',
            'Housing_Starts_surprise_z', 'Jobless_Claims_surprise_z',
            'monday_dummy', 'wednesday_dummy', 'friday_dummy'
        ]

        # --- Predict
        pred_log_spy = model_spy.predict(features_spy[ml_features_clean])[0]
        pred_vol_spy = np.exp(pred_log_spy) - 1

        pred_log_sso = model_sso.predict(features_sso[ml_features_clean])[0]
        pred_vol_sso = np.exp(pred_log_sso) - 1

        pred_log_upro = model_upro.predict(features_upro[ml_features_clean])[0]
        pred_vol_upro = np.exp(pred_log_upro) - 1

        # --- Output in Tabs
        tab1, tab2, tab3 = st.tabs(["SPY", "SSO", "UPRO"])

        with tab1:
            st.subheader("📊 SPY Prediction")
            st.metric(label="Predicted log(volume+1)", value=f"{pred_log_spy:.4f}")
            st.metric(label="Predicted volume", value=f"{pred_vol_spy:,.0f}")

        with tab2:
            st.subheader("📊 SSO Prediction")
            st.metric(label="Predicted log(volume+1)", value=f"{pred_log_sso:.4f}")
            st.metric(label="Predicted volume", value=f"{pred_vol_sso:,.0f}")

        with tab3:
            st.subheader("📊 UPRO Prediction")
            st.metric(label="Predicted log(volume+1)", value=f"{pred_log_upro:.4f}")
            st.metric(label="Predicted volume", value=f"{pred_vol_upro:,.0f}")
