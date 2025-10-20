import streamlit as st
import pandas as pd
import os
import math
import plotly.express as px
import plotly.graph_objects as go

# --- Funciones Auxiliares Generales ---

def formato_pesos(valor):
    """
    Formatea un valor numérico a una cadena de texto con formato de pesos colombianos.
    Ej: 1234567.89 -> $1.234.567 (redondea a entero sin decimales)
    """
    if isinstance(valor, (int, float)):
        return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)

def formato_porcentaje(valor):
    """
    Formatea un valor numérico a una cadena de texto con formato de porcentaje.
    Ej: 20.5 -> 20.50 %
    """
    if isinstance(valor, (int, float)):
        return f"{valor:.2f} %"
    return str(valor)

def clean_df_for_analysis(df):
    """
    Limpia y convierte a numéricas las columnas relevantes de un DataFrame
    para análisis financiero, manejando símbolos de moneda y separadores.
    """
    df_cleaned = df.copy()
    
    cols_to_clean = ['Dinero', 'Interes anual (%)', 'Interes Mensual']
    
    for col in cols_to_clean:
        if col in df_cleaned.columns:
            # Primero, elimina símbolos de moneda, espacios y espacios no separadores
            cleaned_series = df_cleaned[col].astype(str) \
                                          .str.replace('$', '', regex=False) \
                                          .str.replace(' ', '', regex=False) \
                                          .str.replace('\xa0', '', regex=False) # Elimina el espacio no separador
            
            # Ahora, maneja los separadores de miles y decimales según el formato de entrada (coma para miles, punto para decimales)
            # Elimina los separadores de miles (comas)
            cleaned_series = cleaned_series.str.replace(',', '', regex=False)
            # El punto ya es el separador decimal, no es necesario reemplazarlo.
            
            df_cleaned[col] = pd.to_numeric(cleaned_series, errors='coerce').fillna(0.0) # Convierte a numérico, rellena NaNs con 0
            
    return df_cleaned

# --- Funciones para la Evaluación General de Préstamos ---

def calcular_cuota_francesa(monto, tasa_mensual_porcentaje, plazo_meses):
    """
    Calcula la cuota fija mensual de un préstamo usando la fórmula de amortización francesa.
    """
    if tasa_mensual_porcentaje == 0:
        if plazo_meses <= 0:
            return float('inf')
        return monto / plazo_meses
    
    tasa_mensual_decimal = tasa_mensual_porcentaje / 100
    try:
        cuota = monto * (tasa_mensual_decimal / (1 - (1 + tasa_mensual_decimal) ** -plazo_meses))
        return cuota
    except ZeroDivisionError: 
        return float('inf')

def calcular_cuota_interes_fijo(monto, tasa_mensual_porcentaje, plazo_meses):
    """
    Calcula la cuota mensual para un préstamo donde el monto de interés es fijo cada mes.
    """
    if plazo_meses <= 0:
        return float('inf')

    tasa_mensual_decimal = tasa_mensual_porcentaje / 100
    
    interes_fijo_mensual = monto * tasa_mensual_decimal
    abono_capital_fijo_mensual = monto / plazo_meses
    
    cuota_total_fija = interes_fijo_mensual + abono_capital_fijo_mensual
    return cuota_total_fija

# --- FUNCIONES PARA INTERÉS SIMPLE (ANÁLISIS DETALLADO) ---

def calcular_cuota_interes_simple_fijo(monto, tasa_mensual_porcentaje, plazo_meses):
    """
    Calcula la cuota mensual para un préstamo con INTERÉS SIMPLE FIJO.
    El interés se calcula sobre el monto inicial durante todo el préstamo.
    """
    if plazo_meses <= 0:
        return float('inf')
    
    # Interés simple total
    interes_total = monto * (tasa_mensual_porcentaje / 100) * plazo_meses
    
    # Cuota fija = (Capital + Intereses totales) / Plazo
    cuota_fija = (monto + interes_total) / plazo_meses
    
    return cuota_fija

def calcular_cuota_capital_fijo(monto, tasa_mensual_porcentaje, plazo_meses):
    """
    Calcula cuotas variables donde el capital es fijo pero el interés simple
    se calcula sobre el saldo pendiente cada mes.
    """
    if plazo_meses <= 0:
        return None
    
    cuotas = []
    saldo_pendiente = monto
    capital_fijo_mensual = monto / plazo_meses
    
    for mes in range(1, int(plazo_meses) + 1):
        interes_mensual = saldo_pendiente * (tasa_mensual_porcentaje / 100)
        cuota_total = capital_fijo_mensual + interes_mensual
        saldo_pendiente -= capital_fijo_mensual
        
        cuotas.append({
            'mes': mes,
            'cuota': cuota_total,
            'interes': interes_mensual,
            'capital': capital_fijo_mensual,
            'saldo': max(0, saldo_pendiente)
        })
    
    return cuotas

def calcular_cuota_capital_al_final(monto, tasa_mensual_porcentaje, plazo_meses):
    """
    Calcula cuotas para modalidad "Capital al Final".
    Solo se pagan intereses durante el plazo, el capital se cancela al final.
    """
    if plazo_meses <= 0:
        return None
    
    cuotas = []
    interes_mensual = monto * (tasa_mensual_porcentaje / 100)
    
    # Cuotas 1 a n-1: solo intereses
    for mes in range(1, int(plazo_meses)):
        cuotas.append({
            'mes': mes,
            'cuota': interes_mensual,
            'interes': interes_mensual,
            'capital': 0,
            'saldo': monto
        })
    
    # Última cuota: interés + capital total
    cuota_final = interes_mensual + monto
    cuotas.append({
        'mes': int(plazo_meses),
        'cuota': cuota_final,
        'interes': interes_mensual,
        'capital': monto,
        'saldo': 0
    })
    
    return cuotas

def riesgo_por_actividad(actividad):
    """
    Asigna un nivel de riesgo a una actividad económica.
    """
    riesgos = {
        "Empleado": "Bajo",
        "Independiente": "Medio",
        "Informal": "Alto",
        "Desempleado": "Crítico",
        "Otro": "Desconocido"
    }
    return riesgos.get(actividad, "Desconocido")

def guardar_evaluacion(datos):
    """
    Guarda una evaluación de préstamo en un archivo CSV.
    """
    archivo = "historial_prestamos.csv"
    if os.path.exists(archivo):
        df_existente = pd.read_csv(archivo)
        df = pd.concat([df_existente, pd.DataFrame([datos])], ignore_index=True)
    else:
        df = pd.DataFrame([datos])
    df.to_csv(archivo, index=False)

def cargar_evaluaciones_guardadas():
    """
    Carga el historial de evaluaciones de préstamos desde un archivo CSV.
    """
    archivo = "historial_prestamos.csv"
    if os.path.exists(archivo):
        return pd.read_csv(archivo)
    else:
        return pd.DataFrame()

# --- Función para la Evaluación General de Préstamos ---
def mostrar_evaluacion_general():
    st.header("🤝 Evaluación General de Préstamo")
    st.markdown("""
    Esta herramienta te ayuda a estimar la viabilidad de un préstamo
    analizando tus ingresos, deudas y la cuota del nuevo crédito.
    """)

    # --- Entradas de Usuario ---
    nombre = st.text_input("👤 **Nombre del solicitante**", key="nombre_solicitante_gen")
    ingresos = st.number_input("💰 **Ingresos mensuales (COP)**", min_value=0.0, step=100000.0, format="%.0f", key="ingresos_mensuales_gen")
    deudas_actuales = st.number_input("📉 **Total de deudas actuales (cuotas mensuales COP)**", min_value=0.0, step=100000.0, format="%.0f", key="deudas_actuales_gen")
    monto_prestamo = st.number_input("💲 **Monto del préstamo solicitado (COP)**", min_value=0.0, step=100000.0, format="%.0f", key="monto_solicitado_gen")
    tasa_interes = st.number_input("📈 **Tasa mensual de interés (%)**", min_value=0.0, step=0.1, format="%.2f", key="tasa_interes_gen")
    plazo = st.number_input("📆 **Plazo del préstamo (meses)**", min_value=1.0, value=1.0, step=1.0, format="%.0f", key="plazo_meses_gen")
    actividad = st.selectbox("👷 **Actividad económica**", ["Empleado", "Independiente", "Informal", "Desempleado", "Otro"], key="actividad_economica_gen")

    st.markdown("---")

    # --- Lógica de Evaluación ---
    def clasificar_endeudamiento(ingresos_totales, total_cuotas):
        if ingresos_totales <= 0:
            return "No se puede evaluar sin ingresos."

        porcentaje = (total_cuotas / ingresos_totales) * 100

        if porcentaje <= 20:
            return f"**Aprobado** ({porcentaje:.2f}%): Salud financiera óptima."
        elif porcentaje <= 40:
            return f"**Aprobado con precaución** ({porcentaje:.2f}%): Riesgo moderado de sobreendeudamiento. Considera tus límites."
        elif porcentaje <= 60:
            return f"**Riesgo alto** ({porcentaje:.2f}%): Podrías enfrentar dificultades para cumplir con los pagos. Reevalúa."
        else:
            return f"**Riesgo crítico** ({porcentaje:.2f}%): Tu capacidad de pago está muy comprometida. No se recomienda otorgar el préstamo."

    if st.button("🔍 Evaluar Solicitud de Préstamo", key="evaluar_btn_gen"):
        if monto_prestamo <= 0 or plazo <= 0:
            st.error("Por favor, ingresa un monto de préstamo y un plazo válidos (> 0).")
            return

        cuota_nueva = calcular_cuota_francesa(monto_prestamo, tasa_interes, plazo)
        
        st.markdown(f"**Cuota estimada del nuevo préstamo:** {formato_pesos(cuota_nueva)}")
        
        total_cuotas_mensuales_con_nuevo = deudas_actuales + cuota_nueva
        
        porcentaje_endeudamiento = (total_cuotas_mensuales_con_nuevo / ingresos) * 100 if ingresos > 0 else 0

        resultado_evaluacion = clasificar_endeudamiento(ingresos, total_cuotas_mensuales_con_nuevo)
        riesgo_actividad_resultado = riesgo_por_actividad(actividad)

        st.subheader("✅ Resultado de Evaluación de Crédito")
        if "Aprobado" in resultado_evaluacion:
            st.success(resultado_evaluacion)
        elif "precaución" in resultado_evaluacion:
            st.warning(resultado_evaluacion)
        else:
            st.error(resultado_evaluacion)

        st.subheader("⚠️ Riesgo por Actividad Económica")
        st.warning(f"La actividad seleccionada tiene un nivel de riesgo **{riesgo_actividad_resultado}**.")

        # --- Guardar Evaluación ---
        if nombre:
            datos = {
                "Nombre": nombre,
                "Ingresos": ingresos,
                "Deudas Actuales": deudas_actuales,
                "Monto Prestamo": monto_prestamo,
                "Tasa (%)": tasa_interes,
                "Plazo (meses)": plazo,
                "Cuota Estimada": cuota_nueva,
                "% Endeudamiento": porcentaje_endeudamiento,
                "Resultado": resultado_evaluacion,
                "Riesgo Actividad": riesgo_actividad_resultado
            }
            guardar_evaluacion(datos)
            st.success("Evaluación guardada exitosamente en el historial.")
        else:
            st.warning("🚨 **¡No se guardó la evaluación!** Ingresa un nombre para el solicitante si deseas registrarla.")

    st.markdown("---")

    # --- Tablas de Referencia y Historial ---
    with st.expander("📊 **Ver tabla de evaluación por rangos de endeudamiento**"):
        st.markdown("""
        | **% del ingreso destinado a deudas** | **Evaluación** | **Recomendación** |
        |--------------------------------------|-----------------------------|-----------------------------------------------|
        | 0% - 20%                             | Aprobado                    | Salud financiera adecuada.                    |
        | 21% - 40%                            | Aprobado con precaución     | Riesgo moderado de sobreendeudamiento.        |
        | 41% - 60%                            | Riesgo alto                 | Dificultad probable para pagar.               |
        | 61% - 100%+                          | Riesgo crítico              | Capacidad de pago muy comprometida.           |

        <br>

        | **Actividad Económica** | **Nivel de Riesgo** |
        |-------------------------|---------------------|
        | Empleado                | Bajo                |
        | Independiente           | Medio               |
        | Informal                | Alto                |
        | Desempleado             | Crítico             |
        | Otro                    | Desconocido         |
        """, unsafe_allow_html=True)

    with st.expander("🗂 **Ver historial de evaluaciones registradas**"):
        df_historial = cargar_evaluaciones_guardadas()
        if df_historial.empty:
            st.info("No hay evaluaciones registradas aún. ¡Realiza una para empezar!")
        else:
            df_display = df_historial.copy() 

            columnas_moneda = ["Ingresos", "Deudas Actuales", "Monto Prestamo", "Cuota Estimada"]
            for col in columnas_moneda:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(formato_pesos)

            columnas_porcentaje = ["Tasa (%)", "% Endeudamiento"]
            for col in columnas_porcentaje:
                if col in df_display.columns:
                    df_display[col] = df_display[col].apply(formato_porcentaje)
            
            st.dataframe(df_display)

# --- Función MEJORADA para el Análisis Detallado de Préstamos (INTERÉS SIMPLE) ---
def mostrar_analisis_detalle():
    st.header("🔍 Análisis Detallado de Préstamo - Interés Simple")
    st.markdown("""
    Herramienta para analizar préstamos con **INTERÉS SIMPLE ÚNICAMENTE**.
    No se utiliza interés compuesto en ningún cálculo.
    """)

    # --- Parámetros del Préstamo ---
    st.subheader("📝 Parámetros del Préstamo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monto_prestado = st.number_input(
            "💲 Monto del préstamo (COP)",
            min_value=1_000_00.0,
            value=7_000_000.0,
            step=100_000.0,
            format="%.0f",
            key="monto_prestamo_analisis_det"
        )
        
        plazo_meses = st.number_input(
            "📅 Plazo del préstamo (meses)",
            min_value=1.0,
            value=24.0,
            step=1.0,
            format="%.0f",
            key="plazo_meses_analisis_det"
        )
    
    with col2:
        tasa_interes_mensual_porcentaje = st.number_input(
            "📈 Tasa de interés simple mensual (%)",
            min_value=0.00001,
            value=1.36,
            step=0.01,
            format="%.5f",
            key="tasa_interes_analisis_det"
        )
        
        # Tipo de amortización para interés simple - ACTUALIZADO
        tipo_amortizacion = st.selectbox(
            "📋 Modalidad de pago:",
            [
                "Cuota Fija (Interés Simple Total)",
                "Cuota Variable (Capital Fijo + Interés s/Saldo)",
                "Capital al Final (Solo Intereses + Capital Final)"
            ],
            key="tipo_amortizacion_selector",
            help="""
            - **Cuota Fija:** Interés simple total distribuido en cuotas iguales
            - **Cuota Variable:** Capital fijo + interés simple sobre saldo pendiente
            - **Capital al Final:** Solo se pagan intereses mensualmente, el capital se cancela al final
            """
        )

    # --- Cálculos de Interés Simple ---
    if tipo_amortizacion == "Cuota Fija (Interés Simple Total)":
        # Modalidad 1: Interés simple total calculado al inicio
        interes_total = monto_prestado * (tasa_interes_mensual_porcentaje / 100) * plazo_meses
        cuota_mensual = (monto_prestado + interes_total) / plazo_meses
        
        # Tabla de amortización con cuota fija
        tabla_amortizacion = []
        capital_mensual = monto_prestado / plazo_meses
        interes_mensual = interes_total / plazo_meses
        saldo_restante = monto_prestado
        capital_acumulado = 0
        
        for mes in range(1, int(plazo_meses) + 1):
            saldo_restante = max(0, saldo_restante - capital_mensual)
            capital_acumulado += capital_mensual
            porcentaje_capital = (capital_acumulado / monto_prestado) * 100
            
            tabla_amortizacion.append({
                "Mes": mes,
                "Cuota": round(cuota_mensual, 0),
                "Interés": round(interes_mensual, 0),
                "Capital": round(capital_mensual, 0),
                "Saldo": round(saldo_restante, 0),
                "Capital Acum.": round(capital_acumulado, 0),
                "% Capital": round(porcentaje_capital, 1)
            })
    
    elif tipo_amortizacion == "Cuota Variable (Capital Fijo + Interés s/Saldo)":
        # Modalidad 2: Capital fijo + interés simple sobre saldo pendiente
        cuotas_detalle = calcular_cuota_capital_fijo(monto_prestado, tasa_interes_mensual_porcentaje, plazo_meses)
        
        tabla_amortizacion = []
        interes_total = 0
        capital_acumulado = 0
        
        for detalle in cuotas_detalle:
            interes_total += detalle['interes']
            capital_acumulado += detalle['capital']
            porcentaje_capital = (capital_acumulado / monto_prestado) * 100
            
            tabla_amortizacion.append({
                "Mes": detalle['mes'],
                "Cuota": round(detalle['cuota'], 0),
                "Interés": round(detalle['interes'], 0),
                "Capital": round(detalle['capital'], 0),
                "Saldo": round(detalle['saldo'], 0),
                "Capital Acum.": round(capital_acumulado, 0),
                "% Capital": round(porcentaje_capital, 1)
            })
        
        # Para esta modalidad, calculamos cuota promedio para métricas
        cuota_mensual = sum(detalle['cuota'] for detalle in cuotas_detalle) / len(cuotas_detalle)
    
    else:  # Capital al Final
        # Modalidad 3: Solo intereses + capital al final
        cuotas_detalle = calcular_cuota_capital_al_final(monto_prestado, tasa_interes_mensual_porcentaje, plazo_meses)
        
        tabla_amortizacion = []
        interes_total = 0
        capital_acumulado = 0
        
        for detalle in cuotas_detalle:
            interes_total += detalle['interes']
            capital_acumulado += detalle['capital']
            porcentaje_capital = (capital_acumulado / monto_prestado) * 100
            
            tabla_amortizacion.append({
                "Mes": detalle['mes'],
                "Cuota": round(detalle['cuota'], 0),
                "Interés": round(detalle['interes'], 0),
                "Capital": round(detalle['capital'], 0),
                "Saldo": round(detalle['saldo'], 0),
                "Capital Acum.": round(capital_acumulado, 0),
                "% Capital": round(porcentaje_capital, 1)
            })
        
        # Para esta modalidad, la cuota regular es solo interés
        cuota_mensual = monto_prestado * (tasa_interes_mensual_porcentaje / 100)

    df_amortizacion = pd.DataFrame(tabla_amortizacion)

    # --- Cálculos Finales (Solo Interés Simple) ---
    total_pagado = monto_prestado + interes_total
    
    # Tasas anuales SOLO para referencia (NO para capitalización)
    tasa_anual_simple = tasa_interes_mensual_porcentaje * 12
    
    # --- Métricas Principales ---
    st.subheader("📊 Indicadores del Préstamo (Interés Simple)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Monto Prestado", formato_pesos(monto_prestado))
        st.metric("📅 Plazo", f"{int(plazo_meses)} meses")
    
    with col2:
        st.metric("📈 Tasa Mensual", f"{tasa_interes_mensual_porcentaje:.3f}%")
        st.metric("📊 Tasa Anual Ref.", f"{tasa_anual_simple:.2f}%")
    
    with col3:
        if tipo_amortizacion == "Cuota Fija (Interés Simple Total)":
            st.metric("🏦 Cuota Mensual (Fija)", formato_pesos(cuota_mensual))
        elif tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
            st.metric("🏦 Cuota Regular", formato_pesos(cuota_mensual))
            st.metric("🔚 Cuota Final", formato_pesos(df_amortizacion.iloc[-1]['Cuota']))
        else:
            st.metric("🏦 Cuota Promedio", formato_pesos(cuota_mensual))
        st.metric("💸 Total a Pagar", formato_pesos(total_pagado))
    
    with col4:
        costo_total_porcentaje = (interes_total / monto_prestado) * 100
        st.metric("💰 Interés Total", formato_pesos(interes_total))
        st.metric("📊 Costo Total (%)", f"{costo_total_porcentaje:.2f}%")

    # --- Información Importante sobre Interés Simple ---
    st.info("""
    📌 **Confirmación de Interés Simple:**
    - ✅ NO se utiliza capitalización (interés compuesto)
    - ✅ Los intereses se calculan solo sobre el capital inicial o saldo pendiente
    - ✅ No hay "interés sobre intereses"
    - ✅ Las tasas anuales mostradas son solo de referencia, no para cálculos
    """)

    # Información específica sobre "Capital al Final"
    if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
        st.warning(f"""
        ⚠️ **Modalidad "Capital al Final":**
        - Durante {int(plazo_meses-1)} meses pagas solo intereses: {formato_pesos(cuota_mensual)}
        - En el mes {int(plazo_meses)} pagas interés + capital total: {formato_pesos(df_amortizacion.iloc[-1]['Cuota'])}
        - Requiere mayor disciplina financiera para tener el capital disponible al final
        """)

    # --- Tabla de Amortización ---
    st.subheader("📋 Tabla de Amortización Detallada")
    
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        mostrar_completa = st.checkbox("📊 Mostrar tabla completa", value=False)
    
    with col_viz2:
        mostrar_graficos = st.checkbox("📈 Mostrar gráficos", value=True)
    
    if mostrar_completa:
        st.dataframe(
            df_amortizacion.style.format({
                "Cuota": formato_pesos,
                "Interés": formato_pesos,
                "Capital": formato_pesos,
                "Saldo": formato_pesos,
                "Capital Acum.": formato_pesos
            }),
            use_container_width=True
        )
    else:
        # Mostrar meses clave
        meses_clave = [1, 6, 12, 18, 24] if plazo_meses >= 24 else [1, int(plazo_meses/4), int(plazo_meses/2), int(3*plazo_meses/4), int(plazo_meses)]
        meses_clave = [m for m in meses_clave if m <= plazo_meses]
        
        df_resumida = df_amortizacion[df_amortizacion['Mes'].isin(meses_clave)]
        st.dataframe(
            df_resumida.style.format({
                "Cuota": formato_pesos,
                "Interés": formato_pesos,
                "Capital": formato_pesos,
                "Saldo": formato_pesos,
                "Capital Acum.": formato_pesos
            }),
            use_container_width=True
        )
        st.info("💡 Mostrando meses clave. Activa 'Mostrar tabla completa' para ver todos los meses.")

    # --- Gráficos ---
    if mostrar_graficos:
        st.subheader("📊 Visualizaciones del Préstamo")
        
        # Gráfico 1: Evolución del saldo y pagos acumulados
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=df_amortizacion['Mes'],
            y=df_amortizacion['Saldo'],
            mode='lines+markers',
            name='Saldo Restante',
            line=dict(color='red', width=3)
        ))
        
        fig1.add_trace(go.Scatter(
            x=df_amortizacion['Mes'],
            y=df_amortizacion['Capital Acum.'],
            mode='lines+markers',
            name='Capital Pagado (Acum.)',
            line=dict(color='green', width=3)
        ))
        
        fig1.update_layout(
            title="📈 Evolución del Saldo y Capital Pagado",
            xaxis_title="Mes",
            yaxis_title="Monto (COP)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico 2: Composición de la cuota
        if tipo_amortizacion != "Cuota Fija (Interés Simple Total)":
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=df_amortizacion['Mes'],
                y=df_amortizacion['Cuota'],
                mode='lines+markers',
                name='Cuota Total',
                line=dict(color='blue', width=3)
            ))
            
            fig2.add_trace(go.Scatter(
                x=df_amortizacion['Mes'],
                y=df_amortizacion['Interés'],
                mode='lines+markers',
                name='Componente Interés',
                line=dict(color='orange', width=2)
            ))
            
            fig2.add_trace(go.Scatter(
                x=df_amortizacion['Mes'],
                y=df_amortizacion['Capital'],
                mode='lines+markers',
                name='Componente Capital',
                line=dict(color='green', width=2)
            ))
            
            if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
                titulo_grafico = "💰 Composición de las Cuotas - Capital al Final"
            else:
                titulo_grafico = "💰 Composición de las Cuotas Variables"
            
            fig2.update_layout(
                title=titulo_grafico,
                xaxis_title="Mes",
                yaxis_title="Monto (COP)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig2, use_container_width=True)

    # --- Simulación de Escenarios ---
    st.subheader("🎯 Simulador de Escenarios (Interés Simple)")
    
    col_sim1, col_sim2 = st.columns(2)
    
    with col_sim1:
        st.markdown("**📊 Variación de Tasa de Interés**")
        tasa_min = st.number_input("Tasa mínima (%)", value=max(0.1, tasa_interes_mensual_porcentaje - 1), step=0.1, format="%.2f")
        tasa_max = st.number_input("Tasa máxima (%)", value=tasa_interes_mensual_porcentaje + 1, step=0.1, format="%.2f")
    
    with col_sim2:
        st.markdown("**📅 Variación de Plazo**")
        plazo_min = st.number_input("Plazo mínimo (meses)", value=max(6, int(plazo_meses - 6)), step=6, format="%d")
        plazo_max = st.number_input("Plazo máximo (meses)", value=int(plazo_meses + 12), step=6, format="%d")

    if st.button("🔄 Ejecutar Simulación", key="simular_escenarios"):
        # Simulación de tasas
        tasas_sim = [tasa_min + i * 0.25 for i in range(int((tasa_max - tasa_min) / 0.25) + 1)]
        plazos_sim = list(range(plazo_min, plazo_max + 6, 6))
        
        # Crear tabla de simulación
        simulaciones = []
        
        for tasa in tasas_sim:
            for plazo in plazos_sim:
                if tipo_amortizacion == "Cuota Fija (Interés Simple Total)":
                    interes_sim = monto_prestado * (tasa / 100) * plazo
                    cuota_sim = (monto_prestado + interes_sim) / plazo
                elif tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
                    # Solo intereses mensuales, capital al final
                    interes_sim = monto_prestado * (tasa / 100) * plazo
                    cuota_sim = monto_prestado * (tasa / 100)  # Cuota regular (solo interés)
                else:
                    # Capital fijo + interés sobre saldo
                    cuotas_sim = calcular_cuota_capital_fijo(monto_prestado, tasa, plazo)
                    if cuotas_sim:
                        cuota_sim = sum(c['cuota'] for c in cuotas_sim) / len(cuotas_sim)
                        interes_sim = sum(c['interes'] for c in cuotas_sim)
                    else:
                        cuota_sim = 0
                        interes_sim = 0
                
                total_sim = monto_prestado + interes_sim
                
                simulaciones.append({
                    "Tasa (%)": tasa,
                    "Plazo": plazo,
                    "Cuota": cuota_sim,
                    "Total": total_sim,
                    "Intereses": interes_sim
                })
        
        df_sim = pd.DataFrame(simulaciones)
        
        # Mapa de calor para visualizar cuotas
        pivot_cuotas = df_sim.pivot(index="Tasa (%)", columns="Plazo", values="Cuota")
        
        fig_heatmap = px.imshow(
            pivot_cuotas,
            title="🔥 Mapa de Calor: Cuotas por Tasa y Plazo (Interés Simple)",
            color_continuous_scale="RdYlBu_r"
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Tabla de simulación
        st.markdown("📋 **Resultados de Simulación**")
        df_sim_display = df_sim.copy()
        df_sim_display['Cuota'] = df_sim_display['Cuota'].apply(formato_pesos)
        df_sim_display['Total'] = df_sim_display['Total'].apply(formato_pesos)
        df_sim_display['Intereses'] = df_sim_display['Intereses'].apply(formato_pesos)
        
        st.dataframe(df_sim_display, use_container_width=True)

    # --- Comparación con el Portafolio ---
    st.subheader("🆚 Análisis Comparativo con tu Portafolio")
    
    rentabilidad_portafolio = 0.0
    capital_disponible = 0.0

    # Calcular rentabilidad del portafolio
    if 'df' in st.session_state and st.session_state.df is not None:
        df_portafolio_cleaned = clean_df_for_analysis(st.session_state.df)
        capital_total_portafolio = df_portafolio_cleaned['Dinero'].sum()
        ingreso_pasivo_mensual_portafolio = df_portafolio_cleaned['Interes Mensual'].sum()

        if capital_total_portafolio > 0:
            rentabilidad_portafolio = (ingreso_pasivo_mensual_portafolio / capital_total_portafolio) * 12 * 100
            capital_disponible = capital_total_portafolio
            
            if rentabilidad_portafolio > 500:
                st.warning(f"⚠️ La rentabilidad anual de tu portafolio ({rentabilidad_portafolio:.2f}%) parece muy alta. Esto podría deberse a datos inconsistentes.")
                rentabilidad_portafolio = min(rentabilidad_portafolio, 500.0)
        else:
            st.info("El capital total de tu portafolio es cero, no se puede calcular la rentabilidad.")
    else:
        st.info("💡 Para comparar, carga tu portafolio en la sección '📥 Cargar Portafolio'.")

    # Rentabilidad del préstamo (interés simple anualizado)
    if plazo_meses > 0:
        rentabilidad_prestamo_anual = (interes_total / monto_prestado) * (12 / plazo_meses) * 100
    else:
        rentabilidad_prestamo_anual = 0

    # Métricas de comparación
    col_comp1, col_comp2, col_comp3 = st.columns(3)
    
    with col_comp1:
        st.metric(
            "🏦 Rentabilidad del Préstamo",
            f"{rentabilidad_prestamo_anual:.2f}%",
            help="Rentabilidad anual del préstamo basada en interés simple"
        )
    
    with col_comp2:
        st.metric(
            "💼 Rentabilidad del Portafolio",
            f"{rentabilidad_portafolio:.2f}%",
            help="Rentabilidad anual promedio de tu portafolio actual"
        )
    
    with col_comp3:
        if rentabilidad_portafolio > 0:
            diferencia = rentabilidad_prestamo_anual - rentabilidad_portafolio
            st.metric(
                "📊 Diferencia",
                f"{diferencia:+.2f}%",
                delta=f"{diferencia:.2f}%",
                help="Diferencia entre rentabilidad del préstamo y del portafolio"
            )

    # --- Análisis de Oportunidad de Inversión ---
    if rentabilidad_portafolio > 0:
        st.subheader("💡 Análisis de Oportunidad de Inversión")
        
        # Cálculo del costo de oportunidad
        if monto_prestado <= capital_disponible:
            ingreso_portafolio_anual = monto_prestado * (rentabilidad_portafolio / 100)
            ingreso_prestamo_anual = interes_total * (12 / plazo_meses)  # Anualizar los intereses
            diferencia_ingresos = ingreso_prestamo_anual - ingreso_portafolio_anual
            
            col_opp1, col_opp2, col_opp3 = st.columns(3)
            
            with col_opp1:
                st.metric("💰 Ingreso Anual (Portafolio)", formato_pesos(ingreso_portafolio_anual))
            
            with col_opp2:
                st.metric("🏦 Ingreso Anual (Préstamo)", formato_pesos(ingreso_prestamo_anual))
            
            with col_opp3:
                st.metric(
                    "⚖️ Diferencia de Ingresos",
                    formato_pesos(abs(diferencia_ingresos)),
                    delta=f"{diferencia_ingresos:+,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    delta_color="normal" if diferencia_ingresos > 0 else "inverse"
                )

        # Recomendación detallada considerando modalidad de pago
        recomendacion_modalidad = ""
        if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
            recomendacion_modalidad = f"""
            
            **⚠️ Consideraciones especiales para "Capital al Final":**
            - El prestatario debe demostrar capacidad de ahorro/inversión para reunir {formato_pesos(monto_prestado)} al final
            - Mayor riesgo de incumplimiento en el mes final
            - Evalúa si el prestatario tendrá los recursos disponibles en el mes {int(plazo_meses)}
            - Considera solicitar garantías adicionales por la alta exposición al final
            """

        if rentabilidad_prestamo_anual > rentabilidad_portafolio:
            diferencia_rent = rentabilidad_prestamo_anual - rentabilidad_portafolio
            st.success(f"""
            🎉 **¡Oportunidad Favorable!**
            
            La rentabilidad del préstamo ({rentabilidad_prestamo_anual:.2f}%) supera a tu portafolio ({rentabilidad_portafolio:.2f}%) 
            por **{diferencia_rent:.2f} puntos porcentuales**.
            
            **Consideraciones positivas:**
            - Mayor retorno sobre la inversión
            - Diversificación de ingresos
            - Flujo de caja predecible
            
            **⚠️ Evalúa también:**
            - Perfil crediticio del solicitante
            - Garantías o respaldos disponibles
            - Tu necesidad de liquidez
            {recomendacion_modalidad}
            """)
        elif abs(rentabilidad_prestamo_anual - rentabilidad_portafolio) <= 2:
            st.info(f"""
            🤝 **Oportunidad Neutra**
            
            La rentabilidad del préstamo ({rentabilidad_prestamo_anual:.2f}%) es similar a tu portafolio ({rentabilidad_portafolio:.2f}%).
            
            **Considera factores cualitativos:**
            - Relación con el solicitante
            - Diversificación de riesgo
            - Facilidad de gestión
            - Impacto en tu liquidez
            {recomendacion_modalidad}
            """)
        else:
            diferencia_rent = rentabilidad_portafolio - rentabilidad_prestamo_anual
            st.warning(f"""
            📉 **Costo de Oportunidad Alto**
            
            Tu portafolio ({rentabilidad_portafolio:.2f}%) supera al préstamo ({rentabilidad_prestamo_anual:.2f}%) 
            por **{diferencia_rent:.2f} puntos porcentuales**.
            
            **Recomendación:** Considera mantener el dinero en tu portafolio actual, 
            a menos que existan razones personales muy importantes.
            
            **Alternativas:**
            - Ofrecer una tasa más alta
            - Reducir el plazo del préstamo
            - Buscar otras oportunidades de inversión
            {recomendacion_modalidad}
            """)

    # --- Calculadora de Punto de Equilibrio ---
    st.subheader("⚖️ Calculadora de Punto de Equilibrio")
    
    if rentabilidad_portafolio > 0:
        # Calcular la tasa mínima requerida para igualar el portafolio
        tasa_equilibrio_anual = rentabilidad_portafolio
        tasa_equilibrio_mensual = tasa_equilibrio_anual / 12
        
        if tipo_amortizacion == "Cuota Fija (Interés Simple Total)":
            interes_equilibrio = monto_prestado * (tasa_equilibrio_mensual / 100) * plazo_meses
            cuota_equilibrio = (monto_prestado + interes_equilibrio) / plazo_meses
        elif tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
            cuota_equilibrio = monto_prestado * (tasa_equilibrio_mensual / 100)
        else:
            cuotas_equilibrio = calcular_cuota_capital_fijo(monto_prestado, tasa_equilibrio_mensual, plazo_meses)
            if cuotas_equilibrio:
                cuota_equilibrio = sum(c['cuota'] for c in cuotas_equilibrio) / len(cuotas_equilibrio)
            else:
                cuota_equilibrio = 0
        
        col_eq1, col_eq2, col_eq3 = st.columns(3)
        
        with col_eq1:
            st.metric("🎯 Tasa Mensual Mínima", f"{tasa_equilibrio_mensual:.3f}%")
        
        with col_eq2:
            st.metric("📅 Tasa Anual Mínima", f"{tasa_equilibrio_anual:.2f}%")
        
        with col_eq3:
            if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
                st.metric("💰 Cuota Regular de Equilibrio", formato_pesos(cuota_equilibrio))
            else:
                st.metric("💰 Cuota de Equilibrio", formato_pesos(cuota_equilibrio))
        
        equilibrio_text = f"""
        💡 **Interpretación:** Para que este préstamo sea igual de atractivo que tu portafolio actual,
        necesitarías cobrar al menos **{tasa_equilibrio_mensual:.3f}% mensual** 
        (equivalente a **{tasa_equilibrio_anual:.2f}% anual**).
        """
        
        if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
            equilibrio_text += f"""
            
            **Para modalidad "Capital al Final":** La cuota regular sería de {formato_pesos(cuota_equilibrio)} mensuales.
            """
        
        st.info(equilibrio_text)

    # --- Análisis de Riesgo ---
    st.subheader("⚠️ Análisis de Riesgo del Préstamo")
    
    # Calculadora de impacto por incumplimiento
    col_riesgo1, col_riesgo2 = st.columns(2)
    
    with col_riesgo1:
        probabilidad_incumplimiento = st.slider(
            "Probabilidad estimada de incumplimiento (%)",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
            step=0.5,
            help="Estima la probabilidad de que el prestatario no pueda pagar"
        )
    
    with col_riesgo2:
        porcentaje_recuperacion = st.slider(
            "Porcentaje de recuperación en caso de incumplimiento (%)",
            min_value=0.0,
            max_value=100.0,
            value=50.0,
            step=5.0,
            help="Qué porcentaje del capital podrías recuperar en caso de incumplimiento"
        )

    # Ajuste de riesgo específico para "Capital al Final"
    factor_riesgo_adicional = 1.0
    if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
        factor_riesgo_adicional = 1.5  # 50% más riesgo por la concentración al final
        st.warning("""
        ⚠️ **Riesgo Adicional - Capital al Final:** 
        Esta modalidad tiene mayor riesgo porque el capital se concentra en una sola cuota final.
        Se ha aplicado un factor de riesgo adicional del 50% en los cálculos.
        """)

    # Cálculo del valor esperado ajustado por riesgo
    prob_exito = (100 - probabilidad_incumplimiento * factor_riesgo_adicional) / 100
    prob_incumplimiento_calc = (probabilidad_incumplimiento * factor_riesgo_adicional) / 100
    
    valor_esperado_exito = prob_exito * interes_total
    valor_esperado_perdida = prob_incumplimiento_calc * (monto_prestado * (1 - porcentaje_recuperacion/100))
    valor_esperado_neto = valor_esperado_exito - valor_esperado_perdida
    
    rentabilidad_ajustada_riesgo = (valor_esperado_neto / monto_prestado) * (12 / plazo_meses) * 100

    st.markdown("### 📊 Análisis de Valor Esperado")
    
    col_val1, col_val2, col_val3 = st.columns(3)
    
    with col_val1:
        st.metric("✅ Valor Esperado (Éxito)", formato_pesos(valor_esperado_exito))
    
    with col_val2:
        st.metric("❌ Pérdida Esperada", formato_pesos(valor_esperado_perdida))
    
    with col_val3:
        st.metric("⚖️ Valor Neto Esperado", formato_pesos(valor_esperado_neto))

    st.metric(
        "📈 Rentabilidad Anual Ajustada por Riesgo",
        f"{rentabilidad_ajustada_riesgo:.2f}%",
        help="Rentabilidad esperada considerando probabilidad de incumplimiento"
    )

    # Comparación final con riesgo ajustado
    if rentabilidad_portafolio > 0:
        if rentabilidad_ajustada_riesgo > rentabilidad_portafolio:
            st.success(f"✅ Incluso ajustado por riesgo, el préstamo ({rentabilidad_ajustada_riesgo:.2f}%) supera a tu portafolio ({rentabilidad_portafolio:.2f}%).")
        else:
            st.error(f"❌ Ajustado por riesgo, el préstamo ({rentabilidad_ajustada_riesgo:.2f}%) no supera a tu portafolio ({rentabilidad_portafolio:.2f}%).")

    # --- Recordatorio Final ---
    st.markdown("---")
    mensaje_final = """
    ✅ **Confirmación:** Todos los cálculos utilizan ÚNICAMENTE interés simple.
    
    📋 **Características del análisis:**
    - Interés calculado sobre capital inicial o saldo pendiente
    - Sin capitalización de intereses
    - Cálculos transparentes y lineales
    - Comparaciones justas con tu portafolio
    """
    
    if tipo_amortizacion == "Capital al Final (Solo Intereses + Capital Final)":
        mensaje_final += """
        
    🎯 **Modalidad "Capital al Final":**
    - Solo se pagan intereses durante el plazo
    - El capital completo se cancela en la última cuota
    - Requiere mayor disciplina financiera del prestatario
    - Mayor concentración de riesgo al final del préstamo
        """
    
    st.success(mensaje_final)

# --- Función Principal del Módulo de Evaluación de Préstamos ---
def evaluar_prestamo():
    """
    Función principal que muestra las opciones de evaluación de préstamos.
    Esta es la función que debe importarse en app.py
    """
    st.title("🏦 Herramientas de Evaluación de Préstamos")
    st.markdown("Selecciona la herramienta que deseas utilizar:")

    opcion_evaluacion = st.radio(
        "Elige una opción:",
        ["Evaluación General de Préstamo", "Análisis Detallado de Préstamo"],
        key="opcion_evaluacion_radio"
    )

    if opcion_evaluacion == "Evaluación General de Préstamo":
        mostrar_evaluacion_general()
    elif opcion_evaluacion == "Análisis Detallado de Préstamo":
        mostrar_analisis_detalle()

# Asegurar que la función esté disponible para importación
__all__ = ['evaluar_prestamo']