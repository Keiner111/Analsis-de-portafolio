# Módulo de carga de datos

def cargar_datos(ruta):
    import pandas as pd
    return pd.read_excel(ruta)
