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
    df = Load_data(uploaded_files)

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

if len(pilih_elemen) == 1:
    try:
        # coba forecasting
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
                color="Jenis", 
                color_discrete_map={"Aktual":"blue", "Forecast":"red"},  
                barmode="group",
                title=f"Data Aktual vs Forecast ARIMA - {pilih_elemen[0]}"
            )

        elif pilih_grafik == "Line":
            fig = px.line(
                df_plot,
                x="Tanggal",
                y="Nilai",
                color="Jenis",
                color_discrete_map={"Aktual":"blue", "Forecast":"red"},
                markers=True,
                title=f"Data Aktual vs Forecast ARIMA - {pilih_elemen[0]}"
            )

        st.plotly_chart(fig, use_container_width=True)

    except Exception:
        st.warning(f"⚠️ Data '{pilih_elemen[0]}' tidak memenuhi syarat forecasting. Menampilkan data aktual saja.")

        df_plot = pd.DataFrame({
            "Tanggal": df["Bulan"].astype(str) + "-" + df["Tahun"].astype(str),
            "Nilai": df[pilih_elemen[0]],
            "Jenis": "Aktual"
        })

        if pilih_grafik == "Bar":
            fig = px.bar(
                df_plot,
                x="Tanggal",
                y="Nilai",
                color="Jenis",
                barmode="group",
                title=f"Data Aktual - {pilih_elemen[0]}"
            )

        elif pilih_grafik == "Line":
            fig = px.line(
                df_plot,
                x="Tanggal",
                y="Nilai",
                color="Jenis",
                markers=True,
                title=f"Data Aktual - {pilih_elemen[0]}"
            )

        st.plotly_chart(fig, use_container_width=True)

else:
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
            markers=True,
            title=f"Trend {', '.join(pilih_elemen)} per Bulan",
            labels={"Nilai": ", ".join(pilih_elemen)}
        )

    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'}
    )
    st.plotly_chart(fig, use_container_width=True)

