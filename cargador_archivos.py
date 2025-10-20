# Módulo de carga de excel

# cargador_archivos.py

import streamlit as st
import pandas as pd

def cargar_datos():
    # Aceptar ambos tipos de archivos Excel: .xls (antiguo) y .xlsx (moderno)
    archivo = st.file_uploader("Sube tu archivo Excel (.xls o .xlsx)", type=["xls", "xlsx"])
    if archivo is not None:
        try:
            # Determinar el motor de lectura basado en la extensión del archivo
            if archivo.name.endswith('.xls'):
                # Para archivos .xls, se recomienda el motor 'xlrd'.
                # Si 'xlrd' no está instalado, pandas lo indicará.
                df = pd.read_excel(archivo, engine='xlrd')
            elif archivo.name.endswith('.xlsx'):
                # Para archivos .xlsx, el motor por defecto o 'openpyxl' es adecuado.
                # 'openpyxl' también puede leer .xls en algunas versiones, pero es mejor ser explícito.
                df = pd.read_excel(archivo, engine='openpyxl')
            else:
                st.error("Formato de archivo no soportado. Por favor, sube un archivo .xls o .xlsx.")
                return None
            
            st.success("Archivo cargado correctamente.")
            return df
        except ImportError as ie:
            st.error(f"Error: Falta una librería para leer el archivo. Para archivos .xls, por favor instala 'xlrd' (`pip install xlrd`). Para .xlsx, instala 'openpyxl' (`pip install openpyxl`). Detalle: {ie}")
            return None
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}. Asegúrate de que el formato sea correcto y que las columnas estén bien.")
            return None
    return None