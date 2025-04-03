from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
from fpdf import FPDF
import time

urun = "ps5"
base_url = f"https://www.akakce.com/{urun}"

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

def verileri_cek(driver):
    kartlar = driver.find_elements(By.CSS_SELECTOR, "li.w")
    data = []

    for kart in kartlar:
        try:
            urun_adi = kart.find_element(By.CSS_SELECTOR, "a.pw_v8").get_attribute("title")
        except:
            urun_adi = "Ürün adı yok"

        fiyat = "Fiyat yok"
        for fiyat_selector in ["span.db_v9", "span.pb_v8", "span.pt_v8", "strong.pt_v8", "div.price"]:
            try:
                fiyat = kart.find_element(By.CSS_SELECTOR, fiyat_selector).text.strip()
                if fiyat:
                    break
            except:
                continue

        marka = kart.get_attribute("data-mk") or "Marka yok"
        satici_adi = kart.get_attribute("data-mn") or "Satıcı yok"

        linkler = kart.find_elements(By.CSS_SELECTOR, "div.p_w_v9 a")
        if linkler:
            for link in linkler:
                satici_url = link.get_attribute("href")
                data.append({
                    "Ürün": urun_adi,
                    "Fiyat": fiyat,
                    "Satıcı": satici_adi,
                    "Marka": marka,
                    "Satıcı Linki": satici_url
                })
        else:
            data.append({
                "Ürün": urun_adi,
                "Fiyat": fiyat,
                "Satıcı": satici_adi,
                "Marka": marka,
                "Satıcı Linki": "-"
            })
    return data

# Sayfayı aşağı kaydırarak tüm ürünleri yükleyelim
def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

# Türkçe karakter desteği için doğru kodlama
def tr_encode(metin):
    return metin.encode('iso-8859-9', 'replace').decode('iso-8859-9')

tum_veriler = []

try:
    for sayfa_no in range(1, 11):  # En fazla 10 sayfa kontrol et
        sayfa_url = f"{base_url},{sayfa_no}.html" if sayfa_no > 1 else f"{base_url}.html"
        print(f"{sayfa_no}. sayfa çekiliyor: {sayfa_url}")

        driver.get(sayfa_url)
        time.sleep(4)

        scroll_page(driver)  # Sayfayı aşağıya kaydırarak tüm verileri yükle
        sayfa_verileri = verileri_cek(driver)

        if not sayfa_verileri:  # Sayfa boşsa döngüyü durdur
            print(f"{sayfa_no}. sayfa boş, döngü durduruldu.")
            break

        tum_veriler.extend(sayfa_verileri)

    df = pd.DataFrame(tum_veriler)
    df.to_csv(f"{urun}_tum_sayfalar.csv", index=False)
    print(f"✅ Toplam {len(df)} ürün başarıyla CSV olarak kaydedildi.")

    # PDF oluşturma
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(200, 10, txt=tr_encode(f"{urun.upper()} Arama Sonuçları"), ln=True, align='C')

    headers = ["Ürün", "Fiyat", "Satıcı", "Marka", "Satıcı Linki"]
    pdf.set_font("Arial", 'B', 8)
    for header in headers:
        pdf.cell(38, 8, tr_encode(header), 1, 0, 'C')
    pdf.ln()

    pdf.set_font("Arial", size=8)
    for index, row in df.iterrows():
        pdf.cell(38, 6, tr_encode(row["Ürün"][:25]), 1)
        pdf.cell(38, 6, tr_encode(row["Fiyat"]), 1)
        pdf.cell(38, 6, tr_encode(row["Satıcı"]), 1)
        pdf.cell(38, 6, tr_encode(row["Marka"]), 1)
        pdf.cell(38, 6, tr_encode(row["Satıcı Linki"][:25]), 1)
        pdf.ln()

    pdf.output(f"{urun}_tum_sayfalar.pdf")
    print(f"📄 Sonuçlar '{urun}_tum_sayfalar.pdf' olarak PDF'e kaydedildi.")

except Exception as e:
    print("Hata:", e)

finally:
    driver.quit()
