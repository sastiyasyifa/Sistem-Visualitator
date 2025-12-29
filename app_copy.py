import streamlit as st
from forecasting import Preprocessing, forecast, cek_stationeritas
from Gabungkan_data import filter_periode

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

st.set_page_config(page_title="Simple Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("📊 Satu Data Dashboard")

with open("template_file_satudata.xlsx", "rb") as file:
    file_data = file.read()

# Tombol download
st.download_button(
    label="📥 Download Template Excel Satu Data",
    data=file_data,
    file_name="template_file_satudata.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Upload beberapa file
filenames = []
uploaded_files = st.file_uploader("Upload Excel file", accept_multiple_files=True)

# Membaca file di kode yang berbeda
if not uploaded_files:
    st.info(" Upload file anda di atas, sesuaikan dengan template file satu data", icon="ℹ️")
    st.stop()
else:
    df = Preprocessing(uploaded_files)

# inisiasi Default Selctbox
default_value = "Bulan"
opsi = ["Bulan", "Triwulan", "Semester", "Tahun"]

# Memilih Periode waktu yang akan ditampilkan
pilih_periode = st.selectbox(
    "Tampilkan Berdasarkan:",
    opsi,
    index=opsi.index(default_value)
)
# # Menampilkan Data
df = filter_periode(df, pilih_periode)

# Buat pivot table, dari kode ini, untuk nilai yang kosong tidak akan ditampilkan/secara otomatis dihapus
df = df.set_index(["Bulan", "Tahun"])

# Memilih Elemen yang akan dilakukan visualisasi
pilih_elemen = st.multiselect(
    "Pilih Elemen:", 
    df.columns.unique(),
    default=[df.columns[0]]
)

for col in pilih_elemen:
    pdq, best_model, best_aic = cek_stationeritas(df[col], pilih_periode, pilih_elemen, df)

# --- Tabel ---
st.subheader("GRAFIK")
pilih_grafik = st.selectbox(
    "Pilih Tipe Grafik:",
    ["Bar","Line"]
)

try:
    df = forecast(df, pilih_elemen, pdq, best_aic, best_model, pilih_periode, pilih_grafik)
except:
    st.stop()




