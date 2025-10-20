import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
import uuid
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de archivos
RUTA_PASIVOS = "pasivos_guardados.xlsx"
BACKUP_DIR = "backups"

def crear_backup_directory():
    """Crear directorio de backups si no existe."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def cargar_pasivos_guardados():
    """Cargar pasivos desde archivo Excel con manejo de errores mejorado."""
    try:
        if os.path.exists(RUTA_PASIVOS):
            df = pd.read_excel(RUTA_PASIVOS)
            
            # Verificar columnas requeridas
            columnas_requeridas = ["Descripcion", "Valor", "Tasa Anual"]
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                st.error(f"Archivo de pasivos corrupto. Columnas faltantes: {columnas_faltantes}")
                return crear_dataframe_pasivos_vacio()
            
            # Agregar ID si no existe
            if 'ID' not in df.columns:
                df['ID'] = [str(uuid.uuid4()) for _ in range(len(df))]
                guardar_pasivos_guardados(df)
            
            # Validar tipos de datos
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            df['Tasa Anual'] = pd.to_numeric(df['Tasa Anual'], errors='coerce').fillna(0)
            
            return df
        else:
            return crear_dataframe_pasivos_vacio()
            
    except Exception as e:
        st.error(f"Error al cargar pasivos: {e}")
        return crear_dataframe_pasivos_vacio()

def crear_dataframe_pasivos_vacio():
    """Crear DataFrame vacío con estructura correcta."""
    return pd.DataFrame(columns=["ID", "Descripcion", "Valor", "Tasa Anual", "Fecha_Creacion"])

def guardar_pasivos_guardados(df_pasivos):
    """Guardar pasivos con backup automático."""
    try:
        # Crear backup antes de guardar
        crear_backup_directory()
        if os.path.exists(RUTA_PASIVOS):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(BACKUP_DIR, f"pasivos_backup_{timestamp}.xlsx")
            df_actual = pd.read_excel(RUTA_PASIVOS)
            df_actual.to_excel(backup_path, index=False)
        
        # Agregar timestamp si no existe
        if 'Fecha_Creacion' not in df_pasivos.columns:
            df_pasivos['Fecha_Creacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar archivo principal
        df_pasivos.to_excel(RUTA_PASIVOS, index=False)
        
    except Exception as e:
        st.error(f"Error al guardar pasivos: {e}")

def eliminar_pasivo(pasivo_id):
    """Eliminar pasivo con confirmación."""
    try:
        df_pasivos = cargar_pasivos_guardados()
        df_pasivos = df_pasivos[df_pasivos['ID'] != pasivo_id].reset_index(drop=True)
        guardar_pasivos_guardados(df_pasivos)
        return True
    except Exception as e:
        st.error(f"Error al eliminar pasivo: {e}")
        return False

def formatear_moneda(valor, simbolo="$", decimales=2):
    """Formatear número como moneda con separadores de miles."""
    if pd.isna(valor) or valor == 0:
        return f"{simbolo} 0,00"
    
    formato = f"{{:,.{decimales}f}}"
    return f"{simbolo} {formato.format(valor)}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_metricas_financieras(df_activos, df_pasivos):
    """Calcular métricas financieras principales."""
    try:
        # Limpiar datos de activos
        df_activos = df_activos.copy()
        df_activos['Dinero'] = pd.to_numeric(df_activos['Dinero'].astype(str).str.replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
        df_activos['Interes Mensual'] = pd.to_numeric(df_activos['Interes Mensual'].astype(str).str.replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
        
        capital_total = df_activos['Dinero'].sum()
        ingreso_pasivo_total = df_activos['Interes Mensual'].sum()
        
        # Calcular métricas de pasivos
        total_pasivos = df_pasivos['Valor'].sum() if not df_pasivos.empty else 0
        intereses_mensuales = ((df_pasivos['Valor'] * df_pasivos['Tasa Anual'] / 100) / 12).sum() if not df_pasivos.empty else 0
        
        # Métricas derivadas
        patrimonio = capital_total - total_pasivos
        porcentaje_pasivos = (total_pasivos / capital_total * 100) if capital_total > 0 else 0
        ratio_cobertura = (ingreso_pasivo_total / intereses_mensuales) if intereses_mensuales > 0 else float('inf')
        flujo_neto = ingreso_pasivo_total - intereses_mensuales
        
        return {
            'capital_total': capital_total,
            'ingreso_pasivo_total': ingreso_pasivo_total,
            'total_pasivos': total_pasivos,
            'intereses_mensuales': intereses_mensuales,
            'patrimonio': patrimonio,
            'porcentaje_pasivos': porcentaje_pasivos,
            'ratio_cobertura': ratio_cobertura,
            'flujo_neto': flujo_neto
        }
    except Exception as e:
        st.error(f"Error al calcular métricas financieras: {e}")
        return {}

def crear_graficos_balance(df_activos, df_pasivos, metricas):
    """Crear gráficos interactivos para el balance."""
    try:
        # Gráfico de distribución de activos
        fig_activos = px.pie(
            values=df_activos.groupby("Tipo de inversion")["Dinero"].sum().values,
            names=df_activos.groupby("Tipo de inversion")["Dinero"].sum().index,
            title="Distribución de Activos por Tipo de Inversión",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_activos.update_traces(textposition='inside', textinfo='percent+label')
        
        # Gráfico de patrimonio vs pasivos
        fig_patrimonio = go.Figure()
        fig_patrimonio.add_trace(go.Bar(
            x=['Activos', 'Pasivos', 'Patrimonio Neto'],
            y=[metricas['capital_total'], metricas['total_pasivos'], metricas['patrimonio']],
            marker_color=['green', 'red', 'blue'],
            text=[formatear_moneda(metricas['capital_total']), 
                  formatear_moneda(metricas['total_pasivos']), 
                  formatear_moneda(metricas['patrimonio'])],
            textposition='auto',
        ))
        fig_patrimonio.update_layout(title="Comparación Financiera", yaxis_title="Valor (COP)")
        
        # Gráfico de flujo de efectivo mensual
        fig_flujo = go.Figure()
        fig_flujo.add_trace(go.Bar(
            x=['Ingresos Pasivos', 'Gastos por Intereses', 'Flujo Neto'],
            y=[metricas['ingreso_pasivo_total'], -metricas['intereses_mensuales'], metricas['flujo_neto']],
            marker_color=['green', 'red', 'blue' if metricas['flujo_neto'] >= 0 else 'orange'],
            text=[formatear_moneda(metricas['ingreso_pasivo_total']), 
                  formatear_moneda(-metricas['intereses_mensuales']), 
                  formatear_moneda(metricas['flujo_neto'])],
            textposition='auto',
        ))
        fig_flujo.update_layout(title="Flujo de Efectivo Mensual", yaxis_title="Valor (COP)")
        
        return fig_activos, fig_patrimonio, fig_flujo
    
    except Exception as e:
        st.error(f"Error al crear gráficos: {e}")
        return None, None, None

def generar_pdf_resumen(df_activos, df_pasivos):
    """Generar PDF del balance general - versión original."""
    now = datetime.now()
    mes_anio = now.strftime("%B %Y").capitalize()
    fecha_completa = now.strftime("%d de %B de %Y").capitalize()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Balance General - {mes_anio}", ln=True, align="C")

    # Fecha del balance
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Fecha del balance: {fecha_completa}", ln=True, align="C")

    # --- Tabla: Resumen por tipo de inversión ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen por Tipo de Inversión", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 8, "Tipo de Inversión", 1)
    pdf.cell(60, 8, "Dinero", 1)
    pdf.cell(60, 8, "Interés Mensual", 1)
    pdf.ln()
    pdf.set_font("Arial", '', 10)
    
    # Agrupar datos para PDF
    resumen_pdf = df_activos.groupby("Tipo de inversion").agg({
        "Dinero": "sum",
        "Interes Mensual": "sum"
    }).reset_index()
    
    for _, row in resumen_pdf.iterrows():
        pdf.cell(60, 8, str(row['Tipo de inversion']), 1)
        pdf.cell(60, 8, f"$ {row['Dinero']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
        pdf.cell(60, 8, f"$ {row['Interes Mensual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
        pdf.ln()

    capital_total = df_activos['Dinero'].sum()
    ingreso_pasivo_total = df_activos['Interes Mensual'].sum()

    # --- Capital e ingreso ---
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, f"Capital Total: $ {capital_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=True)
    pdf.cell(0, 10, f"Ingreso Pasivo Mensual: $ {ingreso_pasivo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=True)

    # --- Tabla: Pasivos registrados ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Pasivos Registrados", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 8, "Descripción", 1)
    pdf.cell(40, 8, "Valor (COP)", 1)
    pdf.cell(30, 8, "Tasa Anual (%)", 1)
    pdf.cell(40, 8, "Pago Mensual Aprox.", 1)
    pdf.ln()

    pdf.set_font("Arial", '', 10)
    for _, row in df_pasivos.iterrows():
        mensual = (row['Valor'] * row['Tasa Anual'] / 12 / 100)
        pdf.cell(80, 8, str(row['Descripcion']), 1)
        pdf.cell(40, 8, f"$ {row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
        pdf.cell(30, 8, f"{row['Tasa Anual']:.2f}%", 1, 0, 'R')
        pdf.cell(40, 8, f"$ {mensual:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."), 1, 0, 'R')
        pdf.ln()

    total_pasivos = df_pasivos['Valor'].sum()
    intereses_mensuales = (df_pasivos['Valor'] * df_pasivos['Tasa Anual'] / 100) / 12
    total_intereses_mensuales = intereses_mensuales.sum()
    patrimonio = capital_total - total_pasivos
    porcentaje_pasivos = (total_pasivos / capital_total * 100) if capital_total > 0 else 0

    # --- Resumen Financiero ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen Financiero", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Total Pasivos: $ {total_pasivos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=True)
    pdf.cell(0, 10, f"Patrimonio Neto: $ {patrimonio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=True)
    pdf.cell(0, 10, f"Pago Mensual de Intereses: $ {total_intereses_mensuales:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), ln=True)
    pdf.cell(0, 10, f"Porcentaje de Pasivos sobre Activos: {porcentaje_pasivos:.2f}%", ln=True)

    # --- Consejos Financieros ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Consejos Financieros", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 10, "- Mantén tus pasivos por debajo del 30% de tus activos.\n"
                              "- Evalúa si puedes reducir la tasa de tus deudas.\n"
                              "- Prefiere activos que generen mayor rentabilidad que tus pasivos.\n"
                              "- Consulta este balance mensual para decisiones estratégicas.")

    output = pdf.output(dest='S')
    pdf_bytes = output.encode('latin-1') if isinstance(output, str) else bytes(output)
    return pdf_bytes

def mostrar_balance_general(df):
    """Función principal para mostrar el balance general."""
    st.header("📊 Balance General del Portafolio")
    
    try:
        # Preparar datos de activos
        df_clean = df.copy()
        df_clean['Dinero'] = pd.to_numeric(df_clean['Dinero'].astype(str).str.replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
        df_clean['Interes Mensual'] = pd.to_numeric(df_clean['Interes Mensual'].astype(str).str.replace(r'[\$,]', '', regex=True), errors='coerce').fillna(0)
        
        # Cargar datos de pasivos
        df_pasivos = cargar_pasivos_guardados()
        
        # Calcular métricas básicas
        capital_total = df_clean['Dinero'].sum()
        ingreso_pasivo_total = df_clean['Interes Mensual'].sum()
        total_pasivos = df_pasivos['Valor'].sum() if not df_pasivos.empty else 0
        intereses_mensuales = ((df_pasivos['Valor'] * df_pasivos['Tasa Anual'] / 100) / 12).sum() if not df_pasivos.empty else 0
        patrimonio = capital_total - total_pasivos
        porcentaje_pasivos = (total_pasivos / capital_total * 100) if capital_total > 0 else 0

        # --- SECCIÓN 1: MÉTRICAS PRINCIPALES ---
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Capital Total", formatear_moneda(capital_total))
        
        with col2:
            st.metric("📈 Ingreso Pasivo Mensual", formatear_moneda(ingreso_pasivo_total))
        
        with col3:
            st.metric("💎 Patrimonio Neto", formatear_moneda(patrimonio))
        
        with col4:
            color = "inverse" if porcentaje_pasivos > 30 else "normal"
            delta_msg = "🔴 Riesgo alto" if porcentaje_pasivos > 30 else "🟢 Saludable"
            st.metric(
                "Porcentaje Pasivos/Activos",
                f"{porcentaje_pasivos:.2f}%",
                delta=delta_msg,
                delta_color=color
            )

        # --- SECCIÓN 2: RESUMEN POR TIPO DE INVERSIÓN ---
        st.subheader("📊 Resumen por Tipo de Inversión")
        
        resumen = df_clean.groupby("Tipo de inversion").agg({
            "Dinero": "sum",
            "Interes Mensual": "sum"
        }).reset_index()
        
        resumen["Tasa Promedio (%)"] = (resumen["Interes Mensual"] / resumen["Dinero"]) * 100
        resumen = resumen.sort_values(by="Dinero", ascending=False)
        
        st.dataframe(resumen, use_container_width=True)

        # --- SECCIÓN 3: GESTIÓN DE PASIVOS ---
        st.subheader("📉 Pasivos Registrados")
        
        # Mostrar pasivos existentes
        if not df_pasivos.empty:
            for i, row in df_pasivos.iterrows():
                col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
                col1.markdown(f"**{row['Descripcion']}** - {formatear_moneda(row['Valor'])}")
                col2.markdown(f"Tasa Anual: {row['Tasa Anual']}%")
                col3.markdown(f"Mensual aprox: {formatear_moneda((row['Valor'] * row['Tasa Anual'] / 12 / 100))}")
                if col4.button("❌", key=f"del_{row['ID']}"):
                    if eliminar_pasivo(row['ID']):
                        st.success("Pasivo eliminado correctamente.")
                        st.rerun()
        else:
            st.info("No hay pasivos guardados todavía.")

        # --- SECCIÓN 4: AGREGAR NUEVO PASIVO ---
        with st.expander("➕ Agregar nuevo pasivo"):
            with st.form("form_pasivo"):
                descripcion = st.text_input("Descripción del pasivo")
                valor = st.number_input("Valor del pasivo (COP)", min_value=0.0, step=100000.0, format="%.2f")
                tasa = st.number_input("Tasa de interés anual (%)", min_value=0.0, step=0.1, format="%.2f")
                enviar = st.form_submit_button("Guardar")

            if enviar and descripcion and valor > 0:
                new_id = str(uuid.uuid4())
                nuevo = pd.DataFrame([[new_id, descripcion, valor, tasa]], columns=["ID", "Descripcion", "Valor", "Tasa Anual"])
                df_pasivos = pd.concat([df_pasivos, nuevo], ignore_index=True)
                guardar_pasivos_guardados(df_pasivos)
                st.success("✅ Pasivo guardado correctamente.")
                st.rerun()
            elif enviar:
                st.warning("Por favor, introduce una descripción y un valor válido para el pasivo.")

        # --- SECCIÓN 5: RESUMEN FINANCIERO ---
        st.subheader("📌 Resumen Financiero")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Pasivos", 
                formatear_moneda(total_pasivos),
                help="Suma total de tus deudas. Idealmente no debería superar el 30% de tus activos totales."
            )
            st.metric(
                "Patrimonio Neto", 
                formatear_moneda(patrimonio),
                help="Diferencia entre tus activos y pasivos. A mayor patrimonio, mejor salud financiera."
            )
        
        with col2:
            st.metric(
                "Pago Mensual de Intereses", 
                formatear_moneda(intereses_mensuales),
                help="Monto que pagas mensualmente por intereses. Considera refinanciar si es muy alto."
            )

        # --- SECCIÓN 6: GRÁFICOS (OPCIONAL) ---
        if st.checkbox("📊 Mostrar gráficos avanzados"):
            # Gráfico de distribución de activos
            if not df_clean.empty:
                fig_activos = px.pie(
                    values=df_clean.groupby("Tipo de inversion")["Dinero"].sum().values,
                    names=df_clean.groupby("Tipo de inversion")["Dinero"].sum().index,
                    title="Distribución de Activos por Tipo de Inversión",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_activos.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_activos, use_container_width=True)

        # --- SECCIÓN 7: DESCARGA DE PDF ---
        if not df_pasivos.empty:
            st.write("---")
            st.subheader("📄 Descargar Balance General en PDF")
            pdf_bytes = generar_pdf_resumen(df_clean, df_pasivos)
            now = datetime.now()
            nombre_archivo = f"Balance General - {now.strftime('%B %Y').capitalize()}.pdf"
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_bytes,
                file_name=nombre_archivo,
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error general en el balance: {e}")
        st.error("Por favor, verifica que tu archivo de portafolio tenga el formato correcto.")

# Inicializar session state
if 'show_form' not in st.session_state:
    st.session_state.show_form = False