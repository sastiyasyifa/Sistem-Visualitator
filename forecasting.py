import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import itertools

def forecasting(df, elemen):
    bulan_map = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "Mei": "05", "Jun": "06",
        "Jul": "07", "Agu": "08", "Sep": "09", "Okt": "10", "Nov": "11", "Des": "12"
    }

    # pastikan nama bulan bersih
    df["Bulan"] = df["Bulan"].astype(str).str.strip().map(bulan_map)

    if df["Bulan"].isna().any():
        print("⚠️ Ada bulan yang tidak dikenali:", df["Bulan"].unique())

    # gabungkan Tahun + Bulan jadi datetime
    df["Tanggal"] = pd.to_datetime(df["Tahun"].astype(str) + "-" + df["Bulan"] + "-01")

    # jadikan Tanggal sebagai index
    df.set_index("Tanggal", inplace=True)
    df = df.sort_index()
    series = df[elemen]

    # reindex supaya semua bulan ada
    full_index = pd.date_range(start=series.index.min(), end=series.index.max(), freq="MS")
    series = series.reindex(full_index)
    series = series.fillna(0)

    # --- ARIMA ---
    p = q = range(0, 4)
    pdq = list(itertools.product(p, [0], q))

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

    forecast = fit.forecast(steps=6)

    # data aktual
    actual = series.dropna()

    # forecast index
    forecast_index = pd.date_range(
        start=actual.index[-1] + pd.DateOffset(months=1),
        periods=len(forecast),
        freq='MS'
    )
    forecast_series = pd.Series(forecast, index=forecast_index)

    return actual.index, actual, forecast_series, forecast_series.index


