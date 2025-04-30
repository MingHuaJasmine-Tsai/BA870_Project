# --- pages/3_Get_Features.py ---
# 📂 Get Features for a Specific Date

import streamlit as st
import pandas as pd
from features import get_features_for_date

st.set_page_config(page_title="Get Features", layout="wide")
st.title("📂 Get Features for a Specific Date")

# --- Date Picker ---
target_date = st.date_input(
    label="📅 Select a date:",
    value=pd.to_datetime("2025-04-25"),
    min_value=pd.to_datetime("2010-01-01"),
    max_value=pd.to_datetime("2025-12-31")
)

# --- Action Button ---
if st.button("🔍 Get Features"):
    with st.spinner("Extracting features for model input..."):
        try:
            features = get_features_for_date(target_date.strftime("%Y-%m-%d"))
            st.success("✅ Features successfully generated!")
            st.dataframe(features, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error generating features: {e}")

