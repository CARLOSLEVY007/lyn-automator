
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="LYN DE MEXICO – Cruce de Archivos", layout="centered")

st.image("assets/logo.png", width=150)
st.title("LYN DE MEXICO – Agente de Cruce Inteligente")
st.markdown("Bienvenido al Agente de Cruce de Archivos de **LYN DE MEXICO**.\nSube los archivos requeridos para generar el reporte de ventas y existencias automatizado.")

archivo_skus = st.file_uploader("1. Cargar archivo SKUS", type="xlsx")
archivo_existencias = st.file_uploader("2. Cargar archivo EXISTENCIAS", type="xlsx")
archivo_ordenado = st.file_uploader("3. Cargar archivo ORDENADO", type="xlsx")
archivo_liverpool = st.file_uploader("4. Cargar archivo VENTAS LIVERPOOL", type="xlsx")
archivo_palacio = st.file_uploader("5. Cargar archivo VENTAS PALACIO", type="xlsx")

if st.button("🚀 Ejecutar Cruce"):
    if not all([archivo_skus, archivo_existencias, archivo_ordenado, archivo_liverpool, archivo_palacio]):
        st.warning("Por favor carga todos los archivos.")
    else:
        df_skus = pd.read_excel(archivo_skus)
        df_existencias = pd.read_excel(archivo_existencias)
        df_ordenado = pd.read_excel(archivo_ordenado)
        df_ventas_liv = pd.read_excel(archivo_liverpool)
        df_ventas_pal = pd.read_excel(archivo_palacio)

        df_skus = df_skus[df_skus['LIVERPOOL '].notna() & df_skus['PALACIO'].notna()].copy()
        df_skus['LIVERPOOL '] = df_skus['LIVERPOOL '].astype(float).astype('Int64').astype(str)
        df_skus['PALACIO'] = df_skus['PALACIO'].astype(float).astype('Int64').astype(str)

        df_existencias = df_existencias.rename(columns={df_existencias.columns[0]: 'CODIGO_EXIST'})
        df_existencias = df_existencias[df_existencias['CODIGO_EXIST'].astype(str).str.isnumeric()]
        df_existencias['CODIGO_EXIST'] = df_existencias['CODIGO_EXIST'].astype(float).astype('Int64').astype(str)
        df_temp1 = df_existencias.iloc[:, [0, 2]].copy()
        df_temp1.columns = ['LIVERPOOL ', 'EXISTENCIAS']
        df_skus = pd.merge(df_skus, df_temp1, how="left", on="LIVERPOOL ")

        df_ordenado = df_ordenado.rename(columns={df_ordenado.columns[0]: 'CODIGO_ORD'})
        df_ordenado = df_ordenado[df_ordenado['CODIGO_ORD'].astype(str).str.isnumeric()]
        df_ordenado['CODIGO_ORD'] = df_ordenado['CODIGO_ORD'].astype(float).astype('Int64').astype(str)
        df_temp2 = df_ordenado.iloc[:, [0, 4]].copy()
        df_temp2.columns = ['LIVERPOOL ', 'ORDENADO']
        df_skus = pd.merge(df_skus, df_temp2, how="left", on="LIVERPOOL ")

        df_ventas_liv = df_ventas_liv[['Artículo', 'vta total 9 meses']].dropna()
        df_ventas_liv.columns = ['CODIGO_LIV', 'VENTAS LIV 9 MESES']
        df_ventas_liv = df_ventas_liv[df_ventas_liv['CODIGO_LIV'].astype(str).str.isnumeric()]
        df_ventas_liv['CODIGO_LIV'] = df_ventas_liv['CODIGO_LIV'].astype(float).astype('Int64').astype(str)
        df_skus = pd.merge(df_skus, df_ventas_liv, how='left', left_on='LIVERPOOL ', right_on='CODIGO_LIV')
        df_skus.drop(columns='CODIGO_LIV', inplace=True)

        df_ventas_pal = df_ventas_pal[['Clave de Artículo', 'Venta Neta en UM']].dropna()
        df_ventas_pal.columns = ['CODIGO_PAL', 'VENTAS PAL 9 MESES']
        df_ventas_pal = df_ventas_pal[df_ventas_pal['CODIGO_PAL'].astype(str).str.isnumeric()]
        df_ventas_pal['CODIGO_PAL'] = df_ventas_pal['CODIGO_PAL'].astype(float).astype('Int64').astype(str)
        df_skus = pd.merge(df_skus, df_ventas_pal, how='left', left_on='PALACIO', right_on='CODIGO_PAL')
        df_skus.drop(columns='CODIGO_PAL', inplace=True)

        buffer = BytesIO()
        df_skus.to_excel(buffer, index=False)
        buffer.seek(0)

        st.success("✅ Cruce completado.")
        st.download_button("📥 Descargar archivo final", data=buffer, file_name="Reporte_LYN.xlsx")
