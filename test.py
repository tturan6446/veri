# --- Streamlit Müşteri Segmentasyonu ve Limit Tahminleme Platformu ---

import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="SmartLimit | Dashboard", page_icon="📊", layout="wide")

# Session kontrolü
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# CSS
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

# Giriş ekranı
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
        st.markdown("""
        - Genel istatistik özetleri (toplam müşteri, ortalama kredi limiti vb.)
        - Hızlı grafik: Segment dağılımı, kart tipi dağılımı
        - Kısa özet: Uygulamanın amacı ve yetenekleri
        """)
        st.markdown("""
        <div class="centered-image">
            <img src="https://images.ctfassets.net/3viuren4us1n/5DhTy3R6WNBbDZYMDQNCuo/ebc5e9d6e4a67ef9c7bb1f5cee176a6e/digital-transformation-banking-pioneer.jpg" alt="banking dashboard" />
        </div>
        """, unsafe_allow_html=True)

    elif selected == "Müşteri Segmentasyonu":
        st.subheader("🧩 Müşteri Segmentasyonu")
        st.markdown("""
        - K-Means ile segment ayrımı (PCA ile görselleştirme)
        - Her segmentin profil özeti (ortalama gelir, borç, skor)
        - Kart türü ve harcama davranışına göre analiz
        """)

    elif selected == "Limit Tahminleme Aracı":
        st.subheader("📈 Limit Tahminleme Aracı")
        st.markdown("""
        - Kullanıcıdan giriş al (gelir, borç, skor vb.)
        - Eğitimli modelle kredi limiti tahmini
        - Sonuç + model doğruluk metrikleri (MAPE, RMSE)
        """)

    elif selected == "EDA Analizleri":
        st.subheader("📊 EDA (Keşifsel Veri Analizi)")
        st.markdown("""
        - Kategorik/sayısal değişken dağılımları
        - Korelasyon matrisi, boxplotlar, outlier analizi
        - Zaman serisi harcama analizi
        """)

    elif selected == "Dark Web Risk Paneli":
        st.subheader("⚠️ Dark Web Risk Paneli")
        st.markdown("""
        - Dark web'de görülen kartların kullanıcı profili
        - Riskli kullanıcılar listesi ve skor bazlı sıralama
        - Segmentlere göre risk analizi
        """)
