import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    clean_df_for_analysis,
    formato_pesos,
    formato_porcentaje,
    formatear_columnas_para_vista,
)

def mostrar_dashboard_interactivo(df):
    df_cleaned = clean_df_for_analysis(df)
    df_mostrar = df_cleaned.copy()

    # --- Estilo CSS mejorado con modo oscuro y animaciones ---
    st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(102, 126, 234, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.8)); }
    }
    
    .filter-section {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-card {
        border-radius: 25px;
        padding: 35px 25px;
        color: white;
        animation: slideUp 0.8s ease-out;
        font-weight: bold;
        text-align: center;
        min-width: 220px;
        min-height: 180px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        font-size: 18px;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.7s;
    }
    
    .kpi-card:hover::before {
        left: 100%;
    }
    
    .kpi-grid {
        display: flex;
        gap: 25px;
        justify-content: center;
        flex-wrap: wrap;
        margin: 40px 0;
    }
    
    .card-1 { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: relative;
    }
    .card-2 { 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .card-3 { 
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .card-4 { 
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    @keyframes slideUp {
        from {opacity: 0; transform: translateY(50px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    .metric-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-top: 10px;
    }
    
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 600;
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.02);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 30px 0 20px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- T¨ªtulo principal mejorado ---
    st.markdown('<h1 class="main-title">Dashboard de Inversiones</h1>', unsafe_allow_html=True)

    # --- Filtros originales ---
    st.markdown("### Filtros")

    personas = df_mostrar['Personas'].dropna().unique()
    tipos_inversion = df_mostrar['Tipo de inversion'].dropna().unique()

    st.markdown("**Filtrar por Persona**")
    col_pers = st.columns(len(personas))
    seleccion_personas = [p for i, p in enumerate(personas) if col_pers[i].checkbox(p, key=f"pers_{p}", value=False)]

    st.markdown("**Filtrar por Tipo de Inversion**")
    col_tipo = st.columns(len(tipos_inversion))
    seleccion_tipos = [t for i, t in enumerate(tipos_inversion) if col_tipo[i].checkbox(t, key=f"tipo_{t}", value=False)]

    st.divider()

    # Aplicar filtros
    df_filtrado = df_mostrar.copy()
    if seleccion_personas:
        df_filtrado = df_filtrado[df_filtrado['Personas'].isin(seleccion_personas)]
    if seleccion_tipos:
        df_filtrado = df_filtrado[df_filtrado['Tipo de inversion'].isin(seleccion_tipos)]

    # --- KPIs con dise?o ultra moderno ---
    total = df_filtrado['Dinero'].sum()
    ingreso = df_filtrado['Interes Mensual'].sum()
    rentabilidad = (ingreso * 12 / total * 100) if total > 0 else 0
    porcentaje_total = df_filtrado['Porcentaje'].sum() * 100 if 'Porcentaje' in df_filtrado.columns else 0

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card card-1">
            <div class="metric-icon">$</div>
            <div class="metric-label">Capital Total</div>
            <div class="metric-value">{formato_pesos(total)}</div>
        </div>
        <div class="kpi-card card-2">
            <div class="metric-icon">+</div>
            <div class="metric-label">Ingreso Mensual</div>
            <div class="metric-value">{formato_pesos(ingreso)}</div>
        </div>
        <div class="kpi-card card-3">
            <div class="metric-icon">%</div>
            <div class="metric-label">Rentabilidad Anual</div>
            <div class="metric-value">{formato_porcentaje(rentabilidad)}</div>
        </div>
        <div class="kpi-card card-4">
            <div class="metric-icon">=</div>
            <div class="metric-label">% Representado</div>
            <div class="metric-value">{porcentaje_total:.2f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Gr¨¢ficos mejorados ---
    if not df_filtrado.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Analisis Visual</h3>', unsafe_allow_html=True)
        
        # Gr¨¢fico de barras mejorado
        grafico_df = df_filtrado.groupby('Tipo de inversion')['Dinero'].sum().reset_index()
        
        # Definir colores consistentes
        color_map = {
            'CDT': '#636EFA',  # Azul
            'Neo banco': '#EF553B'  # Rojo/Naranja
        }
        
        fig_bar = px.bar(
            grafico_df,
            x='Tipo de inversion',
            y='Dinero',
            color='Tipo de inversion',
            color_discrete_map=color_map,
            text_auto='.2s',
            template='plotly_white',
            title='Distribucion por Tipo'
        )
        fig_bar.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="$ COP",
            title_font_size=16
        )
        fig_bar.update_traces(
            textfont_size=12
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # --- Tabla mejorada ---
    st.markdown('<h3 class="section-title">Detalle del Portafolio</h3>', unsafe_allow_html=True)
    
    columnas_a_formatear = ['Dinero', 'Interes Mensual', 'Ingreso Mensual Necesario']
    df_formateado = formatear_columnas_para_vista(df_filtrado, columnas_a_formatear)

    if 'Porcentaje' in df_formateado.columns:
        df_formateado['Porcentaje'] = df_filtrado['Porcentaje'].apply(lambda x: f"{x * 100:.2f}%")

    # Estilo para la tabla
    st.markdown("""
    <style>
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        df_formateado,
        use_container_width=True,
        hide_index=True
    )   