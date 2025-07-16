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
            options=["Segment Analizi", "Limit Tahminleme", "Zaman Serisi", "Dark Web Riski", "Model Kıyaslama"],
            icons=["pie-chart", "activity", "clock-history", "shield-exclamation", "bar-chart"],
            menu_icon="grid",
            default_index=0
        )

    if selected == "Segment Analizi":
        st.subheader("📊 Müşteri Segmentasyonu")
        st.write("Segment bazlı özellikleri ve profil analizlerini burada sunabilirsiniz.")

    elif selected == "Limit Tahminleme":
        st.subheader("📊 Kredi Limiti Tahminleme")
        st.write("Model inputlarını alarak kullanıcı bazlı kredi limiti tahminleri yapabilirsiniz.")

    elif selected == "Zaman Serisi":
        st.subheader("⏰ Harcama Zaman Serileri")
        st.write("Aylık veya yıllık harcama davranışlarını analiz edin.")

    elif selected == "Dark Web Riski":
        st.subheader("⚠️ Dark Web Riski")
        st.write("Dark web'de yer alan kartlar ve bu kartlara ait müşteri profillerini listeleyin.")

    elif selected == "Model Kıyaslama":
        st.subheader("📈 Model Performans Karşılaştırması")
        st.write("Regresyon modellerinin hata metriklerini ve başarılarını kıyaslayabilirsiniz.")
