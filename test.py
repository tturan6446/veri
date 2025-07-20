import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# --- 1. VERİ YÜKLEME + TEMİZLEME ---
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

    # --- 2. SEGMENTASYON (K-MEANS) ---
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


# --- 3. ANA UYGULAMA ---
st.set_page_config(page_title="Segmentasyon", layout="wide")
st.title("🧠 Müşteri Segmentasyonu Uygulaması")

df = load_and_clean_merged_csv()

# --- 4. VERİ GÖSTERİMİ ---
st.subheader("Veri Önizlemesi")
st.dataframe(df.head())

# --- 5. SEGMENT GÖRSELLERİ 2x2 KARTLAR ---
segment_visuals = {
    "Riskli & Düşük Gelirli": "https://drive.google.com/uc?id=1kT3tKIpV6TTytr8YoVCOwYJYZM1zKwbW",
    "Premium Müşteri": "https://drive.google.com/uc?id=1N76PFu8QsUlVnB2DRCnScmAjupIn6_au",
    "Gelişmekte Olan Müşteri": "https://drive.google.com/uc?id=1E7NMfP90ufwWq9XCZyN0NZYaf5rTnzQK",
    "Borç Yükü Altında": "https://raw.githubusercontent.com/tturan6446/veri/main/Borc%20ic%CC%87inde.png"
}

st.markdown("## 🎯 Müşteri Segmentasyon Kartları")
cols = st.columns(2)
segment_keys = list(segment_visuals.keys())

for i in range(0, 4, 2):
    with cols[0]:
        st.markdown(f"### **{segment_keys[i]}**")
        st.image(segment_visuals[segment_keys[i]], use_column_width=True)
    with cols[1]:
        st.markdown(f"### **{segment_keys[i+1]}**")
        st.image(segment_visuals[segment_keys[i+1]], use_column_width=True)
