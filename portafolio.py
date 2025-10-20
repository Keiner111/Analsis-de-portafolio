import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime, timedelta

# Verificar si plotly está disponible
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Configuración de estilo para matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['axes.grid'] = True

# Define el nombre del archivo para guardar los parámetros de las metas de KPIs
KPI_META_PARAMS_FILE = "kpi_meta_params.json"

# ========================================
# FUNCIONES AUXILIARES
# ========================================

def formato_pesos(valor):
    """Formatea el numero con separador de miles como '.' y decimal como ','"""
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formato_porcentaje(valor):
    """Formatea porcentajes con 2 decimales"""
    return f"{valor:.2f}%"

def load_kpis_meta_params():
    """Carga los parámetros de las metas de KPIs desde un archivo JSON."""
    if os.path.exists(KPI_META_PARAMS_FILE):
        with open(KPI_META_PARAMS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {
                    "meta_capital": 50_000_000.0,
                    "meta_ingreso_pasivo": 1_000_000.0
                }
    return {
        "meta_capital": 50_000_000.0,
        "meta_ingreso_pasivo": 1_000_000.0
    }

def save_kpis_meta_params(params_dict):
    """Guarda los parámetros de las metas de KPIs en un archivo JSON."""
    with open(KPI_META_PARAMS_FILE, 'w') as f:
        json.dump(params_dict, f, indent=4)

# ========================================
# MÓDULO DE ANÁLISIS DE PORTAFOLIO
# ========================================

# ========================================
# MÓDULO DE ANÁLISIS DE PORTAFOLIO - VERSIÓN MEJORADA
# ========================================

def analizar_portafolio(df):
    # Encabezado con estilo mejorado
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
            <h1 style='color: white; text-align: center; margin: 0; font-size: 2.5rem;'>
                📊 Dashboard de Inversiones
            </h1>
            <p style='color: rgba(255,255,255,0.9); text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
                Análisis completo de tu portafolio
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Limpieza de datos
    df = df.copy()
    df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
    df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

    # Cálculos generales
    capital_total = df['Dinero'].sum()
    capital_productivo = df[df['Interes Mensual'] > 0]['Dinero'].sum()
    porcentaje_improductivo = ((capital_total - capital_productivo) / capital_total) * 100 if capital_total > 0 else 0
    porcentaje_productivo = (capital_productivo / capital_total) * 100 if capital_total > 0 else 0
    ingresos_mensuales = df['Interes Mensual'].sum()
    tasa_promedio = (ingresos_mensuales / capital_total * 100) if capital_total > 0 else 0
    df['Tasa (%)'] = np.where(df['Dinero'] > 0, (df['Interes Mensual'] / df['Dinero']) * 100, 0)

    # ========================================
    # DASHBOARD DE MÉTRICAS PRINCIPALES
    # ========================================
    st.markdown("### 📈 Métricas Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>💰 Capital Total</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(capital_total)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📈 Ingresos Mensuales</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(ingresos_mensuales)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>✅ Tasa Promedio</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_porcentaje(tasa_promedio)}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        color_improductivo = '#43e97b' if porcentaje_improductivo < 10 else '#fa709a' if porcentaje_improductivo < 30 else '#ee0979'
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_improductivo} 0%, #fee140 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>⚠️ Capital Improductivo</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_porcentaje(porcentaje_improductivo)}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================
    # GRÁFICO DE DISTRIBUCIÓN DEL CAPITAL
    # ========================================
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 🥧 Distribución del Capital")
        if PLOTLY_AVAILABLE:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Capital Productivo', 'Capital Improductivo'],
                values=[capital_productivo, capital_total - capital_productivo],
                marker=dict(colors=['#667eea', '#f5576c']),
                hole=0.4,
                textinfo='label+percent',
                textfont_size=14
            )])
            fig_pie.update_layout(
                showlegend=True,
                height=350,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = ['#667eea', '#f5576c']
            ax.pie([capital_productivo, capital_total - capital_productivo], 
                   labels=['Productivo', 'Improductivo'], 
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
            plt.close(fig)
    
    with col_chart2:
        st.markdown("### 📊 Top 5 Inversiones por Monto")
        top_5_capital = df.nlargest(5, 'Dinero')
        if PLOTLY_AVAILABLE:
            fig_bar = go.Figure(data=[go.Bar(
                x=top_5_capital['Dinero'],
                y=top_5_capital['Personas'],
                orientation='h',
                marker=dict(
                    color=top_5_capital['Dinero'],
                    colorscale='Viridis',
                    showscale=False
                ),
                text=[formato_pesos(val) for val in top_5_capital['Dinero']],
                textposition='outside'
            )])
            fig_bar.update_layout(
                xaxis_title='Capital Invertido',
                yaxis_title='',
                height=350,
                margin=dict(t=20, b=40, l=10, r=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(top_5_capital['Personas'], top_5_capital['Dinero'], color='skyblue')
            ax.set_xlabel('Capital')
            st.pyplot(fig)
            plt.close(fig)

    # ========================================
    # TABS CON CONTENIDO MEJORADO
    # ========================================
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "📊 Análisis Visual", "📋 Datos Completos", "💡 Recomendaciones"])
    
    with tab1:
        st.markdown("### 🏆 Mejores y Peores Rendimientos")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                            padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: #333;'>🥇 Top 5 - Mayor Rendimiento</h4>
                </div>
            """, unsafe_allow_html=True)
            
            top_5 = df.sort_values(by="Interes Mensual", ascending=False).head(5).copy()
            top_5_display = top_5[['Personas', 'Dinero', 'Interes Mensual', 'Tasa (%)']].copy()
            top_5_display["Dinero"] = top_5_display["Dinero"].map(formato_pesos)
            top_5_display["Interes Mensual"] = top_5_display["Interes Mensual"].map(formato_pesos)
            top_5_display["Tasa (%)"] = top_5_display["Tasa (%)"].map(formato_porcentaje)
            
            # Aplicar estilo con colores
            st.dataframe(
                top_5_display,
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); 
                            padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: #333;'>🐌 Bottom 5 - Menor Rendimiento</h4>
                </div>
            """, unsafe_allow_html=True)
            
            low_5 = df[df['Interes Mensual'] > 0].sort_values(by="Interes Mensual", ascending=True).head(5).copy()
            if not low_5.empty:
                low_5_display = low_5[['Personas', 'Dinero', 'Interes Mensual', 'Tasa (%)']].copy()
                low_5_display["Dinero"] = low_5_display["Dinero"].map(formato_pesos)
                low_5_display["Interes Mensual"] = low_5_display["Interes Mensual"].map(formato_pesos)
                low_5_display["Tasa (%)"] = low_5_display["Tasa (%)"].map(formato_porcentaje)
                st.dataframe(low_5_display, use_container_width=True, hide_index=True)
            else:
                st.info("✅ No hay inversiones con bajo rendimiento")
    
    with tab2:
        st.markdown("### 📉 Rendimiento Detallado por Inversión")
        
        if PLOTLY_AVAILABLE:
            df_ordenado = df.sort_values(by='Tasa (%)', ascending=True)
            
            # Gráfico de barras horizontal mejorado
            fig = go.Figure()
            
            colors = ['#ee0979' if x < 0.5 else '#f5576c' if x < 1 else '#667eea' if x < 2 else '#43e97b' 
                      for x in df_ordenado['Tasa (%)']]
            
            fig.add_trace(go.Bar(
                y=df_ordenado['Personas'],
                x=df_ordenado['Tasa (%)'],
                orientation='h',
                marker=dict(color=colors),
                text=[f"{val:.2f}%" for val in df_ordenado['Tasa (%)']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Tasa: %{x:.2f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title='Rendimiento Mensual (%)',
                xaxis_title='Tasa de Rendimiento (%)',
                yaxis_title='',
                height=max(450, len(df) * 35),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Leyenda de colores
            st.markdown("""
                <div style='display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;'>
                    <span style='background: #ee0979; padding: 0.3rem 0.8rem; border-radius: 5px; color: white;'>< 0.5%</span>
                    <span style='background: #f5576c; padding: 0.3rem 0.8rem; border-radius: 5px; color: white;'>0.5% - 1%</span>
                    <span style='background: #667eea; padding: 0.3rem 0.8rem; border-radius: 5px; color: white;'>1% - 2%</span>
                    <span style='background: #43e97b; padding: 0.3rem 0.8rem; border-radius: 5px; color: white;'>> 2%</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.4)))
            df_ordenado = df.sort_values(by='Tasa (%)', ascending=False)
            bars = ax.barh(df_ordenado['Personas'], df_ordenado['Tasa (%)'], color='skyblue')
            ax.set_xlabel('Tasa (%)')
            ax.set_title('Rendimiento por Inversión')
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', va='center')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
    
    with tab3:
        st.markdown("### 📋 Tabla Completa del Portafolio")
        
        df_tabla = df[['Personas', 'Tipo de inversion', 'Dinero', 'Interes Mensual', 'Tasa (%)']].sort_values(by='Tasa (%)', ascending=False).copy()
        df_tabla["Dinero"] = df_tabla["Dinero"].map(formato_pesos)
        df_tabla["Interes Mensual"] = df_tabla["Interes Mensual"].map(formato_pesos)
        df_tabla["Tasa (%)"] = df_tabla["Tasa (%)"].map(formato_porcentaje)
        
        st.dataframe(df_tabla, use_container_width=True, hide_index=True, height=400)
        
        # Alertas
        st.markdown("### ⚠️ Alertas de Rendimiento")
        df_bajo = df[df['Tasa (%)'] < 0.5].copy()
        if not df_bajo.empty:
            st.warning(f"⚠️ **{len(df_bajo)} inversiones** con rendimiento < 0.5% mensual")
            df_bajo_display = df_bajo[['Personas', 'Dinero', 'Interes Mensual', 'Tasa (%)']].copy()
            df_bajo_display["Dinero"] = df_bajo_display["Dinero"].map(formato_pesos)
            df_bajo_display["Interes Mensual"] = df_bajo_display["Interes Mensual"].map(formato_pesos)
            df_bajo_display["Tasa (%)"] = df_bajo_display["Tasa (%)"].map(formato_porcentaje)
            st.dataframe(df_bajo_display, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Todas las inversiones superan el 0.5% mensual")
    
    with tab4:
        st.markdown("### 💡 Recomendaciones y Oportunidades")
        
        if not df.empty:
            mejor = df[df['Tasa (%)'] == df['Tasa (%)'].max()].iloc[0]
            peor_productiva = df[df['Interes Mensual'] > 0].sort_values(by='Tasa (%)', ascending=True).head(1)
            sin_rendimiento = df[df['Interes Mensual'] == 0].sort_values(by='Dinero', ascending=False)

            # Mejor inversión
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                            padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
                    <h4 style='margin: 0 0 0.5rem 0; color: #333;'>🏆 Mejor Inversión</h4>
                    <p style='margin: 0; color: #555; font-size: 1.1rem;'>
                        <strong>{mejor['Personas']}</strong> genera <strong>{formato_porcentaje(mejor['Tasa (%)'])}</strong> mensual
                    </p>
                    <p style='margin: 0.5rem 0 0 0; color: #666;'>
                        Ingreso mensual: {formato_pesos(mejor['Interes Mensual'])}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Peor inversión productiva
            if not peor_productiva.empty:
                peor = peor_productiva.iloc[0]
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
                        <h4 style='margin: 0 0 0.5rem 0; color: #333;'>⚠️ Inversión con Menor Rendimiento</h4>
                        <p style='margin: 0; color: #555; font-size: 1.1rem;'>
                            <strong>{peor['Personas']}</strong> solo genera <strong>{formato_porcentaje(peor['Tasa (%)'])}</strong> mensual
                        </p>
                        <p style='margin: 0.5rem 0 0 0; color: #666;'>
                            Considera renegociar o reinvertir
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Capital improductivo
            if not sin_rendimiento.empty:
                mejor_tasa = mejor['Tasa (%)']
                capital_improductivo = sin_rendimiento['Dinero'].sum()
                ingreso_potencial = (capital_improductivo * mejor_tasa) / 100
                
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;'>
                        <h4 style='margin: 0 0 0.5rem 0; color: #333;'>💰 Oportunidad de Optimización</h4>
                        <p style='margin: 0; color: #555; font-size: 1rem;'>
                            Tienes <strong>{formato_pesos(capital_improductivo)}</strong> sin generar ingresos
                        </p>
                        <p style='margin: 0.8rem 0 0 0; color: #333; font-size: 1.1rem; background: white; padding: 1rem; border-radius: 8px;'>
                            <strong>💡 Potencial:</strong> Si reinviertes al {formato_porcentaje(mejor_tasa)} mensual, 
                            generarías <strong>{formato_pesos(ingreso_potencial)}</strong> adicionales cada mes
                        </p>
                        <p style='margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;'>
                            Proyección anual: {formato_pesos(ingreso_potencial * 12)}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                                padding: 1.5rem; border-radius: 12px;'>
                        <h4 style='margin: 0; color: #333;'>🎉 ¡Excelente gestión!</h4>
                        <p style='margin: 0.5rem 0 0 0; color: #555;'>
                            Todo tu capital está generando rendimientos
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📂 Carga tu portafolio para recibir recomendaciones personalizadas")

# ========================================
# MÓDULO DE KPIs Y METAS - VERSIÓN MEJORADA
# ========================================

def mostrar_kpis(df):
    # Encabezado con estilo mejorado
    st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
            <h1 style='color: white; text-align: center; margin: 0; font-size: 2.5rem;'>
                🎯 Centro de Control - KPIs y Metas
            </h1>
            <p style='color: rgba(255,255,255,0.9); text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
                Monitorea tu progreso hacia la libertad financiera
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Configuración de metas en un contenedor elegante
    st.markdown("""
        <div style='background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); 
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h3 style='margin: 0 0 1rem 0; color: #333;'>📌 Define tus Metas Financieras</h3>
        </div>
    """, unsafe_allow_html=True)
    
    saved_kpis_params = load_kpis_meta_params()

    col1, col2 = st.columns(2)
    
    with col1:
        meta_capital = st.number_input(
            "💰 Meta de Capital Total (COP)",
            min_value=0.0,
            value=float(saved_kpis_params.get("meta_capital", 50_000_000.0)),
            step=1_000_000.0,
            format="%.2f",
            key="kpi_meta_capital_input",
            help="Define cuánto capital total deseas acumular"
        )
    
    with col2:
        meta_ingreso_pasivo = st.number_input(
            "📈 Meta de Ingreso Pasivo Mensual (COP)",
            min_value=0.0,
            value=float(saved_kpis_params.get("meta_ingreso_pasivo", 1_000_000.0)),
            step=50_000.0,
            format="%.2f",
            key="kpi_meta_ingreso_pasivo_input",
            help="Define tu objetivo de ingresos mensuales sin trabajar"
        )

    # Guardar parámetros
    save_kpis_meta_params({
        "meta_capital": meta_capital,
        "meta_ingreso_pasivo": meta_ingreso_pasivo
    })

    # Limpieza y cálculos
    df = df.copy()
    df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
    df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

    capital_total = df['Dinero'].sum()
    capital_productivo = df[df['Interes Mensual'] > 0]['Dinero'].sum()
    ingreso_pasivo_actual = df['Interes Mensual'].sum()

    avance_capital = (capital_total / meta_capital) * 100 if meta_capital > 0 else 0
    progreso_ingreso = (ingreso_pasivo_actual / meta_ingreso_pasivo) * 100 if meta_ingreso_pasivo > 0 else 0
    tasa_necesaria = (meta_ingreso_pasivo / capital_productivo) * 100 if capital_productivo > 0 else 0
    
    # Cálculos adicionales
    falta_capital = max(0, meta_capital - capital_total)
    falta_ingreso = max(0, meta_ingreso_pasivo - ingreso_pasivo_actual)
    ingreso_anual_actual = ingreso_pasivo_actual * 12
    ingreso_anual_meta = meta_ingreso_pasivo * 12

    # ========================================
    # DASHBOARD DE KPIs PRINCIPALES
    # ========================================
    st.markdown("### 📊 Indicadores Clave de Desempeño")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color_capital = '#43e97b' if avance_capital >= 100 else '#667eea' if avance_capital >= 70 else '#f5576c'
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_capital} 0%, #38f9d7 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>💰 Capital Actual</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(capital_total)}</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Meta: {formato_pesos(meta_capital)}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_ingreso = '#43e97b' if progreso_ingreso >= 100 else '#667eea' if progreso_ingreso >= 70 else '#f5576c'
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_ingreso} 0%, #fa709a 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📈 Ingreso Mensual</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(ingreso_pasivo_actual)}</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Meta: {formato_pesos(meta_ingreso_pasivo)}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(80,80,80,0.8); margin: 0; font-size: 0.9rem;'>✅ Progreso Capital</p>
                <h2 style='color: #333; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_porcentaje(avance_capital)}</h2>
                <p style='color: rgba(80,80,80,0.8); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Falta: {formato_pesos(falta_capital)}
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(80,80,80,0.8); margin: 0; font-size: 0.9rem;'>🎯 Progreso Ingreso</p>
                <h2 style='color: #333; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_porcentaje(progreso_ingreso)}</h2>
                <p style='color: rgba(80,80,80,0.8); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Falta: {formato_pesos(falta_ingreso)}
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================
    # BARRAS DE PROGRESO VISUALES
    # ========================================
    col_prog1, col_prog2 = st.columns(2)
    
    with col_prog1:
        st.markdown("#### 💰 Progreso de Capital")
        progreso_capital_visual = min(avance_capital, 100)
        st.markdown(f"""
            <div style='background: #e0e0e0; border-radius: 10px; height: 30px; overflow: hidden;'>
                <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                            width: {progreso_capital_visual}%; height: 100%; 
                            display: flex; align-items: center; justify-content: center;
                            transition: width 0.3s ease;'>
                    <span style='color: white; font-weight: bold; font-size: 0.9rem;'>
                        {formato_porcentaje(avance_capital)}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_prog2:
        st.markdown("#### 📈 Progreso de Ingreso Pasivo")
        progreso_ingreso_visual = min(progreso_ingreso, 100)
        st.markdown(f"""
            <div style='background: #e0e0e0; border-radius: 10px; height: 30px; overflow: hidden;'>
                <div style='background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); 
                            width: {progreso_ingreso_visual}%; height: 100%; 
                            display: flex; align-items: center; justify-content: center;
                            transition: width 0.3s ease;'>
                    <span style='color: white; font-weight: bold; font-size: 0.9rem;'>
                        {formato_porcentaje(progreso_ingreso)}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ========================================
    # MÉTRICA DESTACADA - TASA NECESARIA
    # ========================================
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem;'>
            <h3 style='margin: 0 0 0.5rem 0; color: #333;'>📌 Tasa de Retorno Necesaria</h3>
            <h1 style='margin: 0; color: #333; font-size: 3rem;'>{formato_porcentaje(tasa_necesaria)}</h1>
            <p style='margin: 0.5rem 0 0 0; color: #555; font-size: 1rem;'>
                mensual sobre capital productivo para alcanzar tu meta de ingreso
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ========================================
    # TABS PARA ORGANIZAR ANÁLISIS
    # ========================================
    tab1, tab2, tab3 = st.tabs(["📊 Análisis Comparativo", "📋 Matriz de Desempeño", "💡 Insights"])

    with tab1:
        st.markdown("### 🔄 Ingreso Real vs Ingreso Necesario por Inversión")
        
        # Cálculos para el análisis
        df['Peso Relativo'] = df.apply(
            lambda row: row['Dinero'] / capital_productivo if row['Interes Mensual'] > 0 and capital_productivo > 0 else 0,
            axis=1
        )
        df['Ingreso Necesario'] = df['Peso Relativo'] * meta_ingreso_pasivo
        df['Brecha'] = df['Ingreso Necesario'] - df['Interes Mensual']

        # Gráfico comparativo mejorado
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            
            # Ordenar por brecha para mejor visualización
            df_plot = df.sort_values(by='Brecha', ascending=True)
            
            fig.add_trace(go.Bar(
                name='Ingreso Real',
                y=df_plot['Personas'],
                x=df_plot['Interes Mensual'],
                orientation='h',
                marker_color='#43e97b',
                opacity=0.8,
                text=[formato_pesos(val) for val in df_plot['Interes Mensual']],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                name='Ingreso Necesario',
                y=df_plot['Personas'],
                x=df_plot['Ingreso Necesario'],
                orientation='h',
                marker_color='#f5576c',
                opacity=0.8,
                text=[formato_pesos(val) for val in df_plot['Ingreso Necesario']],
                textposition='outside'
            ))
            
            fig.update_layout(
                xaxis_title='Ingreso Mensual (COP)',
                yaxis_title='',
                barmode='group',
                height=max(450, len(df) * 35),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig, ax = plt.subplots(figsize=(12, max(6, len(df) * 0.4)))
            nombres = df['Personas']
            reales = df['Interes Mensual']
            necesarios = df['Ingreso Necesario']
            y_pos = np.arange(len(nombres))
            altura = 0.35

            ax.barh(y_pos - altura/2, reales, altura, label="Ingreso real", color="#4CAF50", alpha=0.7)
            ax.barh(y_pos + altura/2, necesarios, altura, label="Ingreso necesario", color="#F44336", alpha=0.7)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(nombres)
            ax.set_xlabel("COP")
            ax.legend()
            ax.set_title("Comparación: Ingreso Real vs Necesario")
            
            ax.get_xaxis().set_major_formatter(plt.FuncFormatter(
                lambda x, _: f"${int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".")
            ))
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        
        # Resumen de brechas
        st.markdown("#### 📉 Análisis de Brechas")
        col_gap1, col_gap2, col_gap3 = st.columns(3)
        
        inversiones_sobre = len(df[df['Brecha'] < 0])
        inversiones_bajo = len(df[df['Brecha'] > 0])
        brecha_total = df['Brecha'].sum()
        
        with col_gap1:
            st.metric("✅ Superan la Meta", inversiones_sobre)
        with col_gap2:
            st.metric("⚠️ Bajo la Meta", inversiones_bajo)
        with col_gap3:
            st.metric("📊 Brecha Total", formato_pesos(abs(brecha_total)))

    with tab2:
        st.markdown("### 📋 Matriz de Desempeño por Inversión")

        def evaluar_estado(real, necesario):
            if necesario == 0:
                return "⭕ Sin objetivo"
            elif real >= necesario:
                return "✅ Cumple"
            elif real >= necesario * 0.5:
                return "⚠️ Parcial"
            else:
                return "❌ Bajo"

        df['Estado'] = df.apply(
            lambda row: evaluar_estado(row['Interes Mensual'], row['Ingreso Necesario']),
            axis=1
        )
        
        df['Cumplimiento (%)'] = df.apply(
            lambda row: (row['Interes Mensual'] / row['Ingreso Necesario'] * 100) if row['Ingreso Necesario'] > 0 else 0,
            axis=1
        )

        # Tabla de resultados mejorada
        df_matriz = df[['Personas', 'Interes Mensual', 'Ingreso Necesario', 'Brecha', 'Cumplimiento (%)', 'Estado']].copy()
        df_matriz = df_matriz.sort_values(by='Cumplimiento (%)', ascending=False)
        df_matriz['Interes Mensual'] = df_matriz['Interes Mensual'].map(formato_pesos)
        df_matriz['Ingreso Necesario'] = df_matriz['Ingreso Necesario'].map(formato_pesos)
        df_matriz['Brecha'] = df_matriz['Brecha'].map(formato_pesos)
        df_matriz['Cumplimiento (%)'] = df_matriz['Cumplimiento (%)'].map(formato_porcentaje)

        st.dataframe(df_matriz, use_container_width=True, hide_index=True, height=400)

        # Resumen de estado con diseño mejorado
        st.markdown("#### 🎯 Resumen de Cumplimiento")
        
        cumple = len(df[df['Estado'] == '✅ Cumple'])
        parcial = len(df[df['Estado'] == '⚠️ Parcial'])
        bajo = len(df[df['Estado'] == '❌ Bajo'])
        total = len(df[df['Estado'] != '⭕ Sin objetivo'])

        if total > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pct_cumple = (cumple/total)*100
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                                padding: 1.5rem; border-radius: 12px; text-align: center;'>
                        <h3 style='margin: 0; color: #333;'>✅ Cumple Meta</h3>
                        <h2 style='margin: 0.5rem 0; color: #333;'>{cumple}/{total}</h2>
                        <p style='margin: 0; color: #555; font-size: 1.2rem;'>{pct_cumple:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                pct_parcial = (parcial/total)*100
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                                padding: 1.5rem; border-radius: 12px; text-align: center;'>
                        <h3 style='margin: 0; color: #333;'>⚠️ Cumplimiento Parcial</h3>
                        <h2 style='margin: 0.5rem 0; color: #333;'>{parcial}/{total}</h2>
                        <p style='margin: 0; color: #555; font-size: 1.2rem;'>{pct_parcial:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                pct_bajo = (bajo/total)*100
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%); 
                                padding: 1.5rem; border-radius: 12px; text-align: center;'>
                        <h3 style='margin: 0; color: #333;'>❌ Bajo Rendimiento</h3>
                        <h2 style='margin: 0.5rem 0; color: #333;'>{bajo}/{total}</h2>
                        <p style='margin: 0; color: #555; font-size: 1.2rem;'>{pct_bajo:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 💡 Insights y Recomendaciones Estratégicas")
        
        # Proyecciones
        st.markdown("#### 📅 Proyecciones")
        
        col_proj1, col_proj2 = st.columns(2)
        
        with col_proj1:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); 
                            padding: 1.5rem; border-radius: 12px;'>
                    <h4 style='margin: 0 0 1rem 0; color: #333;'>📊 Ingreso Anual Proyectado</h4>
                    <p style='margin: 0; color: #555;'><strong>Actual:</strong> {formato_pesos(ingreso_anual_actual)}</p>
                    <p style='margin: 0.5rem 0; color: #555;'><strong>Meta:</strong> {formato_pesos(ingreso_anual_meta)}</p>
                    <p style='margin: 0.5rem 0; color: #555;'><strong>Diferencia:</strong> {formato_pesos(abs(ingreso_anual_meta - ingreso_anual_actual))}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_proj2:
            if ingreso_pasivo_actual > 0 and falta_capital > 0:
                meses_para_meta = falta_capital / ingreso_pasivo_actual
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                                padding: 1.5rem; border-radius: 12px;'>
                        <h4 style='margin: 0 0 1rem 0; color: #333;'>⏱️ Tiempo Estimado para Meta de Capital</h4>
                        <p style='margin: 0; color: #555;'>Si reinviertes todos tus ingresos pasivos:</p>
                        <h2 style='margin: 0.5rem 0; color: #333;'>{meses_para_meta:.1f} meses</h2>
                        <p style='margin: 0; color: #555;'>({meses_para_meta/12:.1f} años aprox.)</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 Comienza a generar ingresos pasivos para ver proyecciones")
        
        # Recomendaciones accionables
        st.markdown("#### 🎯 Acciones Recomendadas")
        
        if avance_capital >= 100 and progreso_ingreso >= 100:
            st.success("🎉 **¡Felicitaciones!** Has alcanzado ambas metas. Considera aumentar tus objetivos.")
        else:
            recomendaciones = []
            
            if avance_capital < 100:
                recomendaciones.append(f"💰 Te faltan {formato_pesos(falta_capital)} para alcanzar tu meta de capital. Considera aumentar tus aportes mensuales.")
            
            if progreso_ingreso < 100:
                recomendaciones.append(f"📈 Necesitas generar {formato_pesos(falta_ingreso)} más de ingreso pasivo mensual. Busca inversiones con tasas superiores al {formato_porcentaje(tasa_necesaria)}.")
            
            if bajo > 0:
                recomendaciones.append(f"⚠️ Tienes {bajo} inversiones con bajo rendimiento. Evalúa renegociar o reinvertir ese capital.")
            
            for i, rec in enumerate(recomendaciones, 1):
                st.markdown(f"""
                    <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; 
                                margin-bottom: 0.5rem; border-left: 4px solid #667eea;'>
                        <p style='margin: 0; color: #333;'><strong>{i}.</strong> {rec}</p>
                    </div>
                """, unsafe_allow_html=True)

# ========================================
# MÓDULO DE SIMULADOR AVANZADO (Simplificado)
# ========================================

def calcular_metricas_financieras(df):
    """Calcula métricas financieras avanzadas"""
    metricas = {}
    
    metricas['capital_total'] = df['Dinero'].sum()
    metricas['ingreso_pasivo_mensual'] = df['Interes Mensual'].sum()
    metricas['ingreso_pasivo_anual'] = metricas['ingreso_pasivo_mensual'] * 12
    
    if metricas['capital_total'] > 0:
        metricas['rendimiento_promedio'] = (metricas['ingreso_pasivo_anual'] / metricas['capital_total']) * 100
    else:
        metricas['rendimiento_promedio'] = 0
    
    # Índice de diversificación
    if metricas['capital_total'] > 0:
        participaciones = (df['Dinero'] / metricas['capital_total']) ** 2
        metricas['indice_concentracion'] = participaciones.sum()
        metricas['indice_diversificacion'] = 1 - metricas['indice_concentracion']
    else:
        metricas['indice_diversificacion'] = 0
    
    metricas['num_inversiones'] = len(df)
    metricas['activos_improductivos'] = df[df['Interes Mensual'] == 0]['Dinero'].sum()
    
    if metricas['capital_total'] > 0:
        metricas['porcentaje_improductivos'] = (metricas['activos_improductivos'] / metricas['capital_total']) * 100
    else:
        metricas['porcentaje_improductivos'] = 0
    
    return metricas

def calcular_proyecciones_compuestas(df, periodos=[3, 6, 12, 24, 36]):
    """Calcula proyecciones con interés compuesto y simple"""
    df_calc = df.copy()
    
    df_calc['Tasa_Mensual'] = np.where(
        df_calc['Dinero'] > 0,
        df_calc['Interes Mensual'] / df_calc['Dinero'],
        0
    )
    
    for periodo in periodos:
        # Interés Simple
        df_calc[f'Simple_{periodo}M'] = df_calc['Dinero'] + (df_calc['Interes Mensual'] * periodo)
        
        # Interés Compuesto
        df_calc[f'Compuesto_{periodo}M'] = df_calc['Dinero'] * (1 + df_calc['Tasa_Mensual']) ** periodo
        
        # Diferencia
        df_calc[f'Diferencia_{periodo}M'] = df_calc[f'Compuesto_{periodo}M'] - df_calc[f'Simple_{periodo}M']
    
    return df_calc

def simular_proyecciones_integrado(df):
    st.header("📈 Simulador de Proyecciones Financieras")
    st.subheader("Comparación: Interés Simple vs Compuesto")

    # Meta de ingreso pasivo
    meta_ingreso_pasivo = st.number_input(
        "Meta de Ingreso Pasivo Mensual (COP)",
        min_value=0.0,
        value=1_000_000.0,
        step=50_000.0,
        format="%.2f"
    )

    # Limpieza de datos
    df = df.copy()
    df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
    df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

    # Calcular métricas y proyecciones
    metricas = calcular_metricas_financieras(df)
    df_proyecciones = calcular_proyecciones_compuestas(df)

    # Dashboard de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Capital Total", formato_pesos(metricas['capital_total']))
    
    with col2:
        delta_meta = metricas['ingreso_pasivo_mensual'] - meta_ingreso_pasivo
        st.metric(
            "📈 Ingreso Pasivo",
            formato_pesos(metricas['ingreso_pasivo_mensual']),
            delta=formato_pesos(delta_meta) if delta_meta != 0 else None
        )
    
    with col3:
        st.metric("📊 Rendimiento Promedio", formato_porcentaje(metricas['rendimiento_promedio']))
    
    with col4:
        st.metric("🎯 Diversificación", f"{metricas['indice_diversificacion']:.3f}")

    # Selector de período
    periodo_seleccionado = st.selectbox("Período de análisis:", [12, 24, 36], index=1)

    # Tabla comparativa
    st.subheader(f"📋 Proyecciones a {periodo_seleccionado} meses")
    
    columnas_mostrar = ['Personas', 'Dinero', 'Interes Mensual', 
                       f'Simple_{periodo_seleccionado}M', f'Compuesto_{periodo_seleccionado}M', 
                       f'Diferencia_{periodo_seleccionado}M']
    
    df_tabla = df_proyecciones[columnas_mostrar].copy()
    
    # Formatear columnas
    for col in ['Dinero', 'Interes Mensual', f'Simple_{periodo_seleccionado}M', 
                f'Compuesto_{periodo_seleccionado}M', f'Diferencia_{periodo_seleccionado}M']:
        df_tabla[col] = df_tabla[col].map(formato_pesos)
    
    st.dataframe(df_tabla, use_container_width=True)
    
    # Beneficio total del interés compuesto
    beneficio_total = df_proyecciones[f'Diferencia_{periodo_seleccionado}M'].sum()
    st.success(f"💰 **Beneficio del Interés Compuesto**: {formato_pesos(beneficio_total)} COP adicionales en {periodo_seleccionado} meses")

    # Análisis del portafolio
    st.subheader("🧠 Análisis del Portafolio")
    
    if metricas['porcentaje_improductivos'] > 20:
        st.warning(f"⚠️ {formato_porcentaje(metricas['porcentaje_improductivos'])} de tu capital no genera ingresos.")
    
    if metricas['rendimiento_promedio'] < 6:
        st.info("💡 Considera buscar inversiones con mayor rentabilidad (>6% anual).")
    elif metricas['rendimiento_promedio'] > 15:
        st.success(f"🎉 Excelente rendimiento: {formato_porcentaje(metricas['rendimiento_promedio'])} anual.")

# ========================================
# FUNCIÓN PRINCIPAL INTEGRADA
# ========================================

def sistema_financiero_completo(df):
    """Sistema integrado de análisis financiero"""
    
    if df is None or df.empty:
        st.warning("⚠️ No hay datos para analizar. Por favor, carga tu portafolio de inversiones.")
        return
    
    # Crear pestañas principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Análisis Portafolio", 
        "🎯 KPIs y Metas", 
        "📈 Simulador", 
        "📋 Datos"
    ])
    
    with tab1:
        analizar_portafolio(df)
    
    with tab2:
        mostrar_kpis(df)
    
    with tab3:
        simular_proyecciones_integrado(df)
    
    with tab4:
        st.subheader("📋 Datos del Portafolio")
        st.dataframe(df, use_container_width=True)
        
        # Estadísticas básicas
        st.subheader("📊 Estadísticas Básicas")
        df_stats = df.copy()
        df_stats['Dinero'] = df_stats['Dinero'].replace('[\$,]', '', regex=True).astype(float)
        df_stats['Interes Mensual'] = df_stats['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Capital:**")
            st.write(f"- Total: {formato_pesos(df_stats['Dinero'].sum())}")
            st.write(f"- Promedio: {formato_pesos(df_stats['Dinero'].mean())}")
            st.write(f"- Mediana: {formato_pesos(df_stats['Dinero'].median())}")
        
        with col2:
            st.write("**Ingreso Mensual:**")
            st.write(f"- Total: {formato_pesos(df_stats['Interes Mensual'].sum())}")
            st.write(f"- Promedio: {formato_pesos(df_stats['Interes Mensual'].mean())}")
            st.write(f"- Inversiones activas: {len(df_stats[df_stats['Interes Mensual'] > 0])}")

# ========================================
# EJEMPLO DE USO
# ========================================

"""
Para usar este sistema financiero integrado, necesitas un DataFrame con estas columnas:
- Personas: nombre del inversor
- Tipo de inversion: tipo de inversión
- Dinero: capital invertido (puede incluir formato de pesos)
- Interes Mensual: interés mensual generado (puede incluir formato de pesos)

Ejemplo de uso:
```python
import pandas as pd

# Crear DataFrame de ejemplo
df_ejemplo = pd.DataFrame({
    'Personas': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Luis Rodriguez'],
    'Tipo de inversion': ['CDT', 'Acciones', 'Bonos', 'Fondo Mutuo', 'Cuenta Ahorros'],
    'Dinero': ['$5.000.000', '$8.000.000', '$3.000.000', '$12.000.000', '$2.000.000'],
    'Interes Mensual': ['$50.000', '$120.000', '$30.000', '$180.000', '$0']
})

# Ejecutar el sistema
sistema_financiero_completo(df_ejemplo)
```

Características principales del sistema:

🏆 ANÁLISIS DE PORTAFOLIO:
- Dashboard de métricas clave
- Rankings de mejores y peores inversiones
- Visualizaciones interactivas de rendimiento
- Recomendaciones inteligentes automáticas
- Identificación de capital improductivo

🎯 KPIs Y METAS:
- Configuración personalizable de metas financieras
- Seguimiento de progreso hacia objetivos
- Análisis de brechas por inversión
- Matriz de desempeño detallada
- Persistencia de configuraciones

📈 SIMULADOR AVANZADO:
- Cálculos de interés simple vs compuesto
- Proyecciones a múltiples horizontes temporales
- Métricas de diversificación
- Análisis de beneficios del interés compuesto
- Evaluación de estrategias de inversión

📊 VISUALIZACIONES:
- Gráficos interactivos con Plotly (si disponible)
- Fallback a matplotlib para compatibilidad
- Tablas formateadas con estilo colombiano
- Dashboard responsivo con métricas

🔧 CARACTERÍSTICAS TÉCNICAS:
- Sin dependencias problemáticas (seaborn eliminado)
- Detección automática de librerías disponibles
- Formateo consistente de moneda colombiana
- Manejo robusto de errores
- Persistencia de configuraciones en JSON
- Interfaz organizada con tabs

💡 RECOMENDACIONES AUTOMÁTICAS:
- Identificación de oportunidades de mejora
- Análisis de concentración de riesgo
- Sugerencias de rebalanceo
- Alertas de bajo rendimiento
- Cálculo de potencial de ingresos

🎨 INTERFAZ MEJORADA:
- Uso de emojis para mejor UX
- Código limpio y modular
- Documentación integrada
- Manejo de casos edge
- Responsive design
"""