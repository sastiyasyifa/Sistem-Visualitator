import pandas as pd
import numpy as np
import os

def Load_data(nama):
    df = []
    for i in nama:
        df_list = pd.read_excel(i, header=0, skiprows=1)  # Baca file Excel
        year = i.split("-")[1]   # setelah '-' pertama
        df_list["Tahun"] = year
        df.append(df_list)

    df = pd.concat(df, ignore_index=True)
    # print(df)
    # Ubah data menjadi format long
    df_long = df.melt(
        id_vars=["Elemen Data", "Tahun"],
        var_name="Bulan",
        value_name="Nilai"
    )

    # Urutkan bulan secara khusus
    bulan_order = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

    df_long["Bulan"] = pd.Categorical(
        df_long["Bulan"], 
        categories=bulan_order, 
        ordered=True
    )

    # Buat pivot table
    df_pivot = df_long.pivot_table(
        index=(["Bulan", "Tahun"]), 
        columns="Elemen Data", 
        values="Nilai"
    ).reset_index()

    df_pivot.dropna(inplace=True)
    return df_pivot