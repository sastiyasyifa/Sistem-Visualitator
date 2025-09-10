import pandas as pd
import joblib
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
import itertools

def forecasting (df, elemen):
    bulan_map = {
	"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "Mei": "05", "Jun": "06",
	"Jul": "07", "Agu": "08", "Sep": "09", "Okt": "10", "Nov": "11", "Des": "12"
    }
    df["Bulan"] = df["Bulan"].map(bulan_map)
    # gabungkan Tahun + Bulan jadi datetime
    df["Tanggal"] = pd.to_datetime(df["Tahun"].astype(str) + "-" + df["Bulan"].astype(str) + "-01")
    
    # jadikan Tanggal sebagai index
    df.set_index("Tanggal", inplace=True)
    df = df.sort_index()
    
    # Ambil hanya series yang mau diuji
    series = df[elemen]
    print(series.head())

    # Lakukan Augmented Dickey-Fuller Test
    result = adfuller(series)
    for key, value in result[4].items():
        print(f"   {key}: {value}")
    


    p = q = range(0, 4)  # coba nilai 0–3
    pdq = list(itertools.product(p, [0], q))  # d=0 karena sudah stasioner

    best_aic = float("inf")
    best_order = None
    best_model = None

    for order in pdq:
        try:
            model = ARIMA(series, order=order)
            fit = model.fit()
            if fit.aic < best_aic:
                best_aic = fit.aic
                best_order = order
                best_model = fit
        except:
            continue


    model = ARIMA(series, order=best_order)
    fit = model.fit()

    forecast = fit.forecast(steps=6)  # prediksi 6 bulan ke depan

    # --- Data aktual (dari model) ---
    actual = df[elemen]   # ganti 'value' sesuai nama kolom target kamu

    forecast_index = pd.date_range(start=actual.index[-1] + pd.DateOffset(months=1),periods=len(forecast), freq='MS')

    forecast_series = pd.Series(forecast, index=forecast_index)


    return actual.index, actual, forecast_series, forecast_series.index

