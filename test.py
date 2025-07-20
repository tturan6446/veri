import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import plotly.express as px

# --- VERİ YÜKLEME VE TEMİZLEME ---
@st.cache_data
def load_data():
    github_raw_prefix = "https://raw.githubusercontent.com/tturan6446/ITUbitirme/main/"
    file_names = [f"merged_data_part{i}.csv" for i in range(1, 11)]
    df_list = [pd.read_csv(github_raw_prefix + file) for file in file_names]
    df = pd.concat(df_list, ignore_index=True)

    def clean_currency(x):
        if isinstance(x, str):
            return float(x.replace('$', '').replace(',', '').strip())
        return x

    for col in ['total_debt', 'yearly_income', 'credit_limit', 'amount']:
        df[col] = df[col].apply(clean_currency)

    df['txn_date'] = pd.to_datetime(df['txn_date'], errors='coerce')
    df = df.drop(columns=['errors', 'merchant_id', 'user_id'], errors='ignore')

    return df

# --- SEGMENTASYON FONKSİYONU ---
def segment_customers(df):
    features = df[['credit_score', 'yearly_income', 'total_debt', 'amount']].dropna()
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

    return df.merge(features[['credit_score', 'yearly_income', 'total_debt', 'amount', 'segment_label']],
                    on=['credit_score', 'yearly_income', 'total_debt', 'amount'],
                    how='left')

# --- MODEL EĞİTİMİ ---
def train_models(df):
    df_model = df.dropna(subset=['credit_score', 'yearly_income', 'total_debt', 'amount', 'credit_limit'])
    X = df_model[['credit_score', 'yearly_income', 'total_debt', 'amount']]
    y = df_model['credit_limit']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results[name] = {
            "model": model,
            "R2 Score": r2_score(y_test, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_test, y_pred))
        }
    return results

# --- UYGULAMA ARAYÜZÜ ---
st.set_page_config(page_title="SmartLimit Dashboard", layout="wide")
st.title("💳 SmartLimit Dashboard")

df = load_data()
df = segment_customers(df)

# --- MENÜ ---
selected = option_menu(
    menu_title=None,
    options=["Segment Dağılımı", "Veri Tablosu", "Limit Tahmini", "Model Karşılaştırma"],
    icons=["pie-chart", "table", "activity", "bar-chart"],
    orientation="horizontal"
)

# --- MENÜYE GÖRE GÖRÜNTÜLE ---
if selected == "Segment Dağılımı":
    st.subheader("📊 Müşteri Segment Dağılımı")
    seg_counts = df['segment_label'].value_counts().reset_index()
    fig = px.pie(seg_counts, names='index', values='segment_label', title="Segmentlere Göre Dağılım")
    st.plotly_chart(fig)

elif selected == "Veri Tablosu":
    st.subheader("🗃️ Veri Tablosu (İlk 50 Satır)")
    st.dataframe(df.head(50))

elif selected == "Limit Tahmini":
    st.subheader("📈 Tahmini Limit Hesaplama")
    col1, col2 = st.columns(2)

    with col1:
        credit_score = st.number_input("Kredi Skoru", min_value=0, max_value=1000, value=650)
        yearly_income = st.number_input("Yıllık Gelir (TL)", min_value=0.0, value=60000.0)

    with col2:
        total_debt = st.number_input("Toplam Borç (TL)", min_value=0.0, value=15000.0)
        amount = st.number_input("Son Harcama (TL)", min_value=0.0, value=500.0)

    input_data = pd.DataFrame({
        'credit_score': [credit_score],
        'yearly_income': [yearly_income],
        'total_debt': [total_debt],
        'amount': [amount]
    })

    results = train_models(df)
    for name, res in results.items():
        prediction = res['model'].predict(input_data)[0]
        st.success(f"✅ {name} ile tahmini limit: {round(prediction):,.0f} TL")

elif selected == "Model Karşılaştırma":
    st.subheader("📊 Model Performans Karşılaştırması")
    results = train_models(df)
    df_results = pd.DataFrame({
        "Model": list(results.keys()),
        "R2 Score": [results[m]["R2 Score"] for m in results],
        "RMSE": [results[m]["RMSE"] for m in results],
    })
    st.dataframe(df_results.style.format({"R2 Score": "{:.2f}", "RMSE": "{:,.0f}"}))
    st.bar_chart(df_results.set_index("Model"))
