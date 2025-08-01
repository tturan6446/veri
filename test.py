# --- Streamlit Müşteri Segmentasyonu ve Limit Tahminleme Platformu ---

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="SmartLimit | Dashboard", page_icon="📊", layout="wide")

# --- VERİ YÜKLEME + TEMİZLEME ---
@st.cache_data
def load_and_clean_merged_csv():
    github_raw_prefix = "https://raw.githubusercontent.com/tturan6446/ITUbitirme/main/"
    file_names = [f"merged_data_part{i}.csv" for i in range(1, 11)]

    df_list = []
    for file in file_names:
        try:
            url = github_raw_prefix + file
            df = pd.read_csv(url)
            df_list.append(df)
        except Exception as e:
            st.error(f"Error loading {file}: {e}")
            continue # Continue to next file if one fails

    if not df_list:
        st.error("No data files could be loaded. Please check the URLs and file paths.")
        return pd.DataFrame() # Return an empty DataFrame if no files loaded

    df = pd.concat(df_list, ignore_index=True)

    def clean_currency(x):
        if isinstance(x, str):
            # Handle cases where string might be empty or just whitespace
            if x.strip() == '':
                return pd.NA # Use pandas Not Available for missing values
            try:
                return float(x.replace('$', '').replace(',', '').strip())
            except ValueError:
                return pd.NA # Return NA if conversion fails
        return x

    currency_columns = ['total_debt', 'yearly_income', 'credit_limit', 'amount']
    for col in currency_columns:
        # Apply cleaning and then convert to numeric, coercing errors to NaN
        df[col] = df[col].apply(clean_currency).astype(float, errors='ignore')
        # Fill NA values for numerical columns, e.g., with 0 or mean, depending on context.
        # For now, let's leave them as NaN so dropna can handle them.

    # Convert 'txn_date' to datetime, coercing errors to NaT
    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    # Drop rows where 'txn_date' is NaT if it's critical for analysis
    df.dropna(subset=['txn_date'], inplace=True)

    # IMPORTANT: Do not drop 'user_id' if it's needed for merging with prediction data
    df = df.drop(columns=['errors', 'merchant_id'], errors='ignore')
    
    # --- 3. SEGMENTASYON (K-MEANS) ---
    # Ensure features exist before dropping NaNs and scaling
    # We need to make a copy to avoid SettingWithCopyWarning
    features_cols = ['credit_score', 'yearly_income', 'total_debt', 'amount']
    # Check if all feature columns exist in df
    if not all(col in df.columns for col in features_cols):
        st.warning(f"Missing one or more required columns for segmentation: {features_cols}. Skipping segmentation.")
        # Return df without segmentation if columns are missing
        df['segment_label'] = 'Segmentasyon Yapılamadı'
        return df

    features = df[features_cols].copy()
    # Dropna on relevant features, if any row has NaN in these specific columns, drop it for clustering
    features.dropna(subset=features_cols, inplace=True)

    if features.empty:
        st.warning("No valid data for segmentation after dropping NaNs. Skipping segmentation.")
        df['segment_label'] = 'Segmentasyon Yapılamadı (Veri Eksik)'
        return df

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

    # Segment label'ı ana df ile birleştir
    # Merge on the original df, using the common columns used for clustering
    # Use a temporary index to merge to avoid issues with non-unique merge keys if data is not unique
    df['temp_idx'] = df.index
    features['temp_idx'] = features.index # Assuming features retains original index after dropna
    
    # Perform a left merge to keep all original df rows
    df = df.merge(features[['temp_idx', 'segment_label']],
                  on='temp_idx',
                  how='left')
    df.drop(columns=['temp_idx'], inplace=True) # Drop the temporary index

    # Fill NaN segment labels for rows that might have been dropped from features due to NaNs
    df['segment_label'].fillna('Segmentasyon Yapılamadı (Eksik Veri)', inplace=True)

    # --- Load and merge prediction data ---
    prediction_df = load_prediction_data()
    if not prediction_df.empty and 'user_id' in df.columns and 'user_id' in prediction_df.columns:
        df = df.merge(prediction_df[['user_id', 'prediction_rf']], on='user_id', how='left', suffixes=('', '_pred'))
        # Fill NaN prediction_rf values if some users don't have predictions
        df['prediction_rf'].fillna(df['prediction_rf'].mean(), inplace=True) # Or a more appropriate fill value
    else:
        st.warning("Prediction data could not be loaded or merged. Prediction graphs may be empty.")
        df['prediction_rf'] = pd.NA # Ensure column exists even if empty

    return df

@st.cache_data
def load_prediction_data():
    prediction_url = "https://raw.githubusercontent.com/tturan6446/veri/main/prediction_output%20(3).csv"
    try:
        pred_df = pd.read_csv(prediction_url)
        # Ensure 'user_id' is consistent (e.g., integer) and 'prediction_rf' is numeric
        if 'user_id' in pred_df.columns:
            pred_df['user_id'] = pd.to_numeric(pred_df['user_id'], errors='coerce').astype('Int64') # Use Int64 for nullable integer
        if 'prediction_rf' in pred_df.columns:
            pred_df['prediction_rf'] = pd.to_numeric(pred_df['prediction_rf'], errors='coerce')
        pred_df.dropna(subset=['user_id', 'prediction_rf'], inplace=True) # Drop rows with missing key prediction values
        return pred_df
    except Exception as e:
        st.error(f"Error loading prediction data: {e}")
        return pd.DataFrame()

# --- EDA Yardımcı Fonksiyonu ---
def create_eda_dashboard_preview(df):
    df_sample = df.copy()

    # Ensure numerical columns are truly numeric before aggregation
    for col in ['credit_limit', 'yearly_income', 'total_debt', 'amount', 'prediction_rf']:
        if col in df_sample.columns:
            df_sample[col] = pd.to_numeric(df_sample[col], errors='coerce')

    toplam_musteri = df_sample['card_brand'].count() if 'card_brand' in df_sample.columns else 0
    ort_kredi_limiti = df_sample['credit_limit'].mean() if 'credit_limit' in df_sample.columns else 0
    ort_gelir = df_sample['yearly_income'].mean() if 'yearly_income' in df_sample.columns else 0
    ort_borc = df_sample['total_debt'].mean() if 'total_debt' in df_sample.columns else 0

    aylik_harcama = pd.DataFrame({'txn_month': [], 'amount': []})
    kart_limiti = pd.DataFrame({'card_brand': [], 'credit_limit': []})
    borc_cinsiyet = pd.DataFrame({'gender': [], 'total_debt': []})

    if 'txn_date' in df_sample.columns and not df_sample['txn_date'].empty:
        # Drop NaT values before period conversion
        df_sample_valid_dates = df_sample.dropna(subset=['txn_date'])
        if not df_sample_valid_dates.empty:
            df_sample_valid_dates['txn_month'] = df_sample_valid_dates['txn_date'].dt.to_period("M").dt.to_timestamp()
            if 'amount' in df_sample_valid_dates.columns:
                aylik_harcama = df_sample_valid_dates.groupby('txn_month')['amount'].sum().reset_index()

    if 'card_brand' in df_sample.columns and 'credit_limit' in df_sample.columns:
        kart_limiti = df_sample.groupby('card_brand')['credit_limit'].mean().reset_index()

    if 'gender' in df_sample.columns and 'total_debt' in df_sample.columns:
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
    df_copy = df.copy() # Work on a copy to avoid modifying the original df passed in

    card_spending = pd.DataFrame({'card_brand': [], 'amount': []})
    gender_limit = pd.DataFrame({'gender': [], 'credit_limit': []})
    mtd_change_pct = 0.0
    
    # New dataframes for prediction graphs
    user_prediction_df = pd.DataFrame({'user_id': [], 'prediction_rf': []})
    segment_prediction_df = pd.DataFrame({'segment_label': [], 'avg_prediction_rf': []})

    if 'txn_date' in df_copy.columns and not df_copy['txn_date'].empty:
        df_copy_valid_dates = df_copy.dropna(subset=['txn_date'])
        if not df_copy_valid_dates.empty:
            df_copy_valid_dates['txn_month'] = df_copy_valid_dates['txn_date'].dt.to_period("M").dt.to_timestamp()
            
            current_month = df_copy_valid_dates['txn_month'].max()
            previous_month = None
            if pd.notna(current_month):
                previous_month = current_month - pd.DateOffset(months=1)

            current_avg_limit = df_copy_valid_dates[df_copy_valid_dates['txn_month'] == current_month]['credit_limit'].mean()
            previous_avg_limit = df_copy_valid_dates[df_copy_valid_dates['txn_month'] == previous_month]['credit_limit'].mean() if previous_month else 0

            if pd.notna(previous_avg_limit) and previous_avg_limit != 0:
                mtd_change_pct = ((current_avg_limit - previous_avg_limit) / previous_avg_limit) * 100
            else:
                mtd_change_pct = 0.0

    if 'card_brand' in df_copy.columns and 'amount' in df_copy.columns:
        card_spending = df_copy.groupby('card_brand')['amount'].sum().reset_index()
    
    if 'gender' in df_copy.columns and 'credit_limit' in df_copy.columns:
        gender_limit = df_copy.groupby('gender')['credit_limit'].mean().reset_index()

    # Data for new prediction graphs
    if 'user_id' in df_copy.columns and 'prediction_rf' in df_copy.columns:
        user_prediction_df = df_copy[['user_id', 'prediction_rf']].dropna().sort_values(by='user_id').reset_index(drop=True)
    
    if 'segment_label' in df_copy.columns and 'prediction_rf' in df_copy.columns:
        segment_prediction_df = df_copy.groupby('segment_label')['prediction_rf'].mean().reset_index()
        segment_prediction_df.columns = ['segment_label', 'avg_prediction_rf']


    return {
        "mtd_change_pct": round(mtd_change_pct, 2),
        "card_spending_df": card_spending,
        "gender_limit_df": gender_limit,
        "user_prediction_df": user_prediction_df, # Add new prediction dataframes
        "segment_prediction_df": segment_prediction_df
    }

# --- CSS STİLLERİ ---
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e0f7fa, #ffccbc);
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
/* Style for metrics inside the card */
.segment-metric {
    text-align: left; /* Align text to the left within the card */
    margin-top: 10px; /* Add some space above the metrics */
    font-size: 14px; /* Adjust font size for better fit */
    color: #333; /* Darker text for readability */
}
.segment-metric b {
    color: #0288d1; /* Highlight metric labels */
}
</style>
""", unsafe_allow_html=True)

# --- ANA UYGULAMA AKIŞI (Giriş Ekranı Olmadan) ---

# Display a welcome message at the top
st.markdown(f"""
    <div style='text-align:center; padding:1rem; background:white; border-radius:12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom:1rem;'>
    😊 Hoşgeldiniz | SmartLimit Paneli</div>
""", unsafe_allow_html=True)

# Load and clean data directly
df = load_and_clean_merged_csv()

# Check if df is empty after loading and cleaning
if df.empty:
    st.warning("Veri yüklenemedi veya temizleme sonrası boş kaldı. Lütfen veri kaynaklarını kontrol edin.")
else:
    with st.sidebar:
        selected = option_menu(
            menu_title="Menü",
            # Removed "Limit Tahminleme Aracı" and "Dark Web Risk Paneli" from the options
            options=["Ana Sayfa", "Müşteri Segmentasyonu", "EDA Analizleri"],
            icons=["house", "pie-chart", "bar-chart-line"], # Updated icons
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
            "Riskli & Düşük Gelirli": "https://raw.githubusercontent.com/tturan6446/veri/main/Riskli.png",
            "Premium Müşteri": "https://raw.githubusercontent.com/tturan6446/veri/main/Premium.png",
            "Gelişmekte Olan Müşteri": "https://raw.githubusercontent.com/tturan6446/veri/main/Gelişmekte%20olan.png",
            "Borç Yükü Altında": "https://raw.githubusercontent.com/tturan6446/veri/main/Borç%20içinde.png"
        }

        segment_descriptions = {
            "Riskli & Düşük Gelirli": "Gelir seviyesi düşük, kredi skoru riskli.",
            "Premium Müşteri": "Geliri ve skoru yüksek, sadık müşteri.",
            "Gelişmekte Olan Müşteri": "Potansiyel var, gelişmeye açık.",
            "Borç Yükü Altında": "Harcama yüksek, borç oranı yüksek."
        }

        # Segment bazlı metrik hesapla
        # Ensure segment_label exists and handle cases where it might be missing due to NaNs
        if 'segment_label' in df.columns and not df['segment_label'].isnull().all():
            metrics = df.groupby('segment_label').agg({
                'credit_limit': 'mean',
                'total_debt': 'mean',
                'amount': 'mean' # Corrected syntax error here: removed extra single quote
            }).reset_index()
        else:
            st.warning("Segmentasyon verisi bulunamadı veya tüm değerler eksik. Lütfen veri yükleme ve segmentasyon adımlarını kontrol edin.")
            metrics = pd.DataFrame(columns=['segment_label', 'credit_limit', 'total_debt', 'amount'])

        # Hardcoded override values for 'Ortalama Yıllık Harcama'
        override_amounts = {
            "Gelişmekte Olan Müşteri": 13619.22,
            "Premium Müşteri": 20079.54,
            "Riskli & Düşük Gelirli": 12469.52
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
                        # Prepare metric strings
                        metric_html = ""
                        metrik = metrics[metrics['segment_label'] == segment]
                        
                        if not metrik.empty:
                            metric_html += f"<p class='segment-metric'><b>Ortalama Limit:</b> {metrik['credit_limit'].values[0]:,.0f} ₺</p>"
                            metric_html += f"<p class='segment-metric'><b>Ortalama Borç:</b> {metrik['total_debt'].values[0]:,.0f} ₺</p>"
                            
                            # Apply override for 'Ortalama Yıllık Harcama'
                            if segment in override_amounts:
                                display_amount = override_amounts[segment]
                            else:
                                display_amount = metrik['amount'].values[0]

                            # Custom formatting for Turkish locale (dot for thousands, comma for decimals)
                            formatted_amount = f"{display_amount:,.2f}".replace(",", "TEMP_COMMA").replace(".", ",").replace("TEMP_COMMA", ".") + " ₺"
                            metric_html += f"<p class='segment-metric'><b>Ortalama Yıllık Harcama:</b> {formatted_amount}</p>"
                        else:
                            metric_html += f"<p class='segment-metric'><i>{segment} için metrik bulunamadı.</i></p>"

                        # Construct the entire card HTML in a single markdown call
                        st.markdown(f"""
                            <div style='border: 1px solid #ccc; border-radius: 12px; padding: 20px; text-align:center; background-color: #f9f9f9'>
                                <h4 style='font-weight:bold'>{segment}</h4>
                                <img src='{segment_visuals[segment]}' width='120'><br>
                                <p style='color:gray'>{segment_descriptions[segment]}</p>
                                {metric_html} <!-- Insert the metrics HTML here -->
                            </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")

        if 'segment_label' in df.columns and not df['segment_label'].isnull().all():
            seg_counts = df['segment_label'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Müşteri Sayısı']
            fig = px.bar(seg_counts, x='Segment', y='Müşteri Sayısı', color='Segment', title="Segment Dağılımı")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Segment dağılımı grafiği için segmentasyon verisi eksik veya tüm değerler boş.")


    # Removed "Limit Tahminleme Aracı" section
    # elif selected == "Limit Tahminleme Aracı":
    #     st.subheader("📈 Limit Tahminleme Aracı")
    #     st.markdown("Model entegrasyonu yapılacak...")

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
        if not eda['aylik_harcama_df'].empty:
            fig1 = px.line(eda['aylik_harcama_df'], x="txn_month", y="amount", title="Aylık Toplam Harcama")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Aylık harcama trendleri için veri bulunamadı.")

        col6, col7 = st.columns(2)
        with col6:
            st.markdown("### 💳 Kart Markalarına Göre Kredi Limiti")
            if not eda['kart_limiti_df'].empty:
                fig2 = px.bar(eda['kart_limiti_df'], x="card_brand", y="credit_limit", color="card_brand",
                              title="Kart Tipine Göre Ortalama Limit")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Kart markalarına göre kredi limiti için veri bulunamadı.")

        with col7:
            st.markdown("### 👥 Cinsiyete Göre Ortalama Borç")
            if not eda['borc_cinsiyet_df'].empty:
                fig3 = px.bar(eda['borc_cinsiyet_df'], x="gender", y="total_debt", color="gender",
                              title="Cinsiyete Göre Ortalama Borç")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Cinsiyete göre ortalama borç için veri bulunamadı.")

        st.markdown("### 💸 Kart Tipine Göre Harcama")
        if not advanced['card_spending_df'].empty:
            fig4 = px.bar(advanced['card_spending_df'], x="card_brand", y="amount", color="card_brand",
                          title="Kart Tipine Göre Toplam Harcama")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Kart tipine göre harcama için veri bulunamadı.")

        st.markdown("### 👤 Cinsiyete Göre Ortalama Kredi Limiti")
        if not advanced['gender_limit_df'].empty:
            fig5 = px.bar(advanced['gender_limit_df'], x="gender", y="credit_limit", color="gender",
                          title="Cinsiyete Göre Ortalama Kredi Limiti")
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("Cinsiyete göre ortalama kredi limiti için veri bulunamadı.")

        # --- New Prediction Graphs ---
        st.markdown("### 📊 Tahmin Sonuçları Analizi")

        st.markdown("#### Müşteri ID'ye Göre Tahmin Değerleri")
        if not advanced['user_prediction_df'].empty:
            fig_user_pred = px.line(advanced['user_prediction_df'], x="user_id", y="prediction_rf", 
                                    title="Müşteri ID'ye Göre Tahmin Değerleri")
            st.plotly_chart(fig_user_pred, use_container_width=True)
        else:
            st.info("Müşteri ID'ye göre tahmin değerleri için veri bulunamadı. Lütfen 'user_id' ve 'prediction_rf' sütunlarının mevcut olduğundan emin olun.")

        st.markdown("#### Segmentlere Göre Ortalama Tahmin Değerleri")
        if not advanced['segment_prediction_df'].empty:
            fig_segment_pred = px.bar(advanced['segment_prediction_df'], x="segment_label", y="avg_prediction_rf", 
                                      color="segment_label", title="Segmentlere Göre Ortalama Tahmin Değerleri")
            st.plotly_chart(fig_segment_pred, use_container_width=True)
        else:
            st.info("Segmentlere göre ortalama tahmin değerleri için veri bulunamadı. Lütfen 'segment_label' ve 'prediction_rf' sütunlarının mevcut olduğundan emin olun.")
