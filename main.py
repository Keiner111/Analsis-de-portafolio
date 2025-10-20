
import streamlit as st
from modules.analysis import analizar_portafolio
from modules.upload import cargar_archivo_excel

st.set_page_config(page_title="IA Financiera Keyner Ruiz", layout="wide")
st.title("IA Financiera Keyner Ruiz")

archivo = st.file_uploader("Sube tu archivo Excel del portafolio", type=["xlsx"])
if archivo:
    df = cargar_archivo_excel(archivo)
    analizar_portafolio(df)
