import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import numpy as np

def cargar_historial_capital():
    """
    Carga el historial de capital desde un archivo JSON
    """
    try:
        if os.path.exists('historial_capital.json'):
            with open('historial_capital.json', 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                df['fecha'] = pd.to_datetime(df['fecha'])
                return df
        else:
            return pd.DataFrame(columns=['fecha', 'capital_cop', 'capital_usd', 'tasa_cop'])
    except Exception as e:
        st.error(f"Error cargando historial: {e}")
        return pd.DataFrame(columns=['fecha', 'capital_cop', 'capital_usd', 'tasa_cop'])

def guardar_historial_capital(df):
    """
    Guarda el historial de capital en un archivo JSON
    """
    try:
        # Convertir timestamps a string para JSON
        df_to_save = df.copy()
        df_to_save['fecha'] = df_to_save['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        with open('historial_capital.json', 'w') as f:
            json.dump(df_to_save.to_dict('records'), f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error guardando historial: {e}")
        return False

def agregar_registro_capital(capital_cop, capital_usd, tasa_cop):
    """
    Agrega un nuevo registro al historial de capital
    SOLO mantiene el último registro del día
    """
    df_historial = cargar_historial_capital()
    
    # Obtener la fecha de hoy (sin hora)
    hoy = datetime.now().date()
    
    if not df_historial.empty:
        # Eliminar TODOS los registros del día de hoy
        df_historial = df_historial[df_historial['fecha'].dt.date != hoy]
    
    # Agregar NUEVO registro (solo uno por día)
    nuevo_registro = pd.DataFrame({
        'fecha': [datetime.now()],
        'capital_cop': [capital_cop],
        'capital_usd': [capital_usd],
        'tasa_cop': [tasa_cop]
    })
    
    df_historial = pd.concat([df_historial, nuevo_registro], ignore_index=True)
    
    # Ordenar por fecha
    df_historial = df_historial.sort_values('fecha')
    
    # Guardar en archivo
    if guardar_historial_capital(df_historial):
        return df_historial
    else:
        return None

def obtener_ultimo_registro_por_dia(df_historial):
    """
    Retorna el DataFrame con solo el último registro VÁLIDO de cada día
    Elimina días con valores nulos, cero o inválidos
    """
    if df_historial is None or df_historial.empty:
        return df_historial
    
    # Crear copia y limpiar datos
    df = df_historial.copy()
    
    # Eliminar registros con valores nulos o inválidos
    df = df.dropna(subset=['capital_usd', 'capital_cop'])
    df = df[(df['capital_usd'] > 0) & (df['capital_cop'] > 0)]
    
    if df.empty:
        return df
    
    # Crear columna de fecha sin hora
    df['fecha_dia'] = df['fecha'].dt.date
    
    # Obtener el último registro válido de cada día
    ultimo_por_dia = df.sort_values('fecha').groupby('fecha_dia').last().reset_index()
    ultimo_por_dia = ultimo_por_dia.drop('fecha_dia', axis=1)
    
    # Ordenar por fecha final
    ultimo_por_dia = ultimo_por_dia.sort_values('fecha')
    
    return ultimo_por_dia

def crear_grafico_capital_usd(df_historial, periodo="Todos"):
    """
    Crea un gráfico moderno y mejorado del capital en USD
    """
    if df_historial is None or df_historial.empty:
        return None
    
    # Obtener solo el último registro válido de cada día
    df_completo = obtener_ultimo_registro_por_dia(df_historial)
    
    # Eliminar registros con valores nulos o cero
    df_completo = df_completo.dropna(subset=['capital_usd'])
    df_completo = df_completo[df_completo['capital_usd'] > 0]
    
    # Filtrar datos según el período seleccionado
    ahora = datetime.now()
    
    periodos = {
        "7 días": 7,
        "30 días": 30,
        "90 días": 90,
        "1 año": 365
    }
    
    # IMPORTANTE: Aplicar filtro de período ANTES de calcular métricas
    if periodo in periodos:
        fecha_limite = ahora - timedelta(days=periodos[periodo])
        df_filtrado = df_completo[df_completo['fecha'] >= fecha_limite].copy()
    else:
        df_filtrado = df_completo.copy()
    
    if df_filtrado.empty or len(df_filtrado) < 1:
        return None
    
    # Ordenar por fecha para asegurar continuidad
    df_filtrado = df_filtrado.sort_values('fecha').reset_index(drop=True)
    
    # Cálculo de métricas de rendimiento SOLO con datos del período filtrado
    if len(df_filtrado) > 1:
        valor_inicial = float(df_filtrado['capital_usd'].iloc[0])
        valor_final = float(df_filtrado['capital_usd'].iloc[-1])
        cambio_absoluto = valor_final - valor_inicial
        
        if valor_inicial != 0:
            cambio_porcentual = (cambio_absoluto / valor_inicial) * 100
        else:
            cambio_porcentual = 0
            
        valor_max = float(df_filtrado['capital_usd'].max())
        valor_min = float(df_filtrado['capital_usd'].min())
        
    else:
        valor_inicial = float(df_filtrado['capital_usd'].iloc[0])
        valor_final = valor_inicial
        cambio_porcentual = 0.0
        cambio_absoluto = 0.0
        valor_max = valor_inicial
        valor_min = valor_inicial
    
    # Calcular rango dinámico para mejor visualización de caídas
    rango_datos = valor_max - valor_min
    margen_visual = rango_datos * 0.1  # 10% de margen arriba y abajo
    
    # Si el rango es muy pequeño, usar un margen fijo
    if rango_datos < valor_min * 0.02:  # Menos del 2% de variación
        margen_visual = valor_min * 0.05  # 5% de margen
    
    # Colores modernos basados en rendimiento
    if cambio_absoluto >= 0:
        color_principal = '#10B981'  # Verde esmeralda
        color_fill = 'rgba(16, 185, 129, 0.1)'
        color_gradient = 'rgba(16, 185, 129, 0.05)'
    else:
        color_principal = '#EF4444'  # Rojo moderno
        color_fill = 'rgba(239, 68, 68, 0.1)'
        color_gradient = 'rgba(239, 68, 68, 0.05)'
    
    # Crear gráfico mejorado
    fig = go.Figure()
    
    # LÍNEA ROJA HORIZONTAL en el punto mínimo (si hay caída significativa)
    variacion_relativa = (valor_max - valor_min) / valor_min if valor_min > 0 else 0
    if variacion_relativa > 0.01 and len(df_filtrado) > 1:  # Si hay más de 1% de variación
        fig.add_trace(go.Scatter(
            x=[df_filtrado['fecha'].iloc[0], df_filtrado['fecha'].iloc[-1]],
            y=[valor_min, valor_min],
            mode='lines',
            line=dict(
                color='rgba(239, 68, 68, 0.6)',
                width=2,
                dash='dash'
            ),
            name='Mínimo del período',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Línea principal mejorada (sin relleno hasta cero para ver mejor las caídas)
    fig.add_trace(go.Scatter(
        x=df_filtrado['fecha'],
        y=df_filtrado['capital_usd'],
        mode='lines+markers',
        line=dict(
            color=color_principal,
            width=3,
        ),
        marker=dict(
            size=6,
            color=color_principal,
            line=dict(width=2, color='white'),
            symbol='circle'
        ),
        fill='tozeroy',
        fillcolor=color_fill,
        name='Capital USD',
        hovertemplate='<b>$%{y:,.0f} USD</b><br>' +
                      '<span style="color: #6B7280;">%{x|%d %B %Y}</span><br>' +
                      '<extra></extra>',
        showlegend=False
    ))
    
    # Configurar formato de fechas mejorado
    num_puntos = len(df_filtrado)
    dias_total = (df_filtrado['fecha'].iloc[-1] - df_filtrado['fecha'].iloc[0]).days if num_puntos > 1 else 1
    
    # Configuración de ejes X mejorada
    if periodo == "7 días" or dias_total <= 7:
        dtick = "D1"  # Cada día
        tickformat = "%d %b"
    elif periodo == "30 días" or dias_total <= 30:
        dtick = "D2"  # Cada 2 días  
        tickformat = "%d %b"
    elif periodo == "90 días" or dias_total <= 90:
        dtick = "D7"  # Cada semana
        tickformat = "%d %b"
    else:
        dtick = "M1"  # Cada mes
        tickformat = "%b %Y"
    
    # Layout mejorado y moderno
    fig.update_layout(
        # Título elegante
        title={
            'text': f'<b style="color: #1F2937;">💰 Evolución del Capital</b><span style="color: #6B7280; font-size: 16px;"> - {periodo}</span>',
            'font': {'size': 22, 'family': 'Inter, -apple-system, sans-serif'},
            'x': 0.02,
            'xanchor': 'left',
            'y': 0.95
        },
        
        # Colores y fondo
        plot_bgcolor='white',
        paper_bgcolor='white',
        
        # Dimensiones
        height=550,
        margin=dict(l=60, r=60, t=80, b=60),
        
        # Eje X mejorado
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(156, 163, 175, 0.2)',
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor='rgba(156, 163, 175, 0.3)',
            linewidth=1,
            tickfont=dict(size=11, color='#6B7280', family='Inter, sans-serif'),
            tickformat=tickformat,
            dtick=dtick,
            tickangle=-45 if periodo not in ["7 días", "30 días"] else 0,
            title=dict(
                text='<b style="color: #374151;">Fecha</b>',
                font=dict(size=13, family='Inter, sans-serif')
            ),
        ),
        
        # Eje Y mejorado con rango dinámico
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(156, 163, 175, 0.2)',
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor='rgba(156, 163, 175, 0.3)',
            linewidth=1,
            tickfont=dict(size=11, color='#6B7280', family='Inter, sans-serif'),
            tickformat='$,.0f',
            title=dict(
                text='<b style="color: #374151;">Capital (USD)</b>',
                font=dict(size=13, family='Inter, sans-serif')
            ),
            # Usar rango dinámico para mejor visualización de cambios
            range=[max(0, valor_min - margen_visual), valor_max + margen_visual]
        ),
        
        # Hover mejorado
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=color_principal,
            font=dict(size=12, family='Inter, sans-serif')
        ),
        
        # Fuente general
        font=dict(family='Inter, -apple-system, sans-serif', size=12, color='#374151')
    )
    
    # Anotaciones mejoradas
    if len(df_filtrado) > 1:
        # Indicador de rendimiento principal
        fig.add_annotation(
            x=df_filtrado['fecha'].iloc[-1],
            y=valor_final,
            text=f'<b style="font-size: 14px;">{cambio_porcentual:+.1f}%</b><br><span style="font-size: 12px;">${cambio_absoluto:+,.0f}</span>',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color_principal,
            ax=60,
            ay=-40,
            font=dict(size=12, color=color_principal, family='Inter, sans-serif'),
            bgcolor='white',
            bordercolor=color_principal,
            borderwidth=2,
            borderpad=8
        )
        
        # Información estadística como tarjeta moderna
        stats_text = f'📊 {dias_total} días • {len(df_filtrado)} registros • Rango: ${valor_min:,.0f} - ${valor_max:,.0f}'
        fig.add_annotation(
            text=stats_text,
            xref="paper", yref="paper",
            x=0.02, y=0.02,
            showarrow=False,
            font=dict(size=11, color='#6B7280', family='Inter, sans-serif'),
            bgcolor='rgba(249, 250, 251, 0.95)',
            bordercolor='rgba(209, 213, 219, 0.5)',
            borderwidth=1,
            borderpad=8
        )
        
        # Indicadores de máximo y mínimo solo si hay variación significativa
        variacion_relativa = (valor_max - valor_min) / valor_min if valor_min > 0 else 0
        if variacion_relativa > 0.02:  # Solo si hay más de 2% de variación
            # Punto mínimo con indicador más visible
            if len(df_filtrado) > 1:
                fecha_min = df_filtrado[df_filtrado['capital_usd'] == valor_min]['fecha'].iloc[0]
                
                # Marcador grande en el punto mínimo
                fig.add_trace(go.Scatter(
                    x=[fecha_min],
                    y=[valor_min],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='#EF4444',
                        line=dict(width=3, color='white'),
                        symbol='circle'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                # Anotación del mínimo
                fig.add_annotation(
                    x=fecha_min,
                    y=valor_min,
                    text=f'📉 Mínimo<br>${valor_min:,.0f}',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='#EF4444',
                    ax=0,
                    ay=40,
                    font=dict(size=11, color='#DC2626', family='Inter, sans-serif', weight='bold'),
                    bgcolor='rgba(254, 226, 226, 0.95)',
                    bordercolor='#EF4444',
                    borderwidth=2,
                    borderpad=6
                )
            
            # Punto máximo (solo si no es el valor final ni inicial)
            if valor_max != valor_final and valor_max != valor_inicial:
                fecha_max = df_filtrado[df_filtrado['capital_usd'] == valor_max]['fecha'].iloc[0]
                
                # Marcador en el punto máximo
                fig.add_trace(go.Scatter(
                    x=[fecha_max],
                    y=[valor_max],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='#10B981',
                        line=dict(width=3, color='white'),
                        symbol='circle'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
                fig.add_annotation(
                    x=fecha_max,
                    y=valor_max,
                    text=f'📈 Máximo<br>${valor_max:,.0f}',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='#10B981',
                    ax=0,
                    ay=-40,
                    font=dict(size=11, color='#059669', family='Inter, sans-serif', weight='bold'),
                    bgcolor='rgba(209, 250, 229, 0.95)',
                    bordercolor='#10B981',
                    borderwidth=2,
                    borderpad=6
                )
    
    return fig

def obtener_tasa_cambio():
    """
    Retorna las tasas de cambio USD-COP y USD-EUR usando una API pública.
    """
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tasa_cop = data['rates'].get('COP')
            tasa_eur = data['rates'].get('EUR')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return tasa_cop, tasa_eur, timestamp
        else:
            st.error(f"Error al obtener tasas de cambio: Código {response.status_code}")
            return None, None, None
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None, None, None

def formatear_moneda(valor, simbolo="$"):
    """Formatea un número como moneda con separadores de miles."""
    return f"{simbolo} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validar_tasa(tasa, nombre_moneda):
    """Valida que una tasa sea válida (positiva y razonable)."""
    if tasa is None or tasa <= 0:
        return False
    
    if nombre_moneda == "COP" and (tasa < 1000 or tasa > 10000):
        st.warning(f"La tasa USD → {nombre_moneda} ({tasa}) parece inusual.")
    elif nombre_moneda == "EUR" and (tasa < 0.5 or tasa > 2.0):
        st.warning(f"La tasa USD → {nombre_moneda} ({tasa}) parece inusual.")
    
    return True

def mostrar_tasas_actuales(tasa_cop, tasa_eur):
    """Muestra las tasas de cambio actuales"""
    st.subheader("📊 Tasas de Cambio Actuales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if validar_tasa(tasa_cop, "COP"):
            st.metric(
                "USD → COP", 
                formatear_moneda(tasa_cop, "$"),
                help="Pesos Colombianos por 1 Dólar"
            )
        else:
            st.error("❌ Tasa USD → COP no disponible")

    with col2:
        if validar_tasa(tasa_eur, "EUR"):
            st.metric(
                "USD → EUR", 
                formatear_moneda(tasa_eur, "€"),
                help="Euros por 1 Dólar"
            )
        else:
            st.error("❌ Tasa USD → EUR no disponible")
    
    with col3:
        if validar_tasa(tasa_cop, "COP") and validar_tasa(tasa_eur, "EUR"):
            tasa_cop_eur = tasa_eur / tasa_cop
            st.metric(
                "COP → EUR", 
                f"€ {tasa_cop_eur:.6f}",
                help="Euros por 1 Peso Colombiano"
            )

def mostrar_conversores(tasa_cop, tasa_eur):
    """Muestra los conversores de moneda"""
    st.subheader("🔄 Conversores de Moneda")

    tab1, tab2, tab3 = st.tabs(["USD ↔ COP", "USD ↔ EUR", "COP ↔ EUR"])

    with tab1:
        if validar_tasa(tasa_cop, "COP"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### USD → COP")
                monto_usd_to_cop = st.number_input(
                    "Monto en USD", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="usd_to_cop_input"
                )
                if monto_usd_to_cop > 0:
                    convertido_cop = monto_usd_to_cop * tasa_cop
                    st.success(f"💰 {formatear_moneda(convertido_cop, '$')}")
            
            with col2:
                st.markdown("#### COP → USD")
                monto_cop_to_usd = st.number_input(
                    "Monto en COP", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="cop_to_usd_input"
                )
                if monto_cop_to_usd > 0:
                    convertido_usd = monto_cop_to_usd / tasa_cop
                    st.success(f"💰 {formatear_moneda(convertido_usd, 'US$')}")

    with tab2:
        if validar_tasa(tasa_eur, "EUR"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### USD → EUR")
                monto_usd_to_eur = st.number_input(
                    "Monto en USD", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="usd_to_eur_input"
                )
                if monto_usd_to_eur > 0:
                    convertido_eur = monto_usd_to_eur * tasa_eur
                    st.success(f"💰 {formatear_moneda(convertido_eur, '€')}")
            
            with col2:
                st.markdown("#### EUR → USD")
                monto_eur_to_usd = st.number_input(
                    "Monto en EUR", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="eur_to_usd_input"
                )
                if monto_eur_to_usd > 0:
                    convertido_usd_from_eur = monto_eur_to_usd / tasa_eur
                    st.success(f"💰 {formatear_moneda(convertido_usd_from_eur, 'US$')}")

    with tab3:
        if validar_tasa(tasa_cop, "COP") and validar_tasa(tasa_eur, "EUR"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### COP → EUR")
                monto_cop_to_eur = st.number_input(
                    "Monto en COP", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="cop_to_eur_input"
                )
                if monto_cop_to_eur > 0:
                    usd_intermedio = monto_cop_to_eur / tasa_cop
                    convertido_eur_from_cop = usd_intermedio * tasa_eur
                    st.success(f"💰 {formatear_moneda(convertido_eur_from_cop, '€')}")
            
            with col2:
                st.markdown("#### EUR → COP")
                monto_eur_to_cop = st.number_input(
                    "Monto en EUR", 
                    min_value=0.0, 
                    format="%.2f", 
                    key="eur_to_cop_input"
                )
                if monto_eur_to_cop > 0:
                    usd_intermedio = monto_eur_to_cop / tasa_eur
                    convertido_cop_from_eur = usd_intermedio * tasa_cop
                    st.success(f"💰 {formatear_moneda(convertido_cop_from_eur, '$')}")

def mostrar_evolucion_capital(tasa_cop):
    """Muestra la evolución del capital con diseño mejorado"""
    
    # Encabezado moderno con estilo
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; 
                    border-radius: 15px; 
                    margin-bottom: 2rem;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 700;">
                📈 Evolución del Capital
            </h2>
            <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem; font-size: 1.1rem;">
                Análisis histórico de tu portafolio
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Cargar historial para mostrar gráfico
    df_historial = cargar_historial_capital()
    
    if not df_historial.empty:
        # Selector de período con diseño mejorado
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📅 Seleccionar Período de Análisis")
        
        with col2:
            periodo_opciones = ["Todos", "7 días", "30 días", "90 días", "1 año"]
            periodo_seleccionado = st.selectbox(
                "Período:", 
                periodo_opciones, 
                index=0,
                key="periodo_select",
                label_visibility="collapsed"
            )
        
        # Calcular estadísticas según el período seleccionado
        df_periodo = obtener_ultimo_registro_por_dia(df_historial)
        
        # Filtrar por período ANTES de calcular métricas
        periodos = {
            "7 días": 7,
            "30 días": 30,
            "90 días": 90,
            "1 año": 365
        }
        
        if periodo_seleccionado in periodos:
            ahora = datetime.now()
            fecha_limite = ahora - timedelta(days=periodos[periodo_seleccionado])
            df_periodo = df_periodo[df_periodo['fecha'] >= fecha_limite]
        
        if not df_periodo.empty and len(df_periodo) > 1:
            capital_actual = df_periodo['capital_usd'].iloc[-1]
            capital_inicial = df_periodo['capital_usd'].iloc[0]
            cambio_total = capital_actual - capital_inicial
            cambio_pct = (cambio_total / capital_inicial * 100) if capital_inicial > 0 else 0
            dias_registrados = (df_periodo['fecha'].iloc[-1] - df_periodo['fecha'].iloc[0]).days
            max_capital = df_periodo['capital_usd'].max()
            min_capital = df_periodo['capital_usd'].min()
            
            # Tarjetas de métricas clave del período seleccionado
            st.markdown(f"### 📊 Resumen del Período: **{periodo_seleccionado}**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta_color = "normal" if cambio_pct >= 0 else "inverse"
                st.metric(
                    label="💰 Capital Actual",
                    value=f"${capital_actual:,.0f}",
                    delta=f"{cambio_pct:+.2f}%",
                    delta_color=delta_color
                )
            
            with col2:
                st.metric(
                    label="📅 Días en Período",
                    value=f"{dias_registrados}",
                    delta=f"{len(df_periodo)} registros"
                )
            
            with col3:
                # Indicar si el máximo es igual al valor actual
                max_label = "🎯 Máximo del Período"
                if max_capital == capital_actual:
                    max_label = "🎯 Máximo (Actual)"
                st.metric(
                    label=max_label,
                    value=f"${max_capital:,.0f}"
                )
            
            with col4:
                # Indicar si el mínimo es igual al valor actual
                min_label = "⚠️ Mínimo del Período"
                if min_capital == capital_actual:
                    min_label = "⚠️ Mínimo (Actual)"
                st.metric(
                    label=min_label,
                    value=f"${min_capital:,.0f}"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Crear y mostrar gráfico
        fig = crear_grafico_capital_usd(df_historial, periodo_seleccionado)
        if fig:
            # Contenedor con borde elegante para el gráfico
            st.markdown("""
                <style>
                .stPlotlyChart {
                    background: white;
                    border-radius: 12px;
                    padding: 1rem;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                    border: 1px solid #e5e7eb;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estadísticas adicionales del período seleccionado
            if not df_periodo.empty and len(df_periodo) > 1:
                st.markdown("---")
                st.markdown(f"### 📈 Análisis Detallado: {periodo_seleccionado}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                inicio_periodo = df_periodo['capital_usd'].iloc[0]
                fin_periodo = df_periodo['capital_usd'].iloc[-1]
                cambio_periodo = fin_periodo - inicio_periodo
                cambio_pct_periodo = (cambio_periodo / inicio_periodo * 100) if inicio_periodo > 0 else 0
                
                with col1:
                    st.metric(
                        "Valor Inicial",
                        f"${inicio_periodo:,.0f}"
                    )
                
                with col2:
                    st.metric(
                        "Valor Final",
                        f"${fin_periodo:,.0f}"
                    )
                
                with col3:
                    delta_color = "normal" if cambio_periodo >= 0 else "inverse"
                    st.metric(
                        "Cambio Absoluto",
                        f"${abs(cambio_periodo):,.0f}",
                        delta=f"{cambio_pct_periodo:+.2f}%",
                        delta_color=delta_color
                    )
                
                with col4:
                    # Calcular volatilidad (rango)
                    rango = max_capital - min_capital
                    volatilidad_pct = (rango / min_capital * 100) if min_capital > 0 else 0
                    st.metric(
                        "Volatilidad",
                        f"${rango:,.0f}",
                        delta=f"{volatilidad_pct:.2f}%"
                    )
                
                with col5:
                    # Calcular promedio del período
                    promedio = df_periodo['capital_usd'].mean()
                    st.metric(
                        "Promedio",
                        f"${promedio:,.0f}"
                    )
            
            # Tabla con últimos registros dentro de un expander elegante
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 Ver Historial Detallado (Últimos 10 registros)", expanded=False):
                # Obtener solo el último registro de cada día para la tabla
                df_ultimos = obtener_ultimo_registro_por_dia(df_historial)
                df_mostrar = df_ultimos.tail(10).copy()
                
                df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
                df_mostrar['capital_cop'] = df_mostrar['capital_cop'].apply(lambda x: formatear_moneda(x, "$"))
                df_mostrar['capital_usd'] = df_mostrar['capital_usd'].apply(lambda x: formatear_moneda(x, "US$"))
                df_mostrar['tasa_cop'] = df_mostrar['tasa_cop'].apply(lambda x: f"{x:,.2f}")
                
                df_mostrar.columns = ['📅 Fecha', '💵 Capital COP', '💰 Capital USD', '📊 Tasa USD→COP']
                
                # Estilo para la tabla
                st.markdown("""
                    <style>
                    .stDataFrame {
                        border: 1px solid #e5e7eb;
                        border-radius: 8px;
                        overflow: hidden;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    df_mostrar.iloc[::-1], 
                    use_container_width=True, 
                    hide_index=True,
                    height=400
                )
        
    else:
        # Mensaje cuando no hay datos con diseño mejorado
        st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        padding: 3rem;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
                <h3 style="color: white; font-size: 1.8rem; margin-bottom: 1rem;">
                    📊 No hay datos históricos
                </h3>
                <p style="color: rgba(255,255,255,0.95); font-size: 1.1rem; margin-bottom: 0;">
                    Guarda tu primer registro para comenzar a ver la evolución de tu capital
                </p>
            </div>
        """, unsafe_allow_html=True)

def mostrar_divisas():
    st.set_page_config(
        page_title="Consulta de Divisas - Histórico Capital",
        page_icon="💱",
        layout="wide"
    )
    
    st.title("💱 Consulta de Divisas y Evolución del Capital")
    
    # Cache para evitar llamadas excesivas a la API
    if 'last_api_call' not in st.session_state:
        st.session_state.last_api_call = 0
    if 'cached_rates' not in st.session_state:
        st.session_state.cached_rates = (None, None, None)
    
    # Llamar a la API solo si han pasado más de 60 segundos
    current_time = time.time()
    if current_time - st.session_state.last_api_call > 60:
        api_tasa_cop, api_tasa_eur, timestamp = obtener_tasa_cambio()
        st.session_state.cached_rates = (api_tasa_cop, api_tasa_eur, timestamp)
        st.session_state.last_api_call = current_time
    else:
        api_tasa_cop, api_tasa_eur, timestamp = st.session_state.cached_rates

    # Botón para refrescar tasas
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Actualizar Tasas", use_container_width=True):
            api_tasa_cop, api_tasa_eur, timestamp = obtener_tasa_cambio()
            st.session_state.cached_rates = (api_tasa_cop, api_tasa_eur, timestamp)
            st.session_state.last_api_call = current_time
            st.rerun()

    tasa_actual_cop = api_tasa_cop
    tasa_actual_eur = api_tasa_eur

    # Mostrar información de las tasas de la API
    if timestamp:
        st.info(f"📅 Tasas actualizadas: {timestamp}")

    # Sección de tasas manuales - CORREGIDO
    with st.expander("⚙️ Configuración Manual de Tasas", expanded=False):
        st.markdown("**Usa esta sección solo si las tasas de la API no están disponibles.**")
        
        col1, col2 = st.columns(2)
        with col1:
            # Asegurar que el value siempre sea float
            default_cop = 4500.0
            if api_tasa_cop is not None:
                default_cop = float(api_tasa_cop)
            
            manual_tasa_cop = st.number_input(
                "Tasa USD → COP (manual)", 
                min_value=0.0, 
                value=default_cop,
                step=100.0, 
                format="%.2f", 
                key="manual_usd_cop"
            )
        
        with col2:
            # Asegurar que el value siempre sea float
            default_eur = 0.85
            if api_tasa_eur is not None:
                default_eur = float(api_tasa_eur)
            
            manual_tasa_eur = st.number_input(
                "Tasa USD → EUR (manual)", 
                min_value=0.0, 
                value=default_eur,
                step=0.01, 
                format="%.4f", 
                key="manual_usd_eur"
            )

        usar_manual = st.checkbox("Usar tasas manuales en lugar de las de la API")
        if usar_manual:
            if manual_tasa_cop > 0:
                tasa_actual_cop = manual_tasa_cop
            if manual_tasa_eur > 0:
                tasa_actual_eur = manual_tasa_eur

    # Mostrar las tasas actuales
    mostrar_tasas_actuales(tasa_actual_cop, tasa_actual_eur)

    # Cálculo del capital del portafolio
    if validar_tasa(tasa_actual_cop, "COP"):
        
        st.subheader("💼 Capital del Portafolio")
        
        try:
            if 'df' in st.session_state and st.session_state.df is not None and not st.session_state.df.empty:
                df = st.session_state.df.copy()
                
                # Limpiar y convertir la columna de dinero
                if 'Dinero' in df.columns:
                    df['Dinero'] = df['Dinero'].astype(str).str.replace(r'[\$,]', '', regex=True)
                    df['Dinero'] = pd.to_numeric(df['Dinero'], errors='coerce')
                    df = df.dropna(subset=['Dinero'])
                    
                    capital_total_cop = df['Dinero'].sum()
                    capital_total_usd = capital_total_cop / tasa_actual_cop
                    capital_total_eur = capital_total_usd * tasa_actual_eur if validar_tasa(tasa_actual_eur, "EUR") else 0

                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Capital en COP", 
                            formatear_moneda(capital_total_cop, "$")
                        )

                    with col2:
                        st.metric(
                            "Capital en USD", 
                            formatear_moneda(capital_total_usd, "US$")
                        )

                    with col3:
                        if validar_tasa(tasa_actual_eur, "EUR"):
                            st.metric(
                                "Capital en EUR", 
                                formatear_moneda(capital_total_eur, "€")
                            )

                    with col4:
                        # Botón para guardar registro diario
                        if st.button("💾 Guardar Registro del Día", use_container_width=True, help="Guarda el capital actual para el histórico"):
                            df_historial = agregar_registro_capital(
                                capital_total_cop, 
                                capital_total_usd, 
                                tasa_actual_cop
                            )
                            if df_historial is not None:
                                st.success("✅ Registro guardado exitosamente")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Error al guardar el registro")

                    # Mostrar evolución del capital
                    mostrar_evolucion_capital(tasa_actual_cop)
                
                else:
                    st.warning("La columna 'Dinero' no se encuentra en el portafolio cargado.")
            else:
                st.info("💡 Carga tu portafolio para ver el capital y su evolución histórica.")

        except Exception as e:
            st.error(f"Error al calcular el capital: {e}")

        # Mostrar conversores de moneda
        mostrar_conversores(tasa_actual_cop, tasa_actual_eur)
    
    else:
        st.error("❌ No hay tasas de cambio válidas disponibles.")

# Para ejecutar la aplicación
if __name__ == "__main__":
    mostrar_divisas()