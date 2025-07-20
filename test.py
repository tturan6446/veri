# --- Streamlit Müşteri Segmentasyonu ve Limit Tahminleme Platformu ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

    st.success(f"✅ Toplam temizlenmiş veri satırı: {len(df)}")
    return df

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
    animation: gradientFlow 12s ease infinite;
}
@keyframes gradientFlow {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
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
.centered-image {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
.centered-image img {
    max-width: 80%;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
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
        st.dataframe(df.head())

    elif selected == "Limit Tahminleme Aracı":
        st.subheader("📈 Limit Tahminleme Aracı")
        st.markdown("Model entegrasyonu yapılacak...")

    elif selected == "EDA Analizleri":
        st.subheader("📊 EDA (Keşifsel Veri Analizi)")

        dimensions = df.select_dtypes(include='object').columns.tolist() + ['txn_date']
        measures = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        selected_dimension = st.multiselect("Dimension (kategorik ya da zaman)", dimensions, default=["card_brand"])
        selected_measure = st.multiselect("Measure (sayısal değer)", measures, default=["amount"])

        chart_type = st.selectbox("Grafik Türü", ["Bar Plot", "Histogram", "Trend Grafiği (Line)"])

        if selected_dimension and selected_measure:
            for dim in selected_dimension:
                for meas in selected_measure:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    if chart_type == "Bar Plot":
                        plot_data = df.groupby(dim)[meas].mean().sort_values(ascending=False)
                        sns.barplot(x=plot_data.index, y=plot_data.values, ax=ax)
                        ax.set_ylabel(f"Ortalama {meas}")
                        ax.set_title(f"{dim} bazında {meas} ortalaması")

                    elif chart_type == "Histogram":
                        sns.histplot(df[meas], bins=30, kde=True, ax=ax)
                        ax.set_title(f"{meas} Histogramı")

                    elif chart_type == "Trend Grafiği (Line)":
                        if dim == "txn_date":
                            time_data = df.groupby(df["txn_date"].dt.to_period("M"))[meas].sum()
                            time_data.index = time_data.index.to_timestamp()
                            sns.lineplot(x=time_data.index, y=time_data.values, ax=ax)
                            ax.set_title(f"Aylık {meas} Değişimi")
                            ax.set_ylabel(meas)
                        else:
                            st.warning("Trend grafiği sadece tarih boyutuyla çalışır.")
                            continue

                    st.pyplot(fig)

    elif selected == "Dark Web Risk Paneli":
        st.subheader("⚠️ Dark Web Risk Paneli")
        st.markdown("Model entegrasyonu yapılacak...")
