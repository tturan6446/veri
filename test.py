import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import urllib.parse

# Sayfa ayarları
st.set_page_config(page_title="TTech Data App", layout="wide")

# Özel stil ve fontlar
def add_custom_style():
    st.markdown("""
        <style>
            .main {
                background-color: #f8f9fc;
                font-family: 'Poppins', sans-serif;
            }
            section[data-testid="stSidebar"] {
                background-color: #e9eff6;
                padding: 20px;
            }
            h1, h2, h3, h4 {
                font-family: 'Poppins', sans-serif;
                color: #1f77b4;
            }
            .stButton > button {
                background-color: #1f77b4;
                color: white;
                border-radius: 8px;
                padding: 0.5rem 1rem;
            }
            .stButton > button:hover {
                background-color: #135d91;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

add_custom_style()

# Sidebar menu
with st.sidebar:
    main_selection = option_menu(
        menu_title="TTech Panel",
        options=["Ana Sayfa", "Veri Kazıma", "Veri Görselleştirme", "Veri Tahminleme"],
        icons=["house", "cloud-download", "bar-chart", "activity"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#1f77b4", "font-size": "20px"},
            "nav-link": {"font-size": "18px"},
            "nav-link-selected": {"background-color": "#1f77b4", "color": "white"},
        }
    )

    if main_selection == "Veri Kazıma":
        sub_selection = option_menu(
            menu_title="Alt Menü",
            options=["Fiyat Kazıma", "Web Sitesi Ürün Kazıma", "Veri Kazıma"],
            icons=["tag", "globe", "cloud-upload"],
            menu_icon="none",
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "#f0f2f6"},
                "icon": {"color": "#1f77b4", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "margin":"0px"},
                "nav-link-selected": {"background-color": "#1f77b4", "color": "white"},
            }
        )
    else:
        sub_selection = None

if main_selection == "Ana Sayfa":
    st.title("🏠 TTech Veri Platformuna Hoşgeldiniz")
    st.markdown("""
    Sol menüden bir işlem seçin.
    """)

elif main_selection == "Veri Kazıma" and sub_selection == "Fiyat Kazıma":
    st.title("📥 Fiyat Kazıma")
    urun = st.text_input("🔎 Aramak istediğiniz ürünü yazın", placeholder="Örn: saat")

    if st.button("🔍 Ara"):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0")

        driver = webdriver.Chrome(options=options)

        def scroll_page(driver):
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        tum_veriler = []
        query = urllib.parse.quote_plus(urun)
        base_url = f"https://www.akakce.com/arama/?q={query}"

        for sayfa_no in range(1, 4):
            sayfa_url = f"{base_url}&p={sayfa_no}"
            driver.get(sayfa_url)
            time.sleep(3)
            scroll_page(driver)

            kartlar = driver.find_elements(By.CSS_SELECTOR, "li.w")
            if not kartlar:
                break

            for kart in kartlar:
                try:
                    urun_adi = kart.find_element(By.CSS_SELECTOR, "a.pw_v8").get_attribute("title")
                except:
                    urun_adi = "Ürün adı yok"

                marka = kart.get_attribute("data-mk") or "Marka yok"

                try:
                    teklif_bloklari = kart.find_elements(By.CSS_SELECTOR, "div.p_w_v9")
                    for teklif_blok in teklif_bloklari:
                        satirlar = teklif_blok.find_elements(By.CSS_SELECTOR, "a.iC")

                        for satir in satirlar:
                            try:
                                fiyat_span = satir.find_element(By.CSS_SELECTOR, "span.pt_v8")
                                fiyat = fiyat_span.text.strip()
                            except:
                                fiyat = "Fiyat yok"

                            try:
                                img_tag = satir.find_element(By.TAG_NAME, "img")
                                satici_adi = img_tag.get_attribute("alt") or "Satıcı bilgisi yok"
                                logo_url = img_tag.get_attribute("src") or ""
                            except:
                                satici_adi = "Satıcı bilgisi yok"
                                logo_url = ""

                            tum_veriler.append({
                                "Ürün": urun_adi,
                                "Fiyat": fiyat,
                                "Satıcı": satici_adi,
                                "Marka": marka,
                                "Satıcı Logo": logo_url
                            })
                except:
                    continue

        driver.quit()

        if tum_veriler:
            df = pd.DataFrame(tum_veriler)
            st.success(f"{len(df)} ürün bulundu!")

            grouped = df.groupby(["Ürün", "Marka"])
            for (urun_adi, marka), group in grouped:
                st.subheader(f"📦 {urun_adi} ({marka})")
                st.markdown(
                    group[["Fiyat", "Satıcı", "Satıcı Logo"]].to_html(
                        escape=False,
                        formatters={"Satıcı Logo": lambda x: f'<img src="{x}" width="60">'},
                        index=False
                    ),
                    unsafe_allow_html=True
                )

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV İndir", csv, f"{urun}_akakce.csv")

        else:
            st.warning("Hiç sonuç bulunamadı.")

elif main_selection == "Veri Görselleştirme":
    st.title("📊 Veri Görselleştirme")
    st.info("Bu alan yakında aktif olacak.")

elif main_selection == "Veri Tahminleme":
    st.title("📈 Veri Tahminleme")
    st.info("Bu alan yakında aktif olacak.")
