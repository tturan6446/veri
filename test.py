import streamlit as st
from streamlit_option_menu import option_menu

# Sayfa ayarları
st.set_page_config(page_title="NeOBank Dashboard", page_icon="📊", layout="wide")

# Session State ile giriş kontrolü
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'show_bot' not in st.session_state:
    st.session_state['show_bot'] = False

# CSS stiller
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #ff9800, #ffc107, #ff5722);
        background-size: 400% 400%;
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
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        max-width: 420px;
        margin: auto;
        font-family: 'Segoe UI', sans-serif;
        margin-top: 6rem;
    }
    .login-title {
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        color: #ff6f00;
        margin-bottom: 2rem;
    }
    .stTextInput input {
        background-color: #fff3e0;
        color: #000;
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stButton>button {
        background-color: #ff6f00;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #e65100;
    }
    .chatbot-popup {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        width: 260px;
        z-index: 9999;
        animation: popUp 1s ease forwards;
    }
    @keyframes popUp {
        0% {transform: scale(0.5); opacity: 0;}
        100% {transform: scale(1); opacity: 1;}
    }
    .campaign-card {
        background-color: white;
        border-left: 6px solid #ff6f00;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .campaign-card h3 {
        color: #ff6f00;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Giriş ekranı
if not st.session_state['authenticated']:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 NeOBank | Çalışan Girişi</div>', unsafe_allow_html=True)

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        if username == "ozcand" and password == "123":
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.session_state['show_bot'] = True
            st.rerun()
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre.")
    st.markdown('</div>', unsafe_allow_html=True)

# Menü ve içerik
else:
    st.markdown(
        f"""
        <style>
        .css-18e3th9 {{ padding-top: 0rem; }}
        .welcome-text {{
            font-size: 24px;
            font-weight: 600;
            color: #FF6F00;
            padding: 1rem;
            text-align: center;
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        </style>
        <div class="welcome-text">👋 Hoşgeldiniz {st.session_state['username'].title()}!</div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state['show_bot']:
        st.markdown("""
        <div class="chatbot-popup">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" width="40" style="float:left; margin-right:10px;"/>
            <div style="font-size:15px; font-weight:500;">Merhaba! 👋<br/> Ben senin asistanınım. Kullanım kılavuzum var, seninle paylaşabilirim!</div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state['show_bot'] = False

    with st.sidebar:
        selected = option_menu(
            menu_title="Menü",
            options=["Ad-Hoc Report", "Prediction Reports", "Fraud Customer", "Riskli Müşteriler", "Customer Campaign"],
            icons=["bar-chart", "graph-up", "exclamation-triangle", "person-x", "megaphone"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical"
        )

    if selected == "Ad-Hoc Report":
        st.subheader("📊 Ad-Hoc Report")
        st.info("Burada özelleştirilmiş raporları görebilirsiniz.")

    elif selected == "Prediction Reports":
        st.subheader("📈 Prediction Reports")
        st.success("Burada tahmin modellerine ait sonuçlar yer alacak.")

    elif selected == "Fraud Customer":
        st.subheader("🚨 Fraud Customer")
        st.warning("Şüpheli müşteri aktiviteleri burada listelenecek.")

    elif selected == "Riskli Müşteriler":
        st.subheader("⚠️ Riskli Müşteriler")
        st.error("Risk skoruna göre segmentlenmiş müşteri listesi burada gösterilir.")

    elif selected == "Customer Campaign":
        st.subheader("📢 Customer Campaign")
        st.markdown('<div class="campaign-card">', unsafe_allow_html=True)
        st.markdown("<h3>📩 SMS Kampanyaları</h3>", unsafe_allow_html=True)
        st.write("SMS gönderim geçmişi, zamanlama ve başarı oranları buraya gelecek.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="campaign-card">', unsafe_allow_html=True)
        st.markdown("<h3>📧 Mail Kampanyaları</h3>", unsafe_allow_html=True)
        st.write("Mail açılma oranları, tıklanma metrikleri ve A/B test sonuçları buraya gelecek.")
        st.markdown('</div>', unsafe_allow_html=True)
