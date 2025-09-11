import pandas as pd
import numpy as np
import os

def Load_data(files):
    df_all = []

    for f in files:
        # baca langsung dari file upload
        df_list = pd.read_excel(f, header=0, skiprows=1)

        # ambil nama file untuk tahun
        year = f.name.split("-")[1]
        df_list["Tahun"] = year

        df_all.append(df_list)

    # gabungkan semua file
    df = pd.concat(df_all, ignore_index=True)

    # ubah format long
    df_long = df.melt(
        id_vars=["Elemen Data", "Tahun"],
        var_name="Bulan",
        value_name="Nilai"
    )

    # urutkan bulan
    bulan_order = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", 
                   "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

    df_long["Bulan"] = pd.Categorical(df_long["Bulan"], 
                                      categories=bulan_order, 
                                      ordered=True)

    # buat pivot table
    df_pivot = df_long.pivot_table(
        index=["Bulan", "Tahun"],
        columns="Elemen Data",
        values="Nilai"
    ).reset_index()

    df_pivot.dropna(inplace=True)
    return df_pivot
