import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import streamlit as st
from statsmodels.tsa.stattools import adfuller
import itertools


def Preprocessing(uploaded_files):
    df = []
    for file in uploaded_files:
        df_list = pd.read_excel(file, header=0, skiprows=1, decimal=",", thousands=".")  
        year = file.name.split("-")[1]  
        df_list["Tahun"] = year
        df.append(df_list)

    df = pd.concat(df, ignore_index=True)

    # Ubah ke long format
    df_long = df.melt(id_vars=["Elemen Data", "Tahun"], 
                    var_name="Bulan", 
                    value_name="Nilai")

    bulan_order = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

    df_long["Bulan"] = pd.Categorical(
        df_long["Bulan"], 
        categories=bulan_order, 
        ordered=True
    )

    df_long["Nilai"] = pd.to_numeric(df_long["Nilai"], errors="coerce")

    df_pivot = df_long.pivot_table(
        index=(["Bulan", "Tahun"]), 
        columns="Elemen Data", 
        values="Nilai")

    df = df_pivot

    return df

def forecast (df, elements, pdq, best_aic, best_model, pilih_periode="Bulan", pilih_grafik="Bar"):
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6,
        "Jul": 7, "Agu": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12
    }
    
    last_bulan, last_tahun = df.index[-1]
    last_date = pd.to_datetime(f"{last_tahun}-{month_map[last_bulan]}-01")

    # Ubah Bulan dan Tahun menjadi datetime index
    df.index = pd.to_datetime(
        df.index.get_level_values("Tahun").astype(str) + "-" +
        df.index.get_level_values("Bulan").map(month_map).astype(str) + "-01"
    )

    # Pilih elemen yang mau diprediksi (misal dari user)
    selected_elements = elements

    # Forecast result container
    df["Periode"] = df.index

    if pilih_periode == "Bulan":
        np.random.seed(42) 
        forecast_dfs = []

        # Pastikan data tidak berubah selama loop
        df_base = df.copy()
        last_date = df_base.index.max()

        for col in selected_elements:
            series = df_base[col].dropna()

            # --- Uji stasioneritas ---
            try:
                pval = adfuller(series)[1]
            except Exception:
                pval = 1.0

            if pval >= 0.05:
                df_used = series.diff().dropna()
                d = 1
            else:
                df_used = series
                d = 0


            best_aic = float("inf")
            best_model = None
            best_order = None

            for order in pdq:
                try:
                    model = ARIMA(df_used, order=(order[0], d, order[2]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
                    fit = model.fit(method_kwargs={"warn_convergence": False})
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_order = (order[0], d, order[2])
                        best_model = fit
                except:
                    continue

            if best_model is not None:
                forecast = best_model.get_forecast(steps=6)
                forecast = forecast.predicted_mean

                # Jika dilakukan differencing, kembalikan ke level asli
                if d == 1:
                    forecast = np.cumsum(forecast) + series.iloc[-1]

                # Hindari nilai negatif
                forecast = np.maximum(forecast, 0)

                temp = pd.DataFrame({
                    "Periode": pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=6, freq="MS"),
                    f"Forecast {col}": forecast
                })
                forecast_dfs.append(temp)

        # --- Gabungkan hasil forecast dari semua kolom ---
        if not forecast_dfs:
            st.warning("Forecast tidak dapat dilakukan karena data kurang memadai.")
            st.stop()
        else:
            forecast_df = forecast_dfs[0]
            for i in range(1, len(forecast_dfs)):
                forecast_df = forecast_df.merge(forecast_dfs[i], on="Periode", sort=False)

            # Gabungkan data aktual dan hasil forecast
            all_df = df_base.reset_index().merge(forecast_df, how="outer", on="Periode")
            print(all_df)
            # --- Plot hasil ---
            y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]

            if pilih_grafik == "Bar":
                fig = px.bar(all_df, x="Periode", y=y_columns,barmode='group',color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')

            elif pilih_grafik == "Line":
                fig = px.line(all_df, x="Periode", y=y_columns,color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')

    
    elif pilih_periode == "Triwulan":
        print("hai")
        np.random.seed(42)  
        forecast_dfs = []

        # Pastikan data tidak berubah selama loop
        df_base = df.copy()
        last_date = df_base.index.max()
        last_date = last_date + pd.offsets.MonthEnd(0)

        for col in selected_elements:
            series = df_base[col].dropna()

            # --- Uji stasioneritas ---
            try:
                pval = adfuller(series)[1]
            except Exception:
                pval = 1.0

            if pval >= 0.05:
                df_used = series.diff().dropna()
                d = 1
            else:
                df_used = series
                d = 0

            best_aic = float("inf")
            best_model = None
            best_order = None

            # Cari best order dulu
            for order in pdq:
                try:
                    model = ARIMA(df_used, order=(order[0], d, order[2]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
                    fit = model.fit(method_kwargs={"warn_convergence": False})
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_order = (order[0], d, order[2])
                        best_model = fit
                except:
                    continue
					
            if best_model is not None:
                forecast = best_model.forecast(steps=4)

                # Jika dilakukan differencing, kembalikan ke level asli
                if d == 1:
                    forecast = np.cumsum(forecast) + series.iloc[-1]

                # Hindari nilai negatif
                forecast = np.maximum(forecast, 0)

                # buat index triwulanan
                periods = pd.date_range(
                    start=last_date + pd.offsets.QuarterEnd(1), 
                    periods=4, 
                    freq="QE"  
                )

                temp = pd.DataFrame({"Periode": periods, f"Forecast {col}": forecast.values})
                forecast_dfs.append(temp)


        if not forecast_dfs: 
            st.warning("Forecast tidak dapat dilakukan karena data kurang memadai.")
            st.stop()
        else:
            # Gabungkan semua hasil forecast
            forecast_df = forecast_dfs[0]
            for i in range(1, len(forecast_dfs)):
                forecast_df = forecast_df.merge(forecast_dfs[i], on="Periode")

            all_df = pd.concat([df_base, forecast_df], axis=0)
    
            # Tambahkan kolom label untuk ditampilkan di grafik
            all_df["Label"] = all_df["Periode"].dt.strftime("%b %Y")

            # Urutkan berdasarkan datetime, bukan string
            all_df = all_df.sort_values("Periode")

            y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]

            if pilih_grafik == "Bar":
                fig = px.bar(all_df, x='Label', y=y_columns, barmode='group', color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')
            elif pilih_grafik == "Line":
                fig = px.line(all_df, x='Label', y=y_columns, color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')

    elif pilih_periode == "Semester":
        np.random.seed(42)  
        forecast_dfs = []

        # Pastikan data tidak berubah selama loop
        df_base = df.copy()
        last_date = df_base.index.max()
        for col in selected_elements:
            series = df_base[col].dropna()

            # --- Uji stasioneritas ---
            try:
                pval = adfuller(series)[1]
            except Exception:
                pval = 1.0

            if pval >= 0.05:
                df_used = series.diff().dropna()
                d = 1
            else:
                df_used = series
                d = 0

            best_aic = float("inf")
            best_model = None
            best_order = None

            # Cari best order dulu
            for order in pdq:
                try:
                    model = ARIMA(df_used, order=(order[0], d, order[2]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
                    fit = model.fit(method_kwargs={"warn_convergence": False})
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_order = (order[0], d, order[2])
                        best_model = fit
                except:
                    continue
            
            if best_model is not None:
                forecast = best_model.forecast(steps=2)

                # Jika dilakukan differencing, kembalikan ke level asli
                if d == 1:
                    forecast = np.cumsum(forecast) + series.iloc[-1]

                forecast = np.maximum(forecast, 0)

                periods = pd.date_range(
                    start=last_date + pd.offsets.MonthBegin(6), 
                    periods=2, 
                    freq="6M"   
                )

                temp = pd.DataFrame({
                    "Periode": periods,  
                    f"Forecast {col}": forecast.values
                })

                forecast_dfs.append(temp)   

        if not forecast_dfs:  
            st.warning("Forecast tidak dapat dilakukan karena data kurang memadai.")
            st.stop()
        else:
            # Gabungkan semua hasil forecast
            forecast_df = forecast_dfs[0]
            for i in range(1, len(forecast_dfs)):
                forecast_df = forecast_df.merge(forecast_dfs[i], on="Periode")

            # Satukan dengan data aktual
            all_df = pd.concat([df, forecast_df], axis=0)

            # Tambahkan kolom label untuk ditampilkan di grafik
            all_df["Label"] = all_df["Periode"].dt.strftime("%b %Y")

            # Urutkan berdasarkan datetime, bukan string
            all_df = all_df.sort_values("Periode")

            if pilih_grafik == "Bar":
                # Plot pakai Label, tapi urutannya ikut datetime
                y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]
                fig = px.bar(all_df, x="Label", y=y_columns, barmode='group', color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')

            elif pilih_grafik == "Line":
                y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]
                fig = px.line(all_df, x="Label", y=y_columns, color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')

    elif pilih_periode == "Tahun":
        np.random.seed(42)  
        forecast_dfs = []

        # Pastikan data tidak berubah selama loop
        df_base = df.copy()
        last_date = df_base.index.max()
        for col in selected_elements:
            series = df_base[col].dropna()

            # --- Uji stasioneritas ---
            try:
                pval = adfuller(series)[1]
            except Exception:
                pval = 1.0

            if pval >= 0.05:
                df_used = series.diff().dropna()
                d = 1
            else:
                df_used = series
                d = 0

            best_aic = float("inf")
            best_model = None
            best_order = None

            # Cari best order dulu
            for order in pdq:
                try:
                    model = ARIMA(df_used, order=(order[0], d, order[2]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
                    fit = model.fit(method_kwargs={"warn_convergence": False})
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_order = (order[0], d, order[2])
                        best_model = fit
                except:
                    continue

            if best_model is not None:
                forecast = best_model.forecast(steps=2)

                # Jika dilakukan differencing, kembalikan ke level asli
                if d == 1:
                    forecast = np.cumsum(forecast) + series.iloc[-1]

                # Hindari nilai negatif
                forecast = np.maximum(forecast, 0)

                # ambil tahun terakhir dari data
                last_year = df["Periode"].max().year  

                # buat index tahunan
                periods = pd.date_range(
                    start=f"{last_year+1}",  # mulai tahun setelah data terakhir
                    periods=2, 
                    freq="YE"                
                )

                # simpan ke dataframe
                temp = pd.DataFrame({
                    "Periode": periods.year,   
                    f"Forecast {col}": forecast.values
                })
                forecast_dfs.append(temp)

        
        if not forecast_dfs:  # True kalau list kosong
            st.warning("Forecast tidak dapat dilakukan karena data kurang memadai.")
            st.stop()
        else:
            # Gabungkan semua hasil forecast
            forecast_df = forecast_dfs[0]
            for i in range(1, len(forecast_dfs)):
                forecast_df = forecast_df.merge(forecast_dfs[i], on="Periode")

            # Satukan dengan data aktual
            df["Periode"] = df["Periode"].dt.year   # ubah agar kolom periode hanya tahun
            all_df = df.reset_index().merge(forecast_df, how="outer", on="Periode")

            if pilih_grafik == "Bar":
                # Plot
                y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]
                fig = px.bar(all_df, x="Periode", y=y_columns, barmode='group', range_color="blue", color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')
                
            elif pilih_grafik == "Line":
                y_columns = selected_elements + [f"Forecast {col}" for col in selected_elements]
                fig = px.line(all_df, x="Periode", y=y_columns, color_discrete_sequence=px.colors.qualitative.G10)
                st.plotly_chart(fig, width='stretch')


def cek_stationeritas(df, pilih_periode, pilih_elemen, df_asli):
    try:
        adf_result = adfuller(df)
        p_value = adf_result[1]

        if p_value < 0.05:
            d_candidates = [0]   # sudah stasioner
        else:
            d_candidates = [1]   # perlu differencing

        # --- cari parameter ARIMA terbaik ---
        p = q = range(0, 4)  

        pdq = list(itertools.product(p, d_candidates, q))

        best_aic = float("inf")
        best_model = None
        best_order = None

        return pdq, best_model, best_aic
    except:
        st.warning("DATA TIDAK MEMADAI UNTUK DILAKUKAN FORECASTING")
        pilih_grafik = st.selectbox(
            "Grafik:", 
            ["Bar","Line"]
        )
        Visualisasi(pilih_grafik, pilih_periode, pilih_elemen, df_asli)

def Visualisasi(pilih_grafik, x_axis, pilih_elemen, df_final):
    if x_axis == "Semester":
        df_final = df_final.reset_index()  # ini penting biar 'Tahun' jadi kolom biasa
        if pilih_grafik == "Bar":
            fig = px.bar(
                df_final, 
                x="Bulan", 
                y=pilih_elemen,
                barmode="group", 
                color_discrete_sequence=px.colors.qualitative.G10,
                title=f"Trend {', '.join(pilih_elemen)} per Bulan", 
                labels={"Nilai": ", ".join(pilih_elemen)}
            )
        elif pilih_grafik == "Line":
            fig = px.line(
                df_final,
                x="Bulan",
                y=pilih_elemen,
                markers=True,
                color_discrete_sequence=px.colors.qualitative.G10,
                title=f"Trend {', '.join(pilih_elemen)} per Bulan",
                labels={"Nilai": ", ".join(pilih_elemen)}
            )

        fig.update_layout(
            title={'x': 0.5, 'xanchor': 'center'}
        )
        st.plotly_chart(fig, width='stretch')
        st.stop()
    elif x_axis == "Triwulan":
        df_final = df_final.reset_index()  # ini penting biar 'Tahun' jadi kolom biasa
        if pilih_grafik == "Bar":
            fig = px.bar(
                df_final, 
                x="Bulan", 
                y=pilih_elemen,
                color_discrete_sequence=px.colors.qualitative.G10,
                barmode="group", 
                title=f"Trend {', '.join(pilih_elemen)} per Bulan", 
                labels={"Nilai": ", ".join(pilih_elemen)}
            )
        elif pilih_grafik == "Line":
            fig = px.line(
                df_final,
                x="Bulan",
                y=pilih_elemen,
                markers=True,
                color_discrete_sequence=px.colors.qualitative.G10,
                title=f"Trend {', '.join(pilih_elemen)} per Bulan",
                labels={"Nilai": ", ".join(pilih_elemen)}
            )

        fig.update_layout(
            title={'x': 0.5, 'xanchor': 'center'}
        )
        st.plotly_chart(fig, width='stretch')
        st.stop()
    else:    
        df_final = df_final.reset_index()  # ini penting biar 'Tahun' jadi kolom biasa
        if pilih_grafik == "Bar":
            fig = px.bar(
                df_final, 
                x=x_axis, 
                y=pilih_elemen,
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.G10,
                title=f"Trend {', '.join(pilih_elemen)} per Bulan", 
                labels={"Nilai": ", ".join(pilih_elemen)}
            )
        elif pilih_grafik == "Line":
            fig = px.line(
                df_final,
                x=x_axis,
                y=pilih_elemen,
                markers=True,
                color_discrete_sequence=px.colors.qualitative.G10,
                title=f"Trend {', '.join(pilih_elemen)} per Bulan",
                labels={"Nilai": ", ".join(pilih_elemen)}
            )

        fig.update_layout(
            title={'x': 0.5, 'xanchor': 'center'}
        )
        st.plotly_chart(fig, width='stretch')
        st.stop()

