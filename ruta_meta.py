import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px
import json
import os

META_PARAMS_FILE = "ruta_meta_params.json"

def formato_pesos(valor):
    """Formatea valores numéricos como moneda colombiana"""
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formato_tiempo(meses_total):
    """Convierte meses a formato años-meses-días con precisión"""
    if meses_total == float('inf'):
        return "50+ años", ""
    
    meses_int = int(meses_total)
    años = meses_int // 12
    meses = meses_int % 12
    dias = int(round((meses_total - meses_int) * 30))
    
    partes = []
    if años > 0:
        partes.append(f"{años}a")
    if meses > 0 or años == 0:  # Mostrar meses si no hay años o si es el único componente
        partes.append(f"{meses}m")
    if dias > 0 and meses_total < 12:  # Mostrar días solo para plazos cortos
        partes.append(f"{dias}d")
    
    return " ".join(partes), dias

def load_meta_params():
    """Carga los parámetros guardados desde archivo JSON"""
    if os.path.exists(META_PARAMS_FILE):
        with open(META_PARAMS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {
                    "capital_meta": 50_000_000.0,
                    "ingreso_pasivo_objetivo": 1_000_000.0,
                    "inversion_mensual": 1_800_000.0
                }
    return {
        "capital_meta": 50_000_000.0,
        "ingreso_pasivo_objetivo": 1_000_000.0,
        "inversion_mensual": 1_800_000.0
    }

def save_meta_params(params_dict):
    """Guarda los parámetros en archivo JSON"""
    with open(META_PARAMS_FILE, 'w') as f:
        json.dump(params_dict, f, indent=4)

def ruta_hacia_meta(df=None, capital=None, rentabilidad=None, capital_objetivo=None, ingreso_pasivo_objetivo=None, inversion_mensual=None):
    # CSS mejorado para UX moderna
    st.markdown("""
    <style>
    .main-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        margin: 30px 0;
    }
    
    .config-container {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(102, 126, 234, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .progress-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateX(5px);
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(129, 199, 132, 0.1) 100%);
        border-left-color: #4CAF50;
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 183, 77, 0.1) 100%);
        border-left-color: #FF9800;
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(239, 83, 80, 0.1) 100%);
        border-left-color: #F44336;
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(100, 181, 246, 0.1) 100%);
        border-left-color: #2196F3;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #667eea;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    .comparison-table th, .comparison-table td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .comparison-table th {
        background-color: rgba(102, 126, 234, 0.1);
        font-weight: 600;
    }
    
    .comparison-table tr:hover {
        background-color: rgba(102, 126, 234, 0.05);
    }
    
    .time-metric {
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea;
    }
    
    .time-detail {
        font-size: 0.9rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-section">Camino a tu Meta Financiera</h1>', unsafe_allow_html=True)

    # Procesar datos
    if df is not None:
        df = df.copy()
        df['Dinero'] = pd.to_numeric(df['Dinero'].replace('[\$,]', '', regex=True), errors='coerce')
        df['Interes Mensual'] = pd.to_numeric(df['Interes Mensual'], errors='coerce').fillna(0)
        
        # Corrección: Ahora se calcula el capital productivo.
        capital_productivo = df[df['Interes Mensual'] > 0]['Dinero'].sum()
        capital = df['Dinero'].sum()
        ingreso_pasivo = df['Interes Mensual'].sum()
        
        # Corrección: La rentabilidad anual se calcula sobre el capital productivo.
        rentabilidad_anual = ((ingreso_pasivo * 12) / capital_productivo) * 100 if capital_productivo > 0 else 0
    else:
        rentabilidad_anual = rentabilidad

    saved_params = load_meta_params()

    # Configuración en un contenedor elegante
    with st.container():
        st.markdown('<div class="config-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header">Configuración de Metas</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            capital_meta_input = st.number_input(
                "Capital Meta (COP)",
                value=float(saved_params.get("capital_meta", capital_objetivo or 50_000_000.0)),
                step=1_000_000.0,
                format="%.0f",
                key="capital_meta_input_ruta",
                help="El monto total que deseas alcanzar"
            )
        
        with col2:
            ingreso_pasivo_objetivo_input = st.number_input(
                "Ingreso Pasivo Mensual (COP)",
                value=float(saved_params.get("ingreso_pasivo_objetivo", ingreso_pasivo_objetivo or 1_000_000.0)),
                step=100_000.0,
                format="%.0f",
                key="ingreso_pasivo_objetivo_input_ruta",
                help="El ingreso mensual que deseas generar"
            )
        
        with col3:
            inversion_mensual_input = st.number_input(
                "Inversión Mensual Adicional (COP)",
                min_value=0.0,
                value=float(saved_params.get("inversion_mensual", inversion_mensual or 1_800_000.0)),
                step=100_000.0,
                format="%.0f",
                key="inversion_mensual_input_ruta",
                help="Cuánto planeas invertir cada mes"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Guardar parámetros
    st.session_state.capital_meta_informe = capital_meta_input
    st.session_state.inversion_mensual_informe = inversion_mensual_input
    st.session_state.ingreso_pasivo_objetivo_informe = ingreso_pasivo_objetivo_input

    save_meta_params({
        "capital_meta": capital_meta_input,
        "ingreso_pasivo_objetivo": ingreso_pasivo_objetivo_input,
        "inversion_mensual": inversion_mensual_input
    })

    # Cálculos
    rentabilidad_anual_decimal = rentabilidad_anual / 100
    
    # Cálculo con interés
    denominator = inversion_mensual_input + (capital * rentabilidad_anual_decimal / 12)
    
    if denominator > 0 and capital < capital_meta_input:
        meses_para_capital_meta_con_interes = (capital_meta_input - capital) / denominator
        if meses_para_capital_meta_con_interes < 0:
            meses_para_capital_meta_con_interes = 0.0
    elif capital >= capital_meta_input:
        meses_para_capital_meta_con_interes = 0.0
    else:
        meses_para_capital_meta_con_interes = float('inf')
    
    # Cálculo sin interés (solo aportes mensuales)
    if inversion_mensual_input > 0 and capital < capital_meta_input:
        meses_para_capital_meta_sin_interes = (capital_meta_input - capital) / inversion_mensual_input
        if meses_para_capital_meta_sin_interes < 0:
            meses_para_capital_meta_sin_interes = 0.0
    elif capital >= capital_meta_input:
        meses_para_capital_meta_sin_interes = 0.0
    else:
        meses_para_capital_meta_sin_interes = float('inf')

    # Progreso visual mejorado
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Estado de tu Avance</h3>', unsafe_allow_html=True)
    
    porcentaje_actual = capital / capital_meta_input if capital_meta_input > 0 else 0
    
    # Barra de progreso moderna
    progress_col1, progress_col2 = st.columns([3, 1])
    with progress_col1:
        st.progress(min(porcentaje_actual, 1.0))
    with progress_col2:
        st.metric("Progreso", f"{porcentaje_actual:.1%}")

    # Mensajes motivacionales con diseño mejorado
    if porcentaje_actual >= 1:
        st.markdown('<div class="metric-card success-card">🎉 <strong>¡Meta alcanzada!</strong> Has superado el 100% del capital objetivo. ¡Sigue soñando en grande!</div>', unsafe_allow_html=True)
    elif porcentaje_actual >= 0.9:
        st.markdown('<div class="metric-card success-card">🚀 <strong>¡Casi ahí!</strong> Estás al 90% o más de tu meta. ¡Muy cerca de lograrlo!</div>', unsafe_allow_html=True)
    elif porcentaje_actual >= 0.75:
        st.markdown('<div class="metric-card info-card">📈 <strong>Excelente progreso!</strong> Has alcanzado al menos el 75% del capital objetivo.</div>', unsafe_allow_html=True)
    elif porcentaje_actual >= 0.5:
        st.markdown('<div class="metric-card warning-card">⚡ <strong>A mitad de camino.</strong> Considera mantener o aumentar tu inversión para llegar más rápido.</div>', unsafe_allow_html=True)
    elif porcentaje_actual >= 0.25:
        st.markdown('<div class="metric-card warning-card">💪 <strong>¡Vas bien!</strong> Has llegado al 25% de tu meta. ¡No te detengas, cada aporte cuenta!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card error-card">🎯 <strong>¡Tú puedes!</strong> Estás lejos de la meta. Revisa tu rentabilidad o incrementa tu aporte mensual.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Métricas clave en tarjetas
    st.markdown('<h3 class="section-header">Métricas Financieras</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Capital Actual",
            formato_pesos(capital),
            delta=f"{porcentaje_actual:.1%} de la meta"
        )
    
    with col2:
        st.metric(
            "Rentabilidad Anual Capital Productivo",
            f"{rentabilidad_anual:.2f}%",
            delta="Estimada"
        )
    
    with col3:
        tiempo_con_interes, dias_con = formato_tiempo(meses_para_capital_meta_con_interes)
        st.metric(
            "Tiempo con Interés",
            tiempo_con_interes,
            delta=f"~{dias_con}d" if dias_con > 0 and meses_para_capital_meta_con_interes < 12 else "Con interés compuesto"
        )
    
    with col4:
        tiempo_sin_interes, dias_sin = formato_tiempo(meses_para_capital_meta_sin_interes)
        st.metric(
            "Tiempo sin Interés",
            tiempo_sin_interes,
            delta=f"~{dias_sin}d" if dias_sin > 0 and meses_para_capital_meta_sin_interes < 12 else "Solo con aportes"
        )

    # Comparación de escenarios
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">Comparación de Escenarios</h3>', unsafe_allow_html=True)
    
    if meses_para_capital_meta_con_interes != float('inf') and meses_para_capital_meta_sin_interes != float('inf'):
        diferencia_meses = abs(meses_para_capital_meta_sin_interes - meses_para_capital_meta_con_interes)
        diferencia_formateada, _ = formato_tiempo(diferencia_meses)
        
        if diferencia_meses > 0:
            st.markdown(f"""
            <table class="comparison-table">
                <tr>
                    <th>Escenario</th>
                    <th>Tiempo Estimado</th>
                    <th>Diferencia</th>
                </tr>
                <tr>
                    <td>Con interés</td>
                    <td>{tiempo_con_interes}</td>
                    <td>-</td>
                </tr>
                <tr>
                    <td>Solo con aportes</td>
                    <td>{tiempo_sin_interes}</td>
                    <td>{diferencia_formateada} más</td>
                </tr>
            </table>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            **💡 El interés  te ahorra aproximadamente {diferencia_formateada}** en alcanzar tu meta financiera.
            """)
        else:
            st.markdown("""
            <div class="metric-card info-card">
                ℹ️ Con tu configuración actual, el interés no está afectando significativamente tu tiempo para alcanzar la meta.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="metric-card warning-card">
            ⚠️ No se puede calcular la comparación porque uno o ambos escenarios exceden el límite de tiempo.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Gráfico interactivo mejorado
    if capital < capital_meta_input and meses_para_capital_meta_con_interes != float('inf'):
        st.markdown('<h3 class="section-header">Proyección de Crecimiento</h3>', unsafe_allow_html=True)
        
        max_months = min(int(max(meses_para_capital_meta_con_interes, meses_para_capital_meta_sin_interes)) + 12, 600)
        meses = list(range(0, max_months + 1, 3))  # Cada 3 meses para mejor rendimiento
        
        capital_con_interes = []
        capital_sin_interes = []
        
        for m in meses:
            # Con interés
            cap_interes = capital + (inversion_mensual_input * m) + (capital * rentabilidad_anual_decimal * m / 12)
            capital_con_interes.append(cap_interes)
            
            # Sin interés
            cap_sin_interes = capital + (inversion_mensual_input * m)
            capital_sin_interes.append(cap_sin_interes)
        
        fig = go.Figure()
        
        # Línea con interés
        fig.add_trace(go.Scatter(
            x=meses,
            y=capital_con_interes,
            name='Con Interés',
            line=dict(color='#667eea', width=3),
            fill='tonexty' if len(capital_sin_interes) > 0 else None
        ))
        
        # Línea sin interés
        if inversion_mensual_input > 0:
            fig.add_trace(go.Scatter(
                x=meses,
                y=capital_sin_interes,
                name='Solo Aportes',
                line=dict(color='#ff7f50', width=2, dash='dash')
            ))
        
        # Línea de meta
        fig.add_hline(
            y=capital_meta_input,
            line_dash="dot",
            line_color="red",
            annotation_text="Meta"
        )
        
        fig.update_layout(
            title="Evolución Proyectada del Capital",
            xaxis_title="Meses",
            yaxis_title="Capital (COP)",
            template="plotly_white",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(tickformat="$,.0f")
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Insights y explicación
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-header">¿Qué significa esto?</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **⏰ Tiempo con interés:**
        - Considera tus aportes mensuales + ganancias por intereses
        - Muestra años (a), meses (m) y días (d) cuando aplica
        - El interés compuesto acelera el crecimiento
        """)
    
    with col2:
        st.markdown("""
        **⏳ Tiempo sin interés:**
        - Solo considera tus aportes mensuales
        - Útil para comparar el valor del interés
        - Días solo se muestran para plazos <1 año
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla resumen compacta
    if meses_para_capital_meta_con_interes != float('inf') and meses_para_capital_meta_con_interes <= 240:  # Solo si es menos de 20 años
        st.markdown('<h3 class="section-header">Hitos Importantes</h3>', unsafe_allow_html=True)
        
        hitos = [1, 3, 6, 12, 24, 36, int(meses_para_capital_meta_con_interes)]
        hitos = sorted(list(set([h for h in hitos if h <= meses_para_capital_meta_con_interes])))
        
        tabla_data = []
        for mes in hitos:
            capital_proyectado = capital + (inversion_mensual_input * mes) + (capital * rentabilidad_anual_decimal * mes / 12)
            ingreso_proyectado = capital_proyectado * (rentabilidad_anual_decimal / 12)
            
            tiempo_formateado, _ = formato_tiempo(mes)
            
            tabla_data.append({
                "Periodo": tiempo_formateado,
                "Capital": formato_pesos(capital_proyectado),
                "Ingreso Mensual": formato_pesos(ingreso_proyectado),
                "% de Meta": f"{(capital_proyectado/capital_meta_input)*100:.1f}%"
            })
        
        df_tabla = pd.DataFrame(tabla_data)
        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Periodo": "Tiempo",
                "Capital": st.column_config.NumberColumn(format="$%.0f"),
                "Ingreso Mensual": st.column_config.NumberColumn(format="$%.0f"),
                "% de Meta": st.column_config.ProgressColumn(format="%.1f%%")
            }
        )