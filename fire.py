import streamlit as st
import pandas as pd
import math
import numpy as np
from datetime import datetime, timedelta

# Función de utilidad para formato de moneda
def formato_pesos(valor):
    """Formatea el número con separador de miles como '.' y decimal como ','"""
    if valor is None or pd.isna(valor) or math.isinf(valor):
        return "$ 0"
    try:
        return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "$ 0"

def formato_porcentaje(valor):
    """Formatea porcentajes con 2 decimales"""
    if math.isinf(valor) or pd.isna(valor):
        return "0.00%"
    return f"{valor:.2f}%"

def formato_tiempo(meses):
    """Formatea el tiempo en años y meses"""
    if math.isinf(meses) or meses == float('inf'):
        return "∞ (infinito)"
    
    años = meses // 12
    meses_restantes = meses % 12
    
    if años == 0:
        return f"{int(meses)} meses"
    elif meses_restantes == 0:
        return f"{int(años)} años"
    else:
        return f"{int(años)} años y {int(meses_restantes)} meses"

def calcular_tiempo_fire_simple(capital_inicial, capital_objetivo, rentabilidad_anual):
    """
    Calcula el tiempo para FIRE usando INTERÉS SIMPLE y SIN ahorros adicionales
    
    Fórmula: Capital_Final = Capital_Inicial × (1 + rentabilidad × tiempo_años)
    Despejando tiempo: tiempo_años = (Capital_Final/Capital_Inicial - 1) / rentabilidad
    """
    if capital_inicial <= 0 or rentabilidad_anual <= 0:
        return float('inf')
    
    if capital_inicial >= capital_objetivo:
        return 0
    
    # Calcular años necesarios con interés simple
    factor_crecimiento_necesario = capital_objetivo / capital_inicial
    años_necesarios = (factor_crecimiento_necesario - 1) / (rentabilidad_anual / 100)
    
    # Convertir a meses
    meses_necesarios = años_necesarios * 12
    
    return round(meses_necesarios)

def mensaje_tiempo_fire_simple(meses_estimados):
    """Genera mensaje específico para interés simple"""
    tiempo_formateado = formato_tiempo(meses_estimados)
    
    if meses_estimados == 0:
        return "🎉 ¡FELICITACIONES! Ya alcanzaste tu FIRE - puedes vivir de tus ingresos pasivos"
    elif meses_estimados == float('inf'):
        return "⚠️ Con interés simple y sin ahorros adicionales, es imposible alcanzar FIRE"
    elif meses_estimados <= 12:
        return f"🚀 ¡Increíble! Solo {tiempo_formateado} para FIRE sin ahorrar nada más"
    elif meses_estimados <= 60:  # 5 años
        return f"💪 En {tiempo_formateado} alcanzarás FIRE solo con el crecimiento de tu capital"
    elif meses_estimados <= 240:  # 20 años
        return f"📈 Camino largo: {tiempo_formateado} para FIRE solo con interés simple"
    else:
        return f"⏳ Tiempo muy extenso: {tiempo_formateado} - considera estrategias adicionales"

def calcular_fecha_objetivo(meses_estimados):
    """Calcula la fecha estimada para alcanzar FIRE"""
    if meses_estimados == float('inf') or meses_estimados == 0:
        return None
    
    fecha_objetivo = datetime.now() + timedelta(days=meses_estimados * 30.44)
    return fecha_objetivo.strftime("%B de %Y")

def mostrar_proyeccion_capital_simple(capital_inicial, rentabilidad_anual, años_proyeccion=10):
    """Muestra la proyección del capital con interés simple"""
    proyeccion = []
    
    for año in range(1, min(años_proyeccion + 1, 21)):  # Máximo 20 años
        capital_año = capital_inicial * (1 + (rentabilidad_anual/100) * año)
        proyeccion.append({
            'Año': año,
            'Capital': capital_año,
            'Capital_Formateado': formato_pesos(capital_año)
        })
    
    return proyeccion

def mostrar_resumen_fire_simple(meses_estimados, capital_actual, capital_objetivo, gastos_mensuales, rentabilidad):
    """Genera un resumen para interés simple sin ahorros"""
    tiempo_formateado = formato_tiempo(meses_estimados)
    falta = capital_objetivo - capital_actual
    progreso_pct = (capital_actual / capital_objetivo) * 100 if capital_objetivo > 0 else 0
    
    resultado = f"""🎯 FIRE CON INTERÉS SIMPLE (SIN AHORROS ADICIONALES):

⏳ Tiempo estimado: {tiempo_formateado}
📊 Progreso actual: {progreso_pct:.1f}% completado
💰 Capital faltante: {formato_pesos(falta)}
🔢 Modalidad: Solo crecimiento del capital actual"""
    
    # Agregar fecha objetivo si es calculable
    fecha_objetivo = calcular_fecha_objetivo(meses_estimados)
    if fecha_objetivo:
        resultado += f"\n📅 Fecha objetivo: {fecha_objetivo}"
    
    # Calcular el capital final con interés simple
    if meses_estimados != float('inf'):
        años_para_fire = meses_estimados / 12
        capital_final_calculado = capital_actual * (1 + (rentabilidad/100) * años_para_fire)
        resultado += f"\n✅ Capital al alcanzar FIRE: {formato_pesos(capital_final_calculado)}"
    
    return resultado

def calculadora_fire(capital, ingreso_pasivo, rentabilidad):
    st.header("🔥 Calculadora FIRE - Interés Simple (Sin Ahorros)")

    st.markdown("""
    Esta calculadora asume:
    - **Interés SIMPLE** (no compuesto)
    - **Sin ahorros adicionales** (solo crece tu capital actual)
    - Meta: que tus ingresos pasivos cubran tus gastos completamente
    
    ### ⚠️ Importante:
    - Con interés simple, el crecimiento es **lineal** (no exponencial)
    - Sin ahorros adicionales, dependes 100% del crecimiento de tu capital actual
    - Los tiempos pueden ser considerablemente más largos
    """)

    # Inicializar variables de sesión si no existen
    if "gastos_mensuales_fire" not in st.session_state:
        st.session_state.gastos_mensuales_fire = 0.0

    if "editar_rendimiento_fire" not in st.session_state:
        st.session_state.editar_rendimiento_fire = False

    # Input para gastos mensuales
    gastos_mensuales = st.number_input(
        "💸 Tus gastos mensuales estimados (COP)",
        min_value=0.0,
        step=50000.0,
        format="%.2f",
        value=float(st.session_state.gastos_mensuales_fire),
        key="gastos_mensuales_input_fire"
    )
    st.session_state.gastos_mensuales_fire = gastos_mensuales

    gastos_anuales = gastos_mensuales * 12

    st.divider()

    # Checkbox para editar rentabilidad
    editar_rendimiento = st.checkbox(
        "¿Deseas editar el rendimiento anual promedio?",
        value=st.session_state.editar_rendimiento_fire,
        key="editar_rendimiento_checkbox_fire"
    )
    st.session_state.editar_rendimiento_fire = editar_rendimiento

    if editar_rendimiento:
        rentabilidad = st.number_input(
            "🔧 Rentabilidad anual estimada (%)",
            min_value=0.0,
            max_value=100.0,
            value=rentabilidad,
            step=0.1,
            format="%.2f",
            key="rentabilidad_anual_input_fire"
        )
    else:
        st.info(f"💡 Rentabilidad anual usada por defecto: {rentabilidad:.2f}%")

    # Cálculos principales con interés simple
    capital_objetivo = gastos_anuales / (rentabilidad / 100) if rentabilidad > 0 else float('inf')
    delta_capital = capital - capital_objetivo
    ingreso_pasivo_estimado = capital * (rentabilidad / 100)

    # Calcular tiempo con interés simple SIN ahorros adicionales
    meses_estimados = calcular_tiempo_fire_simple(capital, capital_objetivo, rentabilidad)

    # Mostrar métricas principales
    col1, col2 = st.columns(2)
    col1.metric("Capital Actual Productivo", formato_pesos(capital))
    col2.metric("Ingreso Pasivo Actual", formato_pesos(ingreso_pasivo))

    st.metric("🔥 Capital Necesario para FIRE",
              formato_pesos(capital_objetivo),
              delta=formato_pesos(delta_capital))

    st.metric("💰 Ingreso Pasivo Estimado con tu Capital",
              formato_pesos(ingreso_pasivo_estimado))

    # Barra de progreso
    progreso_fi = (capital / capital_objetivo) * 100 if capital_objetivo > 0 and capital_objetivo != float('inf') else 0
    progreso_fi = min(progreso_fi, 100)

    st.subheader("🔋 Progreso hacia tu Libertad Financiera")
    st.progress(progreso_fi / 100, text=f"Avance: {progreso_fi:.2f}% del capital necesario")

    # Mostrar mensaje sobre el tiempo
    mensaje_tiempo = mensaje_tiempo_fire_simple(meses_estimados)
    
    if meses_estimados == 0:
        st.success(mensaje_tiempo)
    elif meses_estimados <= 60:
        st.info(mensaje_tiempo)
    elif meses_estimados == float('inf'):
        st.error(mensaje_tiempo)
    else:
        st.warning(mensaje_tiempo)

    # Información adicional
    fecha_objetivo = calcular_fecha_objetivo(meses_estimados)
    if fecha_objetivo and meses_estimados != float('inf'):
        st.info(f"📅 **Fecha estimada para FIRE:** {fecha_objetivo}")

    # Mostrar resumen
    st.markdown("### 🏁 RESUMEN DE TU CAMINO FIRE")
    resumen_completo = mostrar_resumen_fire_simple(
        meses_estimados, capital, capital_objetivo, gastos_mensuales, rentabilidad
    )
    st.code(resumen_completo)

    # Proyección de crecimiento
    if meses_estimados != float('inf') and meses_estimados > 0:
        st.markdown("### 📈 Proyección de tu Capital (Interés Simple)")
        años_proyeccion = min(int(meses_estimados / 12) + 2, 10)
        proyeccion = mostrar_proyeccion_capital_simple(capital, rentabilidad, años_proyeccion)
        
        # Mostrar tabla de proyección
        df_proyeccion = pd.DataFrame(proyeccion)
        st.dataframe(df_proyeccion[['Año', 'Capital_Formateado']].rename(columns={
            'Año': 'Año',
            'Capital_Formateado': 'Capital Proyectado'
        }), use_container_width=True)

    # Consejos específicos para interés simple
    st.markdown("### 💡 Recomendaciones para Interés Simple")
    
    if meses_estimados == 0:
        st.success("🎉 **¡Ya tienes FIRE!** Disfruta tu independencia financiera.")
    elif meses_estimados <= 60:
        st.info("""
        ✅ **Situación favorable:**
        - Tu capital actual es suficiente para FIRE a corto plazo
        - Mantén la rentabilidad actual
        - Considera proteger tu capital de la inflación
        """)
    elif meses_estimados <= 240:
        st.warning("""
        ⚠️ **Tiempo considerable requerido:**
        - Con solo interés simple, el proceso es lento
        - **Considera agregar ahorros mensuales** para acelerar significativamente
        - **Busca inversiones de mayor rentabilidad** (con el riesgo apropiado)
        - **Evalúa reducir gastos** para bajar la meta FIRE
        """)
    else:
        st.error("""
        🚨 **Estrategia actual no es viable:**
        - El tiempo requerido es excesivamente largo
        - **NECESITAS cambiar la estrategia:**
          - Agregar ahorros mensuales significativos
          - Buscar inversiones con mayor rentabilidad
          - Reducir considerablemente tus gastos mensuales
          - Considerar interés compuesto en lugar de simple
        """)

    # Comparación con interés compuesto
    if st.checkbox("🔍 ¿Quieres ver la diferencia con interés compuesto?"):
        if capital > 0 and capital_objetivo != float('inf') and rentabilidad > 0:
            # Cálculo con interés compuesto
            rentabilidad_mensual_comp = rentabilidad / 100 / 12
            if capital < capital_objetivo:
                meses_compuesto = math.log(capital_objetivo / capital) / math.log(1 + rentabilidad_mensual_comp)
                meses_compuesto = round(meses_compuesto)
            else:
                meses_compuesto = 0
            
            # Comparación
            diferencia_meses = meses_estimados - meses_compuesto
            diferencia_años = diferencia_meses / 12
            
            st.info(f"""
            📊 **Comparación Interés Simple vs Compuesto:**
            
            - **Interés Simple:** {formato_tiempo(meses_estimados)}
            - **Interés Compuesto:** {formato_tiempo(meses_compuesto)}
            - **Diferencia:** {formato_tiempo(diferencia_meses)} ({diferencia_años:.1f} años menos con compuesto)
            
            💡 **Conclusión:** El interés compuesto acelera significativamente tu camino hacia FIRE.
            """)

# Ejemplo de uso
"""
if __name__ == "__main__":
    capital_ejemplo = 50000000  # 50 millones COP
    ingreso_pasivo_ejemplo = 250000  # 250 mil COP mensuales
    rentabilidad_ejemplo = 6.0  # 6% anual
    
    calculadora_fire(capital_ejemplo, ingreso_pasivo_ejemplo, rentabilidad_ejemplo)
"""