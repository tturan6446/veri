
# --- Streamlit SmartLimit Dashboard ---
import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- Currency temizleyici fonksiyon ---
def clean_currency(x):
    if isinstance(x, str):
        return float(x.replace('$', '').replace(',', '').strip())
    return x

# --- Veri yükleme ve temizleme ---
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

    currency_columns = ['total_debt', 'yearly_income', 'credit_limit', 'amount']
    for col in currency_columns:
        df[col] = df[col].apply(clean_currency)

    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    df['txn_month'] = df['txn_date'].dt.to_period('M').astype(str)
    df.drop(columns=['errors', 'merchant_id', 'user_id'], errors='ignore', inplace=True)
    return df

df = load_and_clean_merged_csv()

# --- Segmentasyon (KMeans) ---
features = df[['credit_score', 'yearly_income', 'total_debt', 'amount']].dropna()
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

# --- Özet metrikleri hesapla ---
def hesaplamalari_yap():
    toplam_musteri = df.shape[0]
    ort_kredi_limiti = df['credit_limit'].mean()
    ort_gelir = df['yearly_income'].mean()
    ort_borc = df['total_debt'].mean()
    aylik_harcama = df.groupby('txn_month')['amount'].sum().reset_index()
    kart_limiti = df.groupby('card_brand')['credit_limit'].mean().reset_index()
    borc_cinsiyet = df.groupby('gender')['total_debt'].mean().reset_index()
    return {
        "toplam_musteri": toplam_musteri,
        "ort_kredi_limiti": ort_kredi_limiti,
        "ort_gelir": ort_gelir,
        "ort_borc": ort_borc,
        "aylik_harcama_df": aylik_harcama,
        "kart_limiti_df": kart_limiti,
        "borc_cinsiyet_df": borc_cinsiyet
    }

# --- Streamlit UI ---
st.set_page_config(page_title="SmartLimit", layout="wide")
st.title("SmartLimit Segmentasyon ve Kredi Limit Paneli")

sonuclar = hesaplamalari_yap()
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Müşteri", f"{sonuclar['toplam_musteri']:,}")
col2.metric("Ortalama Limit", f"{sonuclar['ort_kredi_limiti']:.0f} TL")
col3.metric("Ortalama Gelir", f"{sonuclar['ort_gelir']:.0f} TL")

st.subheader("Borç Ortalaması")
st.write(f"{sonuclar['ort_borc']:.0f} TL")

st.subheader("Aylık Harcama")
st.dataframe(sonuclar["aylik_harcama_df"])

st.subheader("Kart Limiti")
st.dataframe(sonuclar["kart_limiti_df"])

st.subheader("Borç / Cinsiyet")
st.dataframe(sonuclar["borc_cinsiyet_df"])
