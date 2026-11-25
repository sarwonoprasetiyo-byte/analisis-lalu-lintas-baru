
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Analisis Lalu Lintas",
    page_icon="🚗",
    layout="wide"
)

st.title("Program Analisis Lalu Lintas")
st.write("Aplikasi untuk menghitung jumlah kendaraan.")

st.subheader("Input Data Kendaraan")

sepeda_motor = st.number_input(
    "Jumlah sepeda motor",
    min_value=0,
    value=204
)

kendaraan_ringan = st.number_input(
    "Jumlah kendaraan ringan",
    min_value=0,
    value=82
)

kendaraan_berat = st.number_input(
    "Jumlah kendaraan berat",
    min_value=0,
    value=41
)

total = sepeda_motor + kendaraan_ringan + kendaraan_berat

st.subheader("Hasil Analisis")

st.metric("Total Kendaraan", total)

data = pd.DataFrame({
    "Jenis Kendaraan": [
        "Sepeda Motor",
        "Kendaraan Ringan",
        "Kendaraan Berat"
    ],
    "Jumlah": [
        sepeda_motor,
        kendaraan_ringan,
        kendaraan_berat
    ]
})

st.bar_chart(
    data,
    x="Jenis Kendaraan",
    y="Jumlah"
)

st.dataframe(data, use_container_width=True)
