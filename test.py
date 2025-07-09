import streamlit as st

# Sayfa yapılandırması
st.set_page_config(page_title="NeoBank Reporting System", page_icon="📊", layout="centered")

# 🎨 Renk Paleti
PRIMARY_COLOR = "#FF6F00"      # NeOBank ana turuncusu
GRADIENT_START = "#FFCC80"     # Açık turuncu
GRADIENT_END = "#FF6F00"       # Koyu turuncu
TEXT_COLOR = "#333333"

# CSS stil kodu
st.markdown(f"""
    <style>
    body {{
        background: linear-gradient(to right, {GRADIENT_START}, {GRADIENT_END});
    }}
    .header {{
        background-color: white;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        border-bottom: 1px solid #eee;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }}
    .header img {{
        height: 40px;
        margin-right: 15px;
    }}
    .header h1 {{
        font-size: 24px;
        color: {TEXT_COLOR};
        margin: 0;
    }}
    .login-box {{
        background-color: white;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        color: {TEXT_COLOR};
        max-width: 420px;
        margin: auto;
        font-family: 'Segoe UI', sans-serif;
    }}
    .title {{
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 1.5rem;
        color: {PRIMARY_COLOR};
    }}
    .stTextInput > div > div > input {{
        background-color: #fff8f0;
        color: #000;
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
    }}
    .footer {{
        text-align: center;
        margin-top: 1rem;
        font-size: 0.9rem;
    }}
    .footer a {{
        color: {PRIMARY_COLOR};
        text-decoration: none;
    }}
    </style>
""", unsafe_allow_html=True)

# --- HEADER alanı ---
with st.container():
    st.markdown(f"""
        <div class="header">
            <img src="https://cdn-icons-png.flaticon.com/512/3178/3178283.png" alt="report icon" />
            <h1>Reportin System</h1>
        </div>
    """, unsafe_allow_html=True)

# --- Giriş Kutusu ---
with st.container():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="title">🧑‍💼 NeOBank | Çalışan Girişi</div>', unsafe_allow_html=True)

    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap", type="primary"):
        if username == "employee" and password == "neobank123":
            st.success("✅ Giriş başarılı! Raporlara yönlendiriliyorsunuz...")
        else:
            st.error("❌ Hatalı kullanıcı adı veya şifre.")

    st.markdown('<p class="footer"><a href="#">Şifremi Unuttum?</a></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
