import streamlit as st
from streamlit_option_menu import option_menu

# Sayfa ayarları
st.set_page_config(page_title="NeOBank Dashboard", page_icon="📊", layout="wide")

# Session State ile giriş kontrolü simülasyonu
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# Giriş ekranı
if not st.session_state['authenticated']:
    st.title("📊 NeOBank Reporting System")
    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş Yap")

        if submitted:
            if username == "ozcand" and password == "123":
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre.")

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

    with st.sidebar:
        selected = option_menu(
            menu_title="Menü",
            options=["Ad-Hoc Report", "Prediction Reports", "Fraud Customer", "Riskli Müşteriler"],
            icons=["bar-chart", "graph-up", "exclamation-triangle", "person-x"],
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
