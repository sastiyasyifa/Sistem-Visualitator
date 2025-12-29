import pandas as pd
import streamlit as st


def filter_periode(df, pilih_periode):
    df = df.reset_index()  # kalau index multi, kembalikan dulu ke kolom
    if pilih_periode == "Bulan":
        st.dataframe(df, use_container_width=True)
        print(df)
        return df

    elif pilih_periode == "Triwulan":
        bulan_triwulan = ["Mar", "Jun", "Sep", "Des"]
        bulan_tidak_ada = [b for b in bulan_triwulan if b not in df["Bulan"].unique()]
        if bulan_tidak_ada:
            st.error(f"DATA ANDA TIDAK MEMENUHI PERSYARATAN. Bulan yang hilang: {', '.join(bulan_tidak_ada)}")
            st.stop()
        df = df[df["Bulan"].isin(bulan_triwulan)]
        st.dataframe(df, use_container_width=True)
        return df

    elif pilih_periode == "Semester":
        bulan_semester = ["Jun", "Des"]
        bulan_tidak_ada = [b for b in bulan_semester if b not in df["Bulan"].unique()]
        if bulan_tidak_ada:
            st.error(f"DATA ANDA TIDAK MEMENUHI PERSYARATAN. Bulan yang hilang: {', '.join(bulan_tidak_ada)}")
            st.stop()
        df = df[df["Bulan"].isin(bulan_semester)]
        st.dataframe(df, use_container_width=True)
        return df

    elif pilih_periode == "Tahun":
        # logika rekap tahunmu taruh di sini
        rekap = []
        for tahun, df_group in df.groupby("Tahun"):
            hasil = {"Tahun": tahun}
            for col in df_group.columns:
                if col in ["Bulan", "Tahun"]:
                    continue
                if df_group[col].nunique() <= 2:
                    val_des = df_group.loc[df_group["Bulan"] == "Des", col]
                    hasil[col] = val_des.values[0] if not val_des.empty else df_group[col].iloc[-1]
                else:
                    hasil[col] = df_group[col].sum()
                if col.split()[1] == "Persentase":
                    hasil[col] = df_group[col].mean()
            hasil["Bulan"] = "Des"
            hasil = {"Tahun": hasil["Tahun"], "Bulan": hasil["Bulan"], **{k: v for k, v in hasil.items() if k not in ["Tahun", "Bulan"]}}
            rekap.append(hasil)
        st.dataframe(pd.DataFrame(rekap), use_container_width=True)
        return pd.DataFrame(rekap)
