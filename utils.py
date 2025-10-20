# utils.py

def clean_df_for_analysis(df):
    """
    Limpia y convierte a numérico las columnas relevantes que vienen en formato 
    de moneda tipo estadounidense ($10,510,000.00) → 10510000.00
    """
    df_cleaned = df.copy()
    cols_to_clean = ['Dinero', 'Interes anual (%)', 'Interes Mensual', 'Ingreso Mensual Necesario']

    for col in cols_to_clean:
        if col in df_cleaned.columns:
            df_cleaned[col] = (
                df_cleaned[col].astype(str)
                .str.replace(r'[\$,]', '', regex=True)
                .astype(float)
            )
    return df_cleaned

def formato_pesos(valor):
    try:
        return "${:,.2f}".format(valor)
    except:
        return valor

def formato_porcentaje(valor):
    try:
        return "{:.2f}%".format(valor)
    except:
        return valor
def formatear_columnas_para_vista(df, columnas):
    df_vista = df.copy()
    for col in columnas:
        if col in df_vista.columns:
            df_vista[col] = df_vista[col].apply(formato_pesos)
    return df_vista
