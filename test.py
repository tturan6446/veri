
# --- Streamlit Müşteri Segmentasyonu ve Limit Tahminleme Platformu ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu

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

    # --- K-Means Segmentasyon ---
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

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

    df = df.merge(
        features[['credit_score', 'yearly_income', 'total_debt', 'amount', 'segment_label']],
        on=['credit_score', 'yearly_income', 'total_debt', 'amount'],
        how='left'
    )

    return df  # ✅ DOĞRU GİRİNTİDE


# --- EDA Yardımcı Fonksiyonu ---
def create_eda_dashboard_preview(df):
    df_sample = df.copy()

    toplam_musteri = df_sample['card_brand'].count()
    ort_kredi_limiti = df_sample['credit_limit'].mean()
    ort_gelir = df_sample['yearly_income'].mean()
    ort_borc = df_sample['total_debt'].mean()

    df_sample['txn_month'] = df_sample['txn_date'].dt.to_period("M").dt.to_timestamp()
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

# --- Gelişmiş KPI ve Alt Grafikler ---
def generate_advanced_kpi_and_charts(df):
    df['txn_month'] = df['txn_date'].dt.to_period("M").dt.to_timestamp()
    current_month = df['txn_month'].max()
    previous_month = current_month - pd.DateOffset(months=1)

    current_avg_limit = df[df['txn_month'] == current_month]['credit_limit'].mean()
    previous_avg_limit = df[df['txn_month'] == previous_month]['credit_limit'].mean()

    if pd.notna(previous_avg_limit) and previous_avg_limit != 0:
        mtd_change_pct = ((current_avg_limit - previous_avg_limit) / previous_avg_limit) * 100
    else:
        mtd_change_pct = 0.0

    card_spending = df.groupby('card_brand')['amount'].sum().reset_index()
    gender_limit = df.groupby('gender')['credit_limit'].mean().reset_index()

    return {
        "mtd_change_pct": round(mtd_change_pct, 2),
        "card_spending_df": card_spending,
        "gender_limit_df": gender_limit
    }

# --- SESSION KONTROLLERİ ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# --- CSS STİLLERİ ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e0f7fa, #ffccbc);
}
.login-box {
    background-color: white;
    padding: 3rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    max-width: 420px;
    margin: auto;
    font-family: 'Segoe UI', sans-serif;
    margin-top: 6rem;
}
.login-title {
    text-align: center;
    font-size: 26px;
    font-weight: bold;
    color: #0288d1;
    margin-bottom: 2rem;
}
.stTextInput input {
    background-color: #e1f5fe;
    border-radius: 8px;
    padding: 10px;
}
.stButton>button {
    background-color: #0288d1;
    color: white;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #01579b;
}
</style>
""", unsafe_allow_html=True)

# --- GİRİŞ EKRANI ---
if not st.session_state['authenticated']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">SmartLimit Girişi</div>', unsafe_allow_html=True)

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        if username == "tolga" and password == "data123":
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
        <div style='text-align:center; padding:1rem; background:white; border-radius:12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom:1rem;'>
        😊 Hoşgeldiniz <b>{st.session_state['username'].title()}</b> | SmartLimit Paneli</div>
    """, unsafe_allow_html=True)

    df = load_and_clean_merged_csv()

    with st.sidebar:
        selected = option_menu(
            menu_title="Menü",
            options=["Ana Sayfa", "Müşteri Segmentasyonu", "Limit Tahminleme Aracı", "EDA Analizleri", "Dark Web Risk Paneli"],
            icons=["house", "pie-chart", "activity", "bar-chart-line", "shield-exclamation"],
            menu_icon="grid",
            default_index=0
        )

    if selected == "Ana Sayfa":
        st.subheader("📊 Ana Sayfa")
        st.markdown("Uygulama açıklaması ve genel özet bilgiler gelecektir.")

    
    elif selected == "Müşteri Segmentasyonu":
        st.subheader("🧩 Müşteri Segmentasyonu")

        st.markdown("### Müşteri Grupları (K-Means Sonuçlarına Göre)")

        segment_visuals = {
            "Riskli & Düşük Gelirli": "https://drive.google.com/uc?id=1kT3tKIpV6TTytr8YoVCOwYJYZM1zKwbW",
            "Premium Müşteri": "https://drive.google.com/uc?id=1N76PFu8QsUlVnB2DRCnScmAjupIn6_au",
            "Gelişmekte Olan Müşteri": "https://drive.google.com/uc?id=1E7NMfP90ufwWq9XCZyN0NZYaf5rTnzQK",
            "Borç Yükü Altında": "https://github.com/tturan6446/veri/blob/main/Borc%CC%A7%20ic%CC%A7inde.png"
        }

        segment_descriptions = {
            "Riskli & Düşük Gelirli": "Gelir seviyesi düşük, kredi skoru riskli.",
            "Premium Müşteri": "Geliri ve skoru yüksek, sadık müşteri.",
            "Gelişmekte Olan Müşteri": "Potansiyel var, gelişmeye açık.",
            "Borç Yükü Altında": "Harcama yüksek, borç oranı yüksek."
        }

        sorted_segments = [
            "Riskli & Düşük Gelirli",
            "Premium Müşteri",
            "Gelişmekte Olan Müşteri",
            "Borç Yükü Altında"
        ]

        for row in range(2):
            cols = st.columns(2)
            for col_index in range(2):
                i = row * 2 + col_index
                if i < len(sorted_segments):
                    segment = sorted_segments[i]
                    with cols[col_index]:
                        st.markdown(f"#### <div style='text-align:center; font-size:20px; font-weight:bold'>{segment}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center'><img src='{segment_visuals[segment]}' width='160'></div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align:center; color:grey'>{segment_descriptions[segment]}</div>", unsafe_allow_html=True)

        st.markdown("---")

        seg_counts = df['segment_label'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Müşteri Sayısı']
        fig = px.bar(seg_counts, x='Segment', y='Müşteri Sayısı', color='Segment', title="Segment Dağılımı")
        st.plotly_chart(fig, use_container_width=True)

    elif selected == "Limit Tahminleme Aracı":
        st.subheader("📈 Limit Tahminleme Aracı")
        st.markdown("Model entegrasyonu yapılacak...")

    elif selected == "EDA Analizleri":
        st.subheader("📊 EDA (Power BI Dashboard Görünümü)")

        eda = create_eda_dashboard_preview(df)
        advanced = generate_advanced_kpi_and_charts(df)

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Toplam Müşteri", f"{eda['toplam_musteri']:,}")
        col2.metric("Ortalama Kredi Limiti", f"{eda['ort_kredi_limiti']:,.0f} ₺")
        col3.metric("Ortalama Gelir", f"{eda['ort_gelir']:,.0f} ₺")
        col4.metric("Ortalama Borç", f"{eda['ort_borc']:,.0f} ₺")
        col5.metric("MTD Limit Artışı", f"{advanced['mtd_change_pct']}%", delta=f"{advanced['mtd_change_pct']}%")

        st.markdown("### 📈 Aylık Harcama Trendleri")
        fig1 = px.line(eda['aylik_harcama_df'], x="txn_month", y="amount", title="Aylık Toplam Harcama")
        st.plotly_chart(fig1, use_container_width=True)

        col6, col7 = st.columns(2)
        with col6:
            st.markdown("### 💳 Kart Markalarına Göre Kredi Limiti")
            fig2 = px.bar(eda['kart_limiti_df'], x="card_brand", y="credit_limit", color="card_brand",
                          title="Kart Tipine Göre Ortalama Limit")
            st.plotly_chart(fig2, use_container_width=True)

        with col7:
            st.markdown("### 👥 Cinsiyete Göre Ortalama Borç")
            fig3 = px.bar(eda['borc_cinsiyet_df'], x="gender", y="total_debt", color="gender",
                          title="Cinsiyete Göre Ortalama Borç")
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 💸 Kart Tipine Göre Harcama")
        fig4 = px.bar(advanced['card_spending_df'], x="card_brand", y="amount", color="card_brand",
                      title="Kart Tipine Göre Toplam Harcama")
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("### 👤 Cinsiyete Göre Ortalama Kredi Limiti")
        fig5 = px.bar(advanced['gender_limit_df'], x="gender", y="credit_limit", color="gender",
                      title="Cinsiyete Göre Ortalama Kredi Limiti")
        st.plotly_chart(fig5, use_container_width=True)

    elif selected == "Dark Web Risk Paneli":
        st.subheader("⚠️ Dark Web Risk Paneli")
        st.markdown("Model entegrasyonu yapılacak...")
