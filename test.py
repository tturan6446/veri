# --- GEREKLİ KÜTÜPHANELER ---
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import streamlit as st

# --- VERİ YÜKLE ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/tturan6446/ITUbitirme/main/merged_data_part1.csv"  # örnek, istersen tüm partları birleştirebilirim
    df = pd.read_csv(url)
    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    df['txn_month'] = df['txn_date'].dt.to_period('M').astype(str)
    return df

df_sample = load_data()
# --- VERİYİ TEMİZLE ve SAYISALA ÇEVİR ---
features = df_sample[['credit_score', 'yearly_income', 'total_debt', 'amount']].copy()
features.dropna(inplace=True)

# String olan '$' ve ',' karakterlerini temizle
for col in ['credit_score', 'yearly_income', 'total_debt', 'amount']:
    features[col] = (
        features[col]
        .astype(str)
        .str.replace(r'[$,]', '', regex=True)
        .astype(float)
    )

# --- SCALE ET ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)


# --- SEGMENTASYON İÇİN VERİYİ HAZIRLA ---
features = df_sample[['credit_score', 'yearly_income', 'total_debt', 'amount']].copy()
features.dropna(inplace=True)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# --- K-MEANS İLE KÜMELEME ---
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
features['segment'] = kmeans.fit_predict(X_scaled)

# --- SEGMENTLERİ HARİTALA ---
segment_map = {
    0: "Riskli & Düşük Gelirli",
    1: "Premium Müşteri",
    2: "Gelişmekte Olan Müşteri",
    3: "Borç Yükü Altında"
}
features['segment_label'] = features['segment'].map(segment_map)

# --- SEGMENTLERİ ANA VERİYLE BİRLEŞTİR ---
df_sample = df_sample.merge(
    features[['credit_score', 'yearly_income', 'total_debt', 'amount', 'segment_label']],
    on=['credit_score', 'yearly_income', 'total_debt', 'amount'],
    how='left'
)

# --- METRİKLERİ HESAPLAYAN FONKSİYON ---
def hesaplamalari_yap():
    toplam_musteri = df_sample.shape[0]
    ort_kredi_limiti = df_sample['credit_limit'].mean()
    ort_gelir = df_sample['yearly_income'].mean()
    ort_borc = df_sample['total_debt'].mean()
    aylik_harcama = df_sample.groupby('txn_month')['amount'].sum().reset_index()
    kart_limiti = df_sample.groupby('card_brand')['credit_limit'].mean().reset_index()
    borc_cinsiyet = df_sample.groupby('gender')['total_debt'].mean().reset_index()

    return {
        "toplam_musteri": toplam_musteri,
        "ort_kredi_limiti": ort_kredi_limiti,
        "ort_gelir": ort_gelir,
        "ort_borc": ort_borc,
        "aylik_harcama_df": aylik_harcama,
        "kart_limiti_df": kart_limiti,
        "borc_cinsiyet_df": borc_cinsiyet
    }

# --- STREAMLIT DASHBOARD ---
st.set_page_config(page_title="Smart Limit Dashboard", layout="wide")
st.title("💳 Smart Limit Müşteri Segmentasyonu Paneli")

sonuclar = hesaplamalari_yap()

col1, col2, col3 = st.columns(3)
col1.metric("Toplam Müşteri", f"{sonuclar['toplam_musteri']:,}")
col2.metric("Ortalama Kredi Limiti", f"{sonuclar['ort_kredi_limiti']:.0f} TL")
col3.metric("Ortalama Gelir", f"{sonuclar['ort_gelir']:.0f} TL")

st.subheader("📊 Ortalama Borç")
st.write(f"{sonuclar['ort_borc']:.0f} TL")

st.subheader("🗓️ Aylık Harcamalar")
st.dataframe(sonuclar["aylik_harcama_df"])

st.subheader("💳 Karta Göre Limit Ortalamaları")
st.dataframe(sonuclar["kart_limiti_df"])

st.subheader("👤 Cinsiyete Göre Borç Ortalamaları")
st.dataframe(sonuclar["borc_cinsiyet_df"])
