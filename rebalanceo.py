import streamlit as st
import pandas as pd

def rebalanceo_inteligente(df, objetivo_productivo_default=0.8):
    st.header("♻️ Asistente de Rebalanceo Inteligente")

    # Limpiar valores
    df = df.copy()
    df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
    df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

    # ✅ Control interactivo: barra editable para porcentaje deseado
    st.subheader("🎯 Objetivo de Capital Productivo")
    objetivo_productivo = st.slider(
        "📊 Porcentaje deseado en inversiones productivas:",
        min_value=0.0,
        max_value=1.0,
        value=objetivo_productivo_default,
        step=0.05,
        format="%.2f"
    )

    # Cálculos
    total = df['Dinero'].sum()
    capital_productivo_actual = df[df['Interes Mensual'] > 0]['Dinero'].sum()
    capital_deseado = total * objetivo_productivo
    diferencia = capital_deseado - capital_productivo_actual

    # KPIs visuales
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Capital Total", f"$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("💼 Capital Productivo Actual", f"$ {capital_productivo_actual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("🎯 Objetivo Productivo", f"$ {capital_deseado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Evaluación
    if diferencia <= 0:
        st.success("✅ Tu portafolio ya cumple o supera el objetivo de capital productivo.")
    else:
        st.warning(f"⚠️ Se recomienda mover aproximadamente $ {diferencia:,.2f} COP hacia inversiones productivas.".replace(",", "X").replace(".", ",").replace("X", "."))

    # Generar sugerencias
    df['Productivo'] = df['Interes Mensual'] > 0
    df['Sugerencia'] = df.apply(
        lambda row: "Mantener" if row['Productivo'] else "Mover capital a inversión productiva", axis=1
    )

    # Tabla con sugerencias
    st.subheader("📋 Sugerencias de Rebalanceo")
    df_resultado = df[['Personas', 'Tipo de inversion', 'Dinero', 'Interes Mensual', 'Sugerencia']].copy()
    df_resultado['Dinero'] = df_resultado['Dinero'].map(lambda x: f"$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_resultado['Interes Mensual'] = df_resultado['Interes Mensual'].map(lambda x: f"$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.dataframe(df_resultado, use_container_width=True)
