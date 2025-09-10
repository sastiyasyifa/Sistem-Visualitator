from fileinput import filename
from unicodedata import name
import pandas as pd
import plotly.express as px
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
from Gabungkan_data import Load_data
from forecasting import forecasting


st.set_page_config(page_title="Simple Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("📊 Satu Data Dashboard")

# Upload beberapa file
filenames = []
uploaded_files = st.file_uploader("Upload Excel file", accept_multiple_files=True)
print(uploaded_files)

if not uploaded_files:
    st.info(" Upload file anda di atas", icon="ℹ️")
    st.stop()
else:
    for i in range(len(uploaded_files)):
        filenames.append(uploaded_files[i].name)
    df = Load_data(filenames)

st.dataframe(df, use_container_width=True)

# --- Pilihan Dropdown ---
pilih_elemen = st.multiselect(
    "Sumbu Y:", 
    df.columns[2:].unique(),
    default=[df.columns[2]]
)

# --- Tabel ---
st.subheader("GRAFIK")
pilih_grafik = st.selectbox(
    "Grafik:", 
    ["Bar","Line"]
)

if len(pilih_elemen) == 1 :
    actual_index, actual_values, forecast_values, forecast_index = forecasting(df, pilih_elemen[0])
    df_actual = pd.DataFrame({
    "Tanggal": actual_index,
    "Nilai": actual_values,
    "Jenis": "Aktual"
})

    df_forecast = pd.DataFrame({
        "Tanggal": forecast_index,
        "Nilai": forecast_values,
        "Jenis": "Forecast"
    })

    # gabungkan
    df_plot = pd.concat([df_actual, df_forecast])
    
    if pilih_grafik == "Bar":
        fig = px.bar(
            df_plot,
            x="Tanggal",
            y="Nilai",
            color="Jenis", color_discrete_map={"Aktual":"red", "Forecast":"blue"},  
            barmode="group",   # di sini nggak masalah, karena bulan forecast beda
            title=f"Data Aktual vs Forecast ARIMA - {pilih_elemen[0]}"
        )  

    elif pilih_grafik == "Line":
        fig = px.line(
            df,
            x="Tanggal",
            y=[pilih_elemen[0], "Forecast"],   # tampilkan data aktual dan forecast
            markers=True, 
            title=f"Data Aktual vs Forecast ARIMA - {pilih_elemen[0]}",
            labels={"value": "Nilai", "variable": "Jenis Data"}
        )

    st.plotly_chart(fig, use_container_width=True)

else : 
    if pilih_grafik == "Bar":
        fig = px.bar(
            df, 
            x="Bulan", 
            y=pilih_elemen,
            barmode="group", 
            title=f"Trend {', '.join(pilih_elemen)} per Bulan", 
            labels={"Nilai": ", ".join(pilih_elemen)}
    )

        
    elif pilih_grafik == "Line":
        fig = px.line(
            df,
            x="Bulan",
            y=pilih_elemen,
            markers=True,   # biar ada titik tiap periode
            title=f"Trend {', '.join(pilih_elemen)} per Bulan",
            labels={"Nilai": ", ".join(pilih_elemen)}
    )

    fig.update_layout(
    title={
        'x': 0.5,        # 0 = kiri, 0.5 = tengah, 1 = kanan
        'xanchor': 'center'
    }
    )
    st.plotly_chart(fig, use_container_width=True)

# # --- Forecasting ---
# forecast_horizon = 6  # jumlah periode ke depan

# # Ambil 1 elemen saja untuk forecasting (karena ARIMA butuh 1 time series)
# if len(pilih_elemen) == 1:
#     ts = filtered.set_index(mode)["Nilai"]

#     # Fit ARIMA sederhana (order bisa diatur sesuai kebutuhan)
#     model = ARIMA(ts, order=(1,1,1))
#     model_fit = model.fit()

#     # Forecast
#     forecast = model_fit.forecast(steps=forecast_horizon)

#     # Gabungkan dengan data aktual
#     forecast_df = pd.DataFrame({
#         mode: range(len(ts), len(ts) + forecast_horizon),
#         "Nilai": forecast,
#         "Elemen Data": f"Forecast {pilih_elemen[0]}"
#     })

#     # Tambahkan ke data untuk plot
#     filtered = pd.concat([filtered, forecast_df])
