import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Verificar si plotly está disponible
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📋 Plotly no está instalado. Usando matplotlib para visualizaciones. Para gráficos interactivos, instala plotly: `pip install plotly`")

# Configuración de estilo para matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['axes.grid'] = True

# Function to format currency in Colombian Pesos
def formato_pesos(valor):
    """Formatea el numero con separador de miles como '.' y decimal como ','"""
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formato_porcentaje(valor):
    """Formatea porcentajes con 2 decimales"""
    return f"{valor:.2f}%"

def calcular_metricas_financieras(df):
    """Calcula métricas financieras avanzadas"""
    metricas = {}
    
    # Capital total
    metricas['capital_total'] = df['Dinero'].sum()
    
    # Ingreso pasivo total mensual
    metricas['ingreso_pasivo_mensual'] = df['Interes Mensual'].sum()
    
    # Ingreso pasivo anual
    metricas['ingreso_pasivo_anual'] = metricas['ingreso_pasivo_mensual'] * 12
    
    # Rendimiento promedio ponderado (APR)
    if metricas['capital_total'] > 0:
        metricas['rendimiento_promedio'] = (metricas['ingreso_pasivo_anual'] / metricas['capital_total']) * 100
    else:
        metricas['rendimiento_promedio'] = 0
    
    # Índice de diversificación (Herfindahl-Hirschman Index)
    participaciones = (df['Dinero'] / metricas['capital_total']) ** 2
    metricas['indice_concentracion'] = participaciones.sum()
    metricas['indice_diversificacion'] = 1 - metricas['indice_concentracion']
    
    # Número de inversiones
    metricas['num_inversiones'] = len(df)
    
    # Inversión promedio
    metricas['inversion_promedio'] = metricas['capital_total'] / metricas['num_inversiones']
    
    # Activos improductivos
    metricas['activos_improductivos'] = df[df['Interes Mensual'] == 0]['Dinero'].sum()
    metricas['porcentaje_improductivos'] = (metricas['activos_improductivos'] / metricas['capital_total']) * 100
    
    return metricas

def calcular_proyecciones_compuestas(df, periodos=[3, 6, 12, 24, 36]):
    """Calcula proyecciones con interés compuesto y simple"""
    df_calc = df.copy()
    
    # Calcular tasa mensual a partir del interés mensual
    df_calc['Tasa_Mensual'] = np.where(
        df_calc['Dinero'] > 0,
        df_calc['Interes Mensual'] / df_calc['Dinero'],
        0
    )
    
    for periodo in periodos:
        # Interés Simple
        df_calc[f'Simple_{periodo}M'] = df_calc['Dinero'] + (df_calc['Interes Mensual'] * periodo)
        
        # Interés Compuesto: P(1 + r)^t
        df_calc[f'Compuesto_{periodo}M'] = df_calc['Dinero'] * (1 + df_calc['Tasa_Mensual']) ** periodo
        
        # Diferencia entre compuesto y simple
        df_calc[f'Diferencia_{periodo}M'] = df_calc[f'Compuesto_{periodo}M'] - df_calc[f'Simple_{periodo}M']
    
    return df_calc

def crear_dashboard_metricas(metricas, meta_ingreso_pasivo):
    """Crea un dashboard con métricas clave"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Capital Total",
            formato_pesos(metricas['capital_total'])
        )
    
    with col2:
        delta_meta = metricas['ingreso_pasivo_mensual'] - meta_ingreso_pasivo
        st.metric(
            "📈 Ingreso Pasivo Mensual",
            formato_pesos(metricas['ingreso_pasivo_mensual']),
            delta=formato_pesos(delta_meta) if delta_meta != 0 else None
        )
    
    with col3:
        st.metric(
            "📊 Rendimiento Promedio",
            formato_porcentaje(metricas['rendimiento_promedio'])
        )
    
    with col4:
        color = "inverse" if metricas['indice_diversificacion'] < 0.5 else "normal"
        st.metric(
            "🎯 Índice Diversificación",
            f"{metricas['indice_diversificacion']:.3f}",
            delta=None
        )

def crear_visualizacion_avanzada(df_proyecciones):
    """Crea visualizaciones usando matplotlib o plotly según disponibilidad"""
    
    if PLOTLY_AVAILABLE:
        # Gráfico 1: Comparación Interés Simple vs Compuesto
        fig_comparacion = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Proyección 12 meses', 'Proyección 24 meses', 'Diferencia Compuesto vs Simple', 'Distribución de Capital'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "pie"}]]
        )
        
        # Proyección 12 meses
        fig_comparacion.add_trace(
            go.Bar(name='Simple 12M', x=df_proyecciones['Personas'], y=df_proyecciones['Simple_12M'], 
                   marker_color='lightblue', opacity=0.7),
            row=1, col=1
        )
        fig_comparacion.add_trace(
            go.Bar(name='Compuesto 12M', x=df_proyecciones['Personas'], y=df_proyecciones['Compuesto_12M'], 
                   marker_color='darkblue', opacity=0.8),
            row=1, col=1
        )
        
        # Proyección 24 meses
        fig_comparacion.add_trace(
            go.Bar(name='Simple 24M', x=df_proyecciones['Personas'], y=df_proyecciones['Simple_24M'], 
                   marker_color='lightcoral', opacity=0.7, showlegend=False),
            row=1, col=2
        )
        fig_comparacion.add_trace(
            go.Bar(name='Compuesto 24M', x=df_proyecciones['Personas'], y=df_proyecciones['Compuesto_24M'], 
                   marker_color='darkred', opacity=0.8, showlegend=False),
            row=1, col=2
        )
        
        # Diferencia Compuesto vs Simple (24M)
        fig_comparacion.add_trace(
            go.Bar(name='Beneficio Interés Compuesto', x=df_proyecciones['Personas'], 
                   y=df_proyecciones['Diferencia_24M'], marker_color='green', showlegend=False),
            row=2, col=1
        )
        
        # Gráfico de torta - Distribución de capital
        fig_comparacion.add_trace(
            go.Pie(labels=df_proyecciones['Personas'], values=df_proyecciones['Dinero'], 
                   name="Capital", showlegend=False),
            row=2, col=2
        )
        
        fig_comparacion.update_layout(height=800, title_text="Análisis Completo de Inversiones")
        return fig_comparacion
    
    else:
        # Fallback usando matplotlib
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Proyección 12 meses
        x = np.arange(len(df_proyecciones['Personas']))
        width = 0.35
        ax1.bar(x - width/2, df_proyecciones['Simple_12M'], width, label='Simple 12M', alpha=0.7, color='lightblue')
        ax1.bar(x + width/2, df_proyecciones['Compuesto_12M'], width, label='Compuesto 12M', alpha=0.8, color='darkblue')
        ax1.set_title('Proyección 12 meses')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_proyecciones['Personas'], rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Proyección 24 meses
        ax2.bar(x - width/2, df_proyecciones['Simple_24M'], width, label='Simple 24M', alpha=0.7, color='lightcoral')
        ax2.bar(x + width/2, df_proyecciones['Compuesto_24M'], width, label='Compuesto 24M', alpha=0.8, color='darkred')
        ax2.set_title('Proyección 24 meses')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_proyecciones['Personas'], rotation=45)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Diferencia
        ax3.bar(df_proyecciones['Personas'], df_proyecciones['Diferencia_24M'], color='green', alpha=0.7)
        ax3.set_title('Beneficio Interés Compuesto (24M)')
        ax3.set_xticklabels(df_proyecciones['Personas'], rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Distribución de capital
        ax4.pie(df_proyecciones['Dinero'], labels=df_proyecciones['Personas'], autopct='%1.1f%%')
        ax4.set_title('Distribución de Capital')
        
        plt.tight_layout()
        return fig

def crear_grafico_evolucion_temporal(df_proyecciones):
    """Crea gráfico de evolución temporal del portafolio"""
    periodos = [0, 3, 6, 12, 24, 36]
    
    # Calcular totales por período
    totales_simple = [df_proyecciones['Dinero'].sum()]
    totales_compuesto = [df_proyecciones['Dinero'].sum()]
    
    for p in [3, 6, 12, 24, 36]:
        if f'Simple_{p}M' in df_proyecciones.columns:
            totales_simple.append(df_proyecciones[f'Simple_{p}M'].sum())
            totales_compuesto.append(df_proyecciones[f'Compuesto_{p}M'].sum())
    
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=periodos, y=totales_simple,
            mode='lines+markers',
            name='Interés Simple',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=periodos, y=totales_compuesto,
            mode='lines+markers',
            name='Interés Compuesto',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Evolución del Portafolio Total: Simple vs Compuesto',
            xaxis_title='Meses',
            yaxis_title='Valor Total (COP)',
            hovermode='x unified',
            height=500
        )
        return fig
    
    else:
        # Fallback usando matplotlib
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(periodos, totales_simple, 'o-', linewidth=3, markersize=8, 
                label='Interés Simple', color='blue')
        ax.plot(periodos, totales_compuesto, 's-', linewidth=3, markersize=8, 
                label='Interés Compuesto', color='red')
        
        ax.set_title('Evolución del Portafolio Total: Simple vs Compuesto', fontsize=14, fontweight='bold')
        ax.set_xlabel('Meses', fontsize=12)
        ax.set_ylabel('Valor Total (COP)', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Formatear eje Y
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(
            lambda x, _: f"${int(x):,}".replace(",", "X").replace(".", ",").replace("X", ".")
        ))
        
        plt.tight_layout()
        return fig

def analisis_avanzado_portafolio(df, metricas, meta_ingreso_pasivo):
    """Análisis avanzado del portafolio con recomendaciones"""
    st.subheader("🧠 Análisis Avanzado del Portafolio")
    
    # Análisis de diversificación
    if metricas['indice_diversificacion'] < 0.3:
        st.error("🔴 **Portafolio Poco Diversificado**: Tu inversión está muy concentrada. Riesgo alto.")
    elif metricas['indice_diversificacion'] < 0.6:
        st.warning("🟡 **Diversificación Moderada**: Considera distribuir mejor tu capital.")
    else:
        st.success("🟢 **Buena Diversificación**: Tu portafolio está bien distribuido.")
    
    # Análisis de productividad
    if metricas['porcentaje_improductivos'] > 20:
        st.warning(f"⚠️ **{formato_porcentaje(metricas['porcentaje_improductivos'])}** de tu capital no genera ingresos. "
                  f"Esto representa {formato_pesos(metricas['activos_improductivos'])} COP.")
    
    # Análisis de rendimiento
    if metricas['rendimiento_promedio'] < 6:
        st.info("💡 **Rendimiento Bajo**: Considera buscar inversiones con mayor rentabilidad (>6% anual).")
    elif metricas['rendimiento_promedio'] > 15:
        st.success(f"🎉 **Excelente Rendimiento**: {formato_porcentaje(metricas['rendimiento_promedio'])} anual está por encima del promedio.")
    
    # Análisis de meta
    meses_para_meta = 0
    if metricas['ingreso_pasivo_mensual'] > 0:
        deficit = meta_ingreso_pasivo - metricas['ingreso_pasivo_mensual']
        if deficit > 0:
            capital_adicional_necesario = deficit / (metricas['rendimiento_promedio'] / 100 / 12) if metricas['rendimiento_promedio'] > 0 else float('inf')
            st.info(f"📌 **Para alcanzar tu meta necesitas**: {formato_pesos(capital_adicional_necesario)} COP adicionales "
                   f"al rendimiento actual de {formato_porcentaje(metricas['rendimiento_promedio'])} anual.")

def simular_proyecciones(df):
    st.header("📈 Simulador Avanzado de Proyecciones Financieras")
    st.subheader("Interés Simple vs Interés Compuesto con Métricas Avanzadas")

    # �?Campo editable de meta
    meta_ingreso_pasivo = st.number_input(
        "Meta de Ingreso Pasivo Mensual (COP)",
        min_value=0.0,
        value=1_000_000.0,
        step=50_000.0,
        format="%.2f"
    )

    # Limpieza y preparacion
    df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
    df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

    # Calcular métricas financieras
    metricas = calcular_metricas_financieras(df)
    
    # Dashboard de métricas
    crear_dashboard_metricas(metricas, meta_ingreso_pasivo)
    
    st.markdown("---")
    
    # Calcular proyecciones con interés compuesto
    df_proyecciones = calcular_proyecciones_compuestas(df)

    # Tabs para organizar la información
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Tabla Detallada", "📊 Visualizaciones", "📈 Evolución Temporal", "🔍 Análisis"])
    
    with tab1:
        st.subheader("Comparación: Interés Simple vs Compuesto")
        
        # Selector de período
        periodo_seleccionado = st.selectbox("Selecciona el período a mostrar:", [12, 24, 36], index=1)
        
        # Crear tabla comparativa
        columnas_mostrar = ['Personas', 'Tipo de inversion', 'Dinero', 'Interes Mensual', 
                           f'Simple_{periodo_seleccionado}M', f'Compuesto_{periodo_seleccionado}M', 
                           f'Diferencia_{periodo_seleccionado}M']
        
        df_tabla = df_proyecciones[columnas_mostrar].copy()
        
        # Formatear columnas monetarias
        columnas_dinero = ['Dinero', 'Interes Mensual', f'Simple_{periodo_seleccionado}M', 
                          f'Compuesto_{periodo_seleccionado}M', f'Diferencia_{periodo_seleccionado}M']
        
        for col in columnas_dinero:
            df_tabla[col] = df_tabla[col].map(formato_pesos)
        
        st.dataframe(
            df_tabla.style
            .set_properties(**{'text-align': 'center'})
            .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
        )
        
        # Resumen del beneficio del interés compuesto
        beneficio_total = df_proyecciones[f'Diferencia_{periodo_seleccionado}M'].sum()
        st.success(f"💰 **Beneficio del Interés Compuesto en {periodo_seleccionado} meses**: {formato_pesos(beneficio_total)} COP adicionales")
    
    with tab2:
        st.subheader("Análisis Visual Comparativo")
        fig_comparacion = crear_visualizacion_avanzada(df_proyecciones)
        
        if PLOTLY_AVAILABLE:
            st.plotly_chart(fig_comparacion, use_container_width=True)
        else:
            st.pyplot(fig_comparacion)
    
    with tab3:
        st.subheader("Evolución Temporal del Portafolio")
        fig_evolucion = crear_grafico_evolucion_temporal(df_proyecciones)
        
        if PLOTLY_AVAILABLE:
            st.plotly_chart(fig_evolucion, use_container_width=True)
        else:
            st.pyplot(fig_evolucion)
        
        # Tabla de totales por período
        st.subheader("Resumen de Totales por Período")
        periodos = [3, 6, 12, 24, 36]
        resumen_data = []
        
        for p in periodos:
            total_simple = df_proyecciones[f'Simple_{p}M'].sum()
            total_compuesto = df_proyecciones[f'Compuesto_{p}M'].sum()
            diferencia = total_compuesto - total_simple
            
            resumen_data.append({
                'Período (Meses)': p,
                'Total Simple': formato_pesos(total_simple),
                'Total Compuesto': formato_pesos(total_compuesto),
                'Beneficio Compuesto': formato_pesos(diferencia),
                'Diferencia %': formato_porcentaje((diferencia/total_simple)*100)
            })
        
        df_resumen = pd.DataFrame(resumen_data)
        st.dataframe(df_resumen, use_container_width=True)
    
    with tab4:
        analisis_avanzado_portafolio(df, metricas, meta_ingreso_pasivo)
        
        # Información adicional
        st.subheader("📚 Información Adicional")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **💡 Interés Simple**
            - Los intereses no se reinvierten
            - Crecimiento lineal
            - Fórmula: Capital + (Interés × Tiempo)
            """)
        
        with col2:
            st.info("""
            **🚀 Interés Compuesto**
            - Los intereses se reinvierten automáticamente
            - Crecimiento exponencial
            - Fórmula: Capital × (1 + Tasa)^Tiempo
            """)

# Ejemplo de uso (comentado para no ejecutar automáticamente)
"""
# Para usar este simulador, necesitas un DataFrame con las siguientes columnas:
# - Personas: nombre del inversor
# - Tipo de inversion: tipo de inversión
# - Dinero: capital invertido
# - Interes Mensual: interés mensual generado

# Ejemplo de DataFrame:
ejemplo_df = pd.DataFrame({
    'Personas': ['Juan', 'María', 'Carlos'],
    'Tipo de inversion': ['CDT', 'Acciones', 'Bonos'],
    'Dinero': [5000000, 8000000, 3000000],
    'Interes Mensual': [50000, 120000, 30000]
})

# Llamar la función:
simular_proyecciones(ejemplo_df)
"""