# --- Streamlit Müşteri Segmentasyonu ve Limit Tahminleme Platformu ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="SmartLimit | Dashboard", page_icon="📊", layout="wide")

# --- VERİ YÜKLEME + TEMİZLEME ---
@st.cache_data
def load_and_clean_merged_csv():
    github_raw_prefix = "https://raw.githubusercontent.com/tturan6446/ITUbitirme/main/"
    file_names = [f"merged_data_part{i}.csv" for i in range(1, 11)]

    df_list = []
    for file in file_names:
        url = github_raw_prefix + file
        df = pd.read_csv(url)
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)

    def clean_currency(x):
        if isinstance(x, str):
            return float(x.replace('$', '').replace(',', '').strip())
        return x

    currency_columns = ['total_debt', 'yearly_income', 'credit_limit', 'amount']
    for col in currency_columns:
        df[col] = df[col].apply(clean_currency)

    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    df = df.drop(columns=['errors', 'merchant_id', 'user_id'], errors='ignore')

    return df

df = load_and_clean_merged_csv()

# --- SEGMENTASYON (K-MEANS) ---
features = df[['credit_score', 'yearly_income', 'total_debt', 'amount']].copy()
features = features.dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
features['segment'] = kmeans.fit_predict(X_scaled)

segment_map = {
    0: "Riskli & Düşük Gelirli",
    1: "Premium Müşteri",
    2: "Gelişmekte Olan Müşteri",
    3: "Borç Yükü Altında"
}
features['segment_label'] = features['segment'].map(segment_map)

# Segment label'ı ana df ile birleştir
df = df.merge(features[['credit_score', 'yearly_income', 'total_debt', 'amount', 'segment_label']],
              on=['credit_score', 'yearly_income', 'total_debt', 'amount'],
              how='left')

# --- MENÜ ---
with st.sidebar:
    selected = option_menu(
        menu_title="SmartLimit Menü",
        options=["Ana Sayfa", "Segment Analizi", "Veri Önizleme"],
        icons=["house", "bar-chart", "table"],
        menu_icon="cast",
        default_index=0
    )

# --- SAYFA İÇERİĞİ ---
if selected == "Ana Sayfa":
    st.title("📊 SmartLimit Dashboard")
    st.markdown("Bu platform, müşteri segmentasyonunu ve kredi limit analizini görselleştirmenizi sağlar.")

elif selected == "Segment Analizi":
    st.subheader("Segment Dağılımı")
    fig = px.histogram(df, x="segment_label", color="segment_label", title="Segmentlere Göre Müşteri Dağılımı")
    st.plotly_chart(fig)

elif selected == "Veri Önizleme":
    st.subheader("Ham Veri")
    st.dataframe(df.head(100))
