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

# --- VERI YÜKLEME + TEMIZLEME ---
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

# --- SEGMENTASYON (K-MEANS) ---
def apply_segmentation(df):
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

    df = df.merge(features[['credit_score', 'yearly_income', 'total_debt', 'amount', 'segment_label']],
                  on=['credit_score', 'yearly_income', 'total_debt', 'amount'],
                  how='left')
    return df

# --- ANA MENÜ ---
def main():
    df = load_and_clean_merged_csv()
    df = apply_segmentation(df)

    selected = option_menu(
        menu_title=None,
        options=["🔹 Segment Dağılımı", "🔹 Veriler"],
        icons=["bar-chart", "table"],
        orientation="horizontal"
    )

    if selected == "🔹 Segment Dağılımı":
        st.header("Müşteri Segment Dağılımı")
        seg_counts = df['segment_label'].value_counts()
        fig = px.pie(values=seg_counts.values, names=seg_counts.index,
                     title="Segmentlere Göre Müşteri Dağılımı",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    elif selected == "🔹 Veriler":
        st.header("Veri Tablosu")
        st.dataframe(df.head(50))

# --- UYGULAMA ÇALIŞTIR ---
if __name__ == '__main__':
    main()
