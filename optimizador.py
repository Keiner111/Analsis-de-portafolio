import streamlit as st
import pandas as pd
import json
import os

# Define el nombre del archivo para guardar los parámetros del optimizador
OPTIMIZADOR_PARAMS_FILE = "optimizador_params.json"

# Funcion para formatear valores monetarios en pesos colombianos
def formato_pesos(valor):
    # Formatea el numero con separador de miles como '.' y decimal como ','
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def load_optimizador_params():
    """
    Carga los parámetros del optimizador desde un archivo JSON.
    Retorna un diccionario con los parámetros o valores por defecto si el archivo no existe o está vacío.
    """
    if os.path.exists(OPTIMIZADOR_PARAMS_FILE):
        with open(OPTIMIZADOR_PARAMS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Si el archivo está vacío o mal formado, retornar valores por defecto
                return {
                    "tasa_minima": 0.5,
                    "porcentaje_objetivo": 70,
                    "tasa_simulada": 0.5
                }
    # Si el archivo no existe, retornar valores por defecto
    return {
        "tasa_minima": 0.5,
        "porcentaje_objetivo": 70,
        "tasa_simulada": 0.5
    }

def save_optimizador_params(params_dict):
    """
    Guarda los parámetros del optimizador en un archivo JSON.
    """
    with open(OPTIMIZADOR_PARAMS_FILE, 'w') as f:
        json.dump(params_dict, f, indent=4)

def sugerir_rebalanceo(df):
    st.header("🧠 Asistente de Rebalanceo Inteligente")

    if df is None or df.empty:
        st.warning("Para utilizar el asistente de rebalanceo, por favor, carga tu portafolio primero.")
        return

    # Limpieza de datos: Asegurarse de que 'Dinero' sea numérico y 'Interes Mensual' también
    df_cleaned = df.copy()
    df_cleaned['Dinero'] = pd.to_numeric(df_cleaned['Dinero'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df_cleaned['Interes Mensual'] = pd.to_numeric(df_cleaned['Interes Mensual'].replace('[\%,]', '', regex=True), errors='coerce').fillna(0)
    # Calcular la tasa de interés mensual en porcentaje para cada inversión
    df_cleaned['Tasa Mensual (%)'] = (df_cleaned['Interes Mensual'] / df_cleaned['Dinero']) * 100
    # Manejar casos donde 'Dinero' es cero para evitar NaN o Inf
    df_cleaned['Tasa Mensual (%)'] = df_cleaned['Tasa Mensual (%)'].replace([float('inf'), -float('inf')], 0).fillna(0)


    st.markdown("""
    Este asistente te ayuda a identificar oportunidades para **optimizar la rentabilidad de tu portafolio**
    moviendo capital de inversiones de bajo rendimiento a aquellas con mayor potencial.
    """)

    # Cargar los parámetros guardados o usar los valores por defecto
    saved_params = load_optimizador_params()

    tasa_minima = st.number_input(
        "Define la tasa de interés mensual mínima deseada (%) para tus inversiones:",
        min_value=0.0,
        value=float(saved_params.get("tasa_minima", 0.5)),
        step=0.1,
        format="%.2f",
        key="tasa_minima_input_optimizador"
    )

    # Filtrar inversiones basadas en la tasa mínima deseada
    improductivas = df_cleaned[df_cleaned['Tasa Mensual (%)'] < tasa_minima].copy()
    productivas = df_cleaned[df_cleaned['Tasa Mensual (%)'] >= tasa_minima].copy()

    # Calcular totales
    total_improductivo = improductivas['Dinero'].sum()
    total_productivo = productivas['Dinero'].sum()
    total_capital_portafolio = df_cleaned['Dinero'].sum()

    st.subheader("📊 Resumen de Capital")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Capital en Inversiones Improductivas (por debajo de tu tasa mínima)", formato_pesos(total_improductivo))
    with col2:
        st.metric("Capital en Inversiones Productivas (igual o por encima de tu tasa mínima)", formato_pesos(total_productivo))

    st.markdown("---")

    st.subheader("🎯 Establece tu Objetivo de Capital Productivo")
    porcentaje_objetivo = st.slider(
        "Porcentaje del capital total que deseas tener en inversiones productivas:",
        0, 100, int(saved_params.get("porcentaje_objetivo", 70)),
        key="porcentaje_objetivo_slider_optimizador"
    )
    
    capital_objetivo_productivo = (porcentaje_objetivo / 100) * total_capital_portafolio
    falta_por_mover = capital_objetivo_productivo - total_productivo

    if falta_por_mover > 0:
        st.warning(f"⚠️ Te falta mover **{formato_pesos(falta_por_mover)}** a inversiones con mejor rendimiento para alcanzar tu objetivo del {porcentaje_objetivo}% de capital productivo.")
    else:
        st.success(f"🎉 ¡Felicidades! Ya estás cumpliendo o superando tu objetivo del {porcentaje_objetivo}% de capital productivo.")

    st.markdown("---")

    if not improductivas.empty:
        st.subheader("🔍 Inversiones a Considerar para Rebalanceo (Bajo Rendimiento)")
        st.markdown(f"""
        Las siguientes inversiones están actualmente generando una tasa de interés mensual **inferior al {tasa_minima:.2f}%**.
        Considera reevaluarlas para mover su capital a oportunidades más rentables o mejorar su desempeño.
        """)
        # Formatear las columnas para la visualización
        improductivas_display = improductivas[['Items', 'Dinero', 'Interes Mensual', 'Tasa Mensual (%)']].copy()
        improductivas_display['Dinero'] = improductivas_display['Dinero'].apply(formato_pesos)
        improductivas_display['Interes Mensual'] = improductivas_display['Interes Mensual'].apply(formato_pesos)
        improductivas_display['Tasa Mensual (%)'] = improductivas_display['Tasa Mensual (%)'].apply(lambda x: f"{x:.2f}%")
        st.dataframe(improductivas_display, use_container_width=True)
    else:
        st.success("✅ No tienes inversiones por debajo de la tasa mínima establecida. ¡Excelente gestión!")

    st.markdown("---")

    # --- Nueva sección: Tabla Completa de Inversiones con Recomendación ---
    st.subheader("📋 Tabla Completa de Inversiones con Recomendación")
    st.markdown("Aquí puedes ver todas tus inversiones con una sugerencia de acción basada en la tasa mínima establecida.")

    # Añadir la columna de recomendación al DataFrame limpio
    df_cleaned['Recomendacion'] = df_cleaned['Tasa Mensual (%)'].apply(
        lambda x: "Mantener" if x >= tasa_minima else "Mover capital a inversión productiva"
    )

    # Preparar el DataFrame para la visualización
    df_full_display = df_cleaned[['Items', 'Tipo de inversion', 'Dinero', 'Interes Mensual', 'Tasa Mensual (%)', 'Recomendacion']].copy()
    df_full_display['Dinero'] = df_full_display['Dinero'].apply(formato_pesos)
    df_full_display['Interes Mensual'] = df_full_display['Interes Mensual'].apply(formato_pesos)
    df_full_display['Tasa Mensual (%)'] = df_full_display['Tasa Mensual (%)'].apply(lambda x: f"{x:.2f}%")

    st.dataframe(df_full_display, use_container_width=True)
    # --- Fin de la nueva sección ---

    st.markdown("---")
    st.subheader("💡 Estrategias de Rebalanceo Sugeridas")
    st.markdown("""
    Para optimizar tu portafolio, considera las siguientes acciones:
    - **Reinvertir:** Mueve el capital de las inversiones de bajo rendimiento a aquellas que consistentemente te ofrecen una tasa superior.
    - **Diversificar:** Explora nuevas oportunidades de inversión que se alineen con tu perfil de riesgo y tus objetivos de rentabilidad.
    - **Revisar condiciones:** Contacta a tu asesor o la entidad financiera para ver si puedes mejorar las condiciones de las inversiones de bajo rendimiento.
    - **Liquidación:** Si una inversión es persistentemente improductiva y no hay perspectivas de mejora, considera liquidarla y reasignar el capital.
    """)

    # Guardar los valores actuales en el archivo JSON
    save_optimizador_params({
        "tasa_minima": tasa_minima,
        "porcentaje_objetivo": porcentaje_objetivo,
        "tasa_simulada": saved_params.get("tasa_simulada", 0.5) # Mantener la tasa simulada
    })


def simular_activacion_activos(df):
    st.header("🧪 Simulador de Activación de Activos Inactivos")

    if df is None or df.empty:
        st.warning("Para utilizar el simulador de activación de activos, por favor, carga tu portafolio primero.")
        return

    # Limpieza y preparación de datos
    df_cleaned = df.copy()
    df_cleaned['Dinero'] = pd.to_numeric(df_cleaned['Dinero'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    df_cleaned['Interes Mensual'] = pd.to_numeric(df_cleaned['Interes Mensual'], errors='coerce').fillna(0)
    
    # Calcular Interes anual en % (si 'Interes Mensual' es un monto)
    # Si 'Interes Mensual' ya es un porcentaje, esta línea podría necesitar ajuste o eliminación.
    # Asumiendo que 'Interes Mensual' es el monto de interés mensual generado.
    # Se corrige la division por cero si df_cleaned['Dinero'] es 0 para evitar errores
    df_cleaned['Interes anual (%)'] = df_cleaned.apply(
        lambda row: (row['Interes Mensual'] / row['Dinero'] * 1200) if row['Dinero'] > 0 else 0,
        axis=1
    )

    st.markdown("""
    Este simulador te permite explorar el **potencial de generación de ingresos** de aquellos activos en tu portafolio que actualmente no están produciendo rendimientos. Al asignar una **tasa de interés mensual simulada**, podrás visualizar cómo se transformaría tu capital inactivo en una fuente de ingresos pasivos.
    """)

    # Cargar los parámetros guardados o usar los valores por defecto
    saved_params = load_optimizador_params()

    # Tasa simulada ingresada por el usuario
    tasa_simulada = st.slider(
        "Define una tasa de interés mensual simulada (%) para tus activos inactivos:",
        min_value=0.0,
        max_value=20.0,
        value=float(saved_params.get("tasa_simulada", 0.5)),
        step=0.1,
        key="tasa_simulada_slider_optimizador"
    ) / 100 # Convertir a decimal

    # Filtramos activos con Interes Mensual == 0
    activos_inactivos = df_cleaned[df_cleaned['Interes Mensual'] == 0].copy()

    if activos_inactivos.empty:
        st.success("¡Felicidades! 🎉 No se han identificado activos inactivos en tu portafolio. Todos tus recursos están generando rendimientos.")
        return

    st.subheader("📋 Activos Actualmente Inactivos")
    st.dataframe(
        activos_inactivos[["Items", "Dinero", "Tipo de inversion"]].style.format({
            "Dinero": lambda x: formato_pesos(x)
        }),
        use_container_width=True
    )

    # Simulamos ingreso mensual potencial
    activos_inactivos["Ingreso Mensual Potencial"] = activos_inactivos["Dinero"] * tasa_simulada
    total_simulado = activos_inactivos["Ingreso Mensual Potencial"].sum()

    st.subheader("📈 Proyección de Ingresos al Activar Activos")
    st.dataframe(
        activos_inactivos[["Items", "Dinero", "Tipo de inversion", "Ingreso Mensual Potencial"]].style.format({
            "Dinero": lambda x: formato_pesos(x),
            "Ingreso Mensual Potencial": lambda x: formato_pesos(x)
        }),
        use_container_width=True
    )

    st.success(f"💰 Con una tasa simulada del **{tasa_simulada*100:.2f}% mensual**, tus activos inactivos podrían generar un ingreso pasivo adicional de **{formato_pesos(total_simulado)}** al mes.")

    st.subheader("💡 Consejos para la Activación de Activos")
    st.markdown("""
    La **activación estratégica** de tus recursos inactivos es una **oportunidad significativa** para **potenciar tu flujo de efectivo** y **acelerar el crecimiento** de tu patrimonio. Aquí te ofrecemos algunas consideraciones:
    """)

    if total_simulado > 0:
        st.markdown(f"""
        - **Impacto Potencial:** Observa que al activar estos activos, podrías añadir **{formato_pesos(total_simulado)}** a tus ingresos mensuales. Este monto podría ser **crucial** para cubrir gastos, aumentar tus ahorros o reinvertir.
        - **Reevaluación de Estrategias:** Te **aconsejamos encarecidamente revisar** las razones por las cuales estos activos no están generando rendimiento. ¿Podrían ser reubicados en inversiones con intereses?
        - **Explora Oportunidades:** **Considera la posibilidad de explorar** productos financieros como CDTs, fondos de inversión de bajo riesgo o incluso inversiones en Neo bancos que ofrecen rendimientos estables.
        - **Asesoramiento Profesional:** Si tienes dudas sobre cómo **movilizar estos fondos de manera eficiente**, buscar el **asesoramiento de un experto financiero** podría **desbloquear nuevas perspectivas** y **optimizar tus decisiones** de inversión.
        """)
    else:
        st.info("Actualmente, la tasa simulada es cero, por lo que el ingreso potencial también es cero. Ajusta la tasa para ver el impacto.")

    st.markdown("""
    Recuerda que cada peso que no está trabajando para ti es una oportunidad de crecimiento perdida. La **gestión proactiva** de tu capital es **esencial** para **maximizar tu potencial financiero**.
    """)

    # Guardar los valores actuales en el archivo JSON
    save_optimizador_params({
        "tasa_minima": saved_params.get("tasa_minima", 0.5), # Mantener la tasa mínima
        "porcentaje_objetivo": saved_params.get("porcentaje_objetivo", 70), # Mantener el porcentaje objetivo
        "tasa_simulada": tasa_simulada * 100 # Guardar en porcentaje
    })


# Nueva función que integra las dos funcionalidades de optimización
def mostrar_optimizacion_completa(df):
    st.title("✨ Herramientas de Optimización de Portafolio")
    st.markdown("Aquí encontrarás dos herramientas clave para mejorar el rendimiento de tus inversiones.")

    st.markdown("---") # Separador visual

    # Pestañas para organizar las dos secciones
    tab1, tab2 = st.tabs(["Asistente de Rebalanceo Inteligente", "Simulador de Activación de Activos Inactivos"])

    with tab1:
        sugerir_rebalanceo(df)

    with tab2:
        simular_activacion_activos(df)