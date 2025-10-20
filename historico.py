import pandas as pd
import streamlit as st
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression

RUTA_HISTORIAL = "historial_snapshots.csv"

def formato_pesos(valor):
    """Formatea valores numéricos como moneda colombiana"""
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Función para guardar snapshot
def guardar_snapshot(df):
    hoy = datetime.today().strftime("%Y-%m")
    capital_total = df['Dinero'].replace('[\$,]', '', regex=True).astype(float).sum()
    ingreso_pasivo = df['Interes Mensual'].replace('[\$,]', '', regex=True).astype(float).sum()

    nuevo = pd.DataFrame([{
        "Fecha": hoy,
        "Capital Total": capital_total,
        "Ingreso Pasivo": ingreso_pasivo
    }])

    if os.path.exists(RUTA_HISTORIAL):
        historial = pd.read_csv(RUTA_HISTORIAL)
        historial = historial[historial["Fecha"] != hoy]
        historial = pd.concat([historial, nuevo], ignore_index=True)
    else:
        historial = nuevo

    historial.to_csv(RUTA_HISTORIAL, index=False)
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
            <p style='margin: 0; color: #333; font-weight: 600;'>
                ✅ Snapshot mensual guardado correctamente para {hoy}
            </p>
        </div>
    """.format(hoy=hoy), unsafe_allow_html=True)

# Función para mostrar histórico y predicción
def mostrar_historico():
    # Header principal
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
            <h1 style='color: white; text-align: center; margin: 0; font-size: 2.5rem;'>
                📈 Evolución Histórica del Portafolio
            </h1>
            <p style='color: rgba(255,255,255,0.9); text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
                Análisis temporal y proyecciones futuras
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(RUTA_HISTORIAL):
        st.markdown("""
            <div style='background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); 
                        padding: 2rem; border-radius: 12px; text-align: center;'>
                <h3 style='margin: 0; color: #333;'>📊 No hay historial disponible</h3>
                <p style='margin: 0.5rem 0 0 0; color: #555;'>
                    Guarda tu primer snapshot para comenzar a rastrear tu progreso
                </p>
            </div>
        """, unsafe_allow_html=True)
        return

    historial = pd.read_csv(RUTA_HISTORIAL)

    # Indicadores de crecimiento
    if len(historial) > 1:
        capital_actual = historial["Capital Total"].iloc[-1]
        capital_anterior = historial["Capital Total"].iloc[-2]
        ingreso_actual = historial["Ingreso Pasivo"].iloc[-1]
        ingreso_anterior = historial["Ingreso Pasivo"].iloc[-2]
        delta_capital = ((capital_actual - capital_anterior) / capital_anterior) * 100 if capital_anterior > 0 else 0
        delta_ingreso = ((ingreso_actual - ingreso_anterior) / ingreso_anterior) * 100 if ingreso_anterior > 0 else 0
    else:
        capital_actual = historial["Capital Total"].iloc[-1]
        ingreso_actual = historial["Ingreso Pasivo"].iloc[-1]
        delta_capital = 0
        delta_ingreso = 0

    # Métricas principales
    st.markdown("### 📊 Indicadores Actuales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color_capital = '#43e97b' if delta_capital > 0 else '#f5576c' if delta_capital < 0 else '#667eea'
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_capital} 0%, #38f9d7 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>💰 Capital Total</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(capital_actual)}</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    {delta_capital:+.2f}% vs mes anterior
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_ingreso = '#43e97b' if delta_ingreso > 0 else '#f5576c' if delta_ingreso < 0 else '#667eea'
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color_ingreso} 0%, #fa709a 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📈 Ingreso Pasivo</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{formato_pesos(ingreso_actual)}</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    {delta_ingreso:+.2f}% vs mes anterior
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if len(historial) > 1:
            crecimiento_promedio_capital = historial["Capital Total"].pct_change().mean() * 100
        else:
            crecimiento_promedio_capital = 0
        
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📊 Crecimiento Promedio</p>
                <h2 style='color: white; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{crecimiento_promedio_capital:.2f}%</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    Capital mensual
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        meses_registrados = len(historial)
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(80,80,80,0.8); margin: 0; font-size: 0.9rem;'>📅 Meses Registrados</p>
                <h2 style='color: #333; margin: 0.5rem 0 0 0; font-size: 1.8rem;'>{meses_registrados}</h2>
                <p style='color: rgba(80,80,80,0.8); margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
                    snapshots guardados
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Predicción para los próximos 6 meses
    st.markdown("### 🔮 Proyección a 6 Meses")

    meses_pred = 6
    fechas_existentes = list(historial["Fecha"])
    X = np.arange(len(fechas_existentes)).reshape(-1, 1)

    # Capital Total
    y_capital = historial["Capital Total"].values
    modelo_capital = LinearRegression().fit(X, y_capital)
    X_pred = np.arange(len(fechas_existentes), len(fechas_existentes) + meses_pred).reshape(-1, 1)
    capital_pred = modelo_capital.predict(X_pred)

    # Ingreso Pasivo
    y_ingreso = historial["Ingreso Pasivo"].values
    modelo_ingreso = LinearRegression().fit(X, y_ingreso)
    ingreso_pred = modelo_ingreso.predict(X_pred)

    # Fechas futuras
    ult_fecha = datetime.strptime(fechas_existentes[-1], "%Y-%m")
    fechas_pred = []
    for i in range(meses_pred):
        mes = ult_fecha.month + i + 1
        anio = ult_fecha.year + (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        fechas_pred.append(f"{anio}-{mes:02d}")

    # Gráfico principal con Plotly
    fig = go.Figure()

    # Líneas históricas
    fig.add_trace(go.Scatter(
        x=historial["Fecha"],
        y=historial["Capital Total"],
        name='Capital Total',
        line=dict(color='#1f77b4', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#1f77b4'),
        hovertemplate='<b>%{x}</b><br>Capital: %{y:,.0f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=historial["Fecha"],
        y=historial["Ingreso Pasivo"],
        name='Ingreso Pasivo',
        line=dict(color='#2ca02c', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#2ca02c'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Ingreso: %{y:,.0f}<extra></extra>'
    ))

    # Líneas de predicción
    fig.add_trace(go.Scatter(
        x=fechas_pred,
        y=capital_pred,
        name='Predicción Capital',
        line=dict(color='#1f77b4', width=2, dash='dash'),
        mode='lines+markers',
        marker=dict(size=6, color='#1f77b4', symbol='square'),
        hovertemplate='<b>%{x}</b><br>Capital proyectado: %{y:,.0f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=fechas_pred,
        y=ingreso_pred,
        name='Predicción Ingreso',
        line=dict(color='#2ca02c', width=2, dash='dash'),
        mode='lines+markers',
        marker=dict(size=6, color='#2ca02c', symbol='square'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Ingreso proyectado: %{y:,.0f}<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title={
            'text': 'Evolución y Proyección del Portafolio',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, color='#000', family='Arial Black')
        },
        xaxis=dict(
            title=dict(text='Fecha', font=dict(size=16, color='#000')),
            tickfont=dict(size=13, color='#000'),
            showgrid=True,
            gridcolor='#d0d0d0',
            linecolor='#000',
            linewidth=2,
            showline=True,
            mirror=True
        ),
        yaxis=dict(
            title=dict(text='Capital Total (COP)', font=dict(color='#1f77b4', size=16)),
            tickfont=dict(color='#1f77b4', size=13),
            tickformat='$,.0f',
            showgrid=True,
            gridcolor='#e0e0e0',
            linecolor='#1f77b4',
            linewidth=2,
            showline=True
        ),
        yaxis2=dict(
            title=dict(text='Ingreso Pasivo (COP)', font=dict(color='#2ca02c', size=16)),
            tickfont=dict(color='#2ca02c', size=13),
            overlaying='y',
            side='right',
            tickformat='$,.0f',
            linecolor='#2ca02c',
            linewidth=2,
            showline=True
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#000',
            borderwidth=2,
            font=dict(size=13, color='#000')
        ),
        height=550,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#000', size=13)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de crecimiento mensual
    if len(historial) > 1:
        st.markdown("### 📊 Crecimiento Mensual (%)")
        
        historial["Crecimiento Capital"] = historial["Capital Total"].pct_change() * 100
        historial["Crecimiento Ingreso"] = historial["Ingreso Pasivo"].pct_change() * 100

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=historial["Fecha"],
            y=historial["Crecimiento Capital"],
            name='Crecimiento Capital (%)',
            marker_color='#1f77b4',
            hovertemplate='<b>%{x}</b><br>Crecimiento: %{y:.2f}%<extra></extra>'
        ))

        fig2.add_trace(go.Bar(
            x=historial["Fecha"],
            y=historial["Crecimiento Ingreso"],
            name='Crecimiento Ingreso (%)',
            marker_color='#2ca02c',
            hovertemplate='<b>%{x}</b><br>Crecimiento: %{y:.2f}%<extra></extra>'
        ))

        fig2.add_hline(y=0, line_color='#333', line_width=2)

        fig2.update_layout(
            title=dict(text='Variación Porcentual Mensual', font=dict(size=20, color='#000', family='Arial Black')),
            xaxis=dict(
                title=dict(text='Fecha', font=dict(size=16, color='#000')),
                tickfont=dict(size=13, color='#000'),
                showgrid=True,
                gridcolor='#e0e0e0',
                linecolor='#000',
                linewidth=2,
                showline=True,
                mirror=True
            ),
            yaxis=dict(
                title=dict(text='Crecimiento (%)', font=dict(size=16, color='#000')),
                tickfont=dict(size=13, color='#000'),
                showgrid=True,
                gridcolor='#e0e0e0',
                linecolor='#000',
                linewidth=2,
                showline=True,
                mirror=True
            ),
            barmode='group',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#000', size=13),
            legend=dict(
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#000',
                borderwidth=2,
                font=dict(size=13, color='#000')
            )
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Tabla de predicción
    st.markdown("### 📈 Tabla de Proyección (6 meses)")
    
    pred_df = pd.DataFrame({
        "📅 Fecha": fechas_pred,
        "💰 Capital Total": [formato_pesos(x) for x in capital_pred],
        "📈 Ingreso Pasivo": [formato_pesos(x) for x in ingreso_pred]
    })
    
    st.dataframe(pred_df, use_container_width=True, hide_index=True)

    # Tabla histórica
    st.markdown("### 📊 Registro Histórico Completo")
    
    tabla = historial.copy()
    tabla["Capital Total"] = tabla["Capital Total"].apply(formato_pesos)
    tabla["Ingreso Pasivo"] = tabla["Ingreso Pasivo"].apply(formato_pesos)
    tabla = tabla.rename(columns={
        "Fecha": "📅 Fecha",
        "Capital Total": "💰 Capital Total",
        "Ingreso Pasivo": "📈 Ingreso Pasivo"
    })
    
    st.dataframe(tabla, use_container_width=True, hide_index=True, height=300)

    # Acciones
    st.markdown("### 🔧 Acciones")
    
    col_action1, col_action2 = st.columns(2)
    
    with col_action1:
        csv = historial.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar Historial CSV",
            data=csv,
            file_name="historial_snapshots.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_action2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                        padding: 1rem; border-radius: 10px;'>
                <p style='margin: 0; color: #333; font-weight: 600; text-align: center;'>
                    ⚠️ Zona de Peligro
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Confirmación para eliminar
    if st.checkbox("⚠️ Confirmo que deseo eliminar el historial completo"):
        if st.button("🗑️ Eliminar Historial", type="primary", use_container_width=True):
            os.remove(RUTA_HISTORIAL)
            st.markdown("""
                <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                            padding: 1rem; border-radius: 10px; margin: 1rem 0;'>
                    <p style='margin: 0; color: #333; font-weight: 600;'>
                        🗑️ Historial eliminado correctamente
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.rerun()