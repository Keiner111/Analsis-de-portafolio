# Este es el archivo app.py: punto de entrada principal de la aplicacion
import streamlit as st
import pandas as pd

# Importaciones de modulos locales
from cargador_archivos import cargar_datos
from portafolio import analizar_portafolio, mostrar_kpis
from simulador import simular_proyecciones
from evaluacion import evaluar_prestamo
from chat_financiero import chat_ia
from generador_informe import generar_docx
from inversiones_fisicas import gestionar_inversiones_fisicas
from manual_ia import mostrar_manual_ia
from fire import calculadora_fire
from devaluacion import calcular_devaluacion

from optimizador import mostrar_optimizacion_completa # Importar la funcion completa
from historico import mostrar_historico, guardar_snapshot
from balance_general import mostrar_balance_general
# from rebalanceo import rebalanceo_inteligente # Esta línea ya no es necesaria y fue eliminada
from divisas import mostrar_divisas, obtener_tasa_cambio
from ruta_meta import ruta_hacia_meta, load_meta_params
from gestion_gastos import mostrar_gestion_gastos
from evaluacion_riesgo import mostrar_evaluacion_riesgo
from seguimiento_metas import mostrar_seguimiento_metas
from dashboard import mostrar_dashboard_interactivo

st.set_page_config(page_title="IA Financiera Analisis de Portafolio",page_icon="🏢", layout="wide")

st.sidebar.title("IA Financiera")
opciones = st.sidebar.radio("Selecciona una opcion:", [
    "📥 Cargar Portafolio",
    "🏠 Inicio",
    "📊 Analisis del Portafolio",
    "📈 Proyecciones",
    "🎯 Meta y KPIs",
    "📘 Balance General",
    "📉 Devaluacion e Inflacion",
    "🕒 Historico del Portafolio",
    "🔥 Calculadora FIRE",
    "🛤️ Camino a tu meta",
    "🎯 Seguimiento de Metas",
    "📤 Generar Informe",
    "💬 Chat Financiero",
    "🧾 Evaluacion de Prestamo",
    "♻️ Rebalanceo", # Se mantiene la opcion en el sidebar
    "🐄 Activos Fisicos",
    "💱 Divisas",
    "💸 Gestion de Gastos",
    "🛡️ Evaluacion de Riesgo",
    "📘 Manual de Usuario"
])

# --- Inicializacion de variables de sesion (para que sean "estaticas" en la sesion) ---
# Es crucial inicializar estas variables al inicio de la aplicacion
# para que siempre existan, incluso en la primera ejecucion o despues de una recarga.

# DataFrame del portafolio: se inicializa a None si no existe
if "df" not in st.session_state:
    st.session_state.df = None

# Cargar los parámetros de la meta desde el archivo JSON al inicio de la sesión
initial_meta_params = load_meta_params()

# Variables de la "Ruta hacia la meta" (usadas en generador_informe.py)
if "capital_meta_informe" not in st.session_state:
    st.session_state.capital_meta_informe = initial_meta_params["capital_meta"]

if "inversion_mensual_informe" not in st.session_state:
    st.session_state.inversion_mensual_informe = initial_meta_params["inversion_mensual"]

if "ingreso_pasivo_objetivo_informe" not in st.session_state:
    st.session_state.ingreso_pasivo_objetivo_informe = initial_meta_params["ingreso_pasivo_objetivo"]

# Variables para el modulo "Devaluacion e Inflacion"
if "inflacion_anual_input" not in st.session_state:
    st.session_state.inflacion_anual_input = 3.0
if "anios_input" not in st.session_state:
    st.session_state.anios_input = 2
if "rentabilidad_mensual_input" not in st.session_state:
    st.session_state.rentabilidad_mensual_input = 1.79

# Variables para el modulo "Calculadora FIRE"
if "gastos_mensuales_fire" not in st.session_state:
    st.session_state.gastos_mensuales_fire = 0.0
if "editar_rendimiento_fire" not in st.session_state:
    st.session_state.editar_rendimiento_fire = False

# Variable para la rentabilidad anualizada en el modulo "Generar Informe"
if "rentabilidad_anualizada_informe" not in st.session_state:
    st.session_state.rentabilidad_anualizada_informe = 14.42

# Inicializar el DataFrame de gastos y presupuestos
if 'gastos_df' not in st.session_state:
    st.session_state.gastos_df = pd.DataFrame(columns=['Fecha', 'Descripcion', 'Monto', 'Categoria'])
if 'presupuestos' not in st.session_state:
    st.session_state.presupuestos = {}

# Inicializar la lista de metas financieras
if 'financial_goals' not in st.session_state:
    st.session_state.financial_goals = []
# -----------------------------------------------------------------------------


if opciones == "📥 Cargar Portafolio":
    st.session_state.df = cargar_datos()

elif opciones == "📊 Analisis del Portafolio":
    if st.session_state.df is not None:
        analizar_portafolio(st.session_state.df)
    else:
        st.warning("Primero debes cargar un archivo de portafolio.")

elif opciones == "📈 Proyecciones":
    if st.session_state.df is not None:
        simular_proyecciones(st.session_state.df)
    else:
        st.warning("Carga tu portafolio para ver proyecciones.")

elif opciones == "🎯 Meta y KPIs":
    if st.session_state.df is not None:
        mostrar_kpis(st.session_state.df)
    else:
        st.warning("Carga tu portafolio para calcular KPIs.")

elif opciones == "📘 Balance General":
    if st.session_state.df is not None:
        mostrar_balance_general(st.session_state.df)
    else:
        st.warning("Carga tu portafolio antes de ver el balance general.")


elif opciones == "📉 Devaluacion e Inflacion":
    if st.session_state.df is not None:
        df = st.session_state.df.copy()

        # Limpieza
        df['Dinero'] = df['Dinero'].replace('[\$,]', '', regex=True).astype(float)
        df['Interes Mensual'] = df['Interes Mensual'].replace('[\$,]', '', regex=True).fillna(0).astype(float)

        capital_productivo = df[df['Interes Mensual'] > 0]['Dinero'].sum()
        ingreso_pasivo_mensual = df['Interes Mensual'].sum()

        calcular_devaluacion(capital_productivo, ingreso_pasivo_mensual)
    else:
        st.warning("Carga tu portafolio primero.")


elif opciones == "🕒 Historico del Portafolio":
    if st.session_state.df is not None:
        guardar_snapshot(st.session_state.df)
    else:
        st.warning("Primero debes cargar un portafolio valido.")
    mostrar_historico()

elif opciones == "📤 Generar Informe":
    if st.session_state.df is not None:
        generar_docx(st.session_state.df)
    else:
        st.warning("Carga tu portafolio antes de generar el informe.")

elif opciones == "💬 Chat Financiero":
    if st.session_state.df is not None:
        chat_ia(st.session_state.df)
    else:
        st.warning("Carga tu portafolio para usar el chat financiero.")

elif opciones == "🧾 Evaluacion de Prestamo":
    evaluar_prestamo()

elif opciones == "♻️ Rebalanceo":
    if st.session_state.df is not None:
        mostrar_optimizacion_completa(st.session_state.df) # LLAMADA CORREGIDA AQUÍ
    else:
        st.warning("Carga tu portafolio para evaluar rebalanceo.")


elif opciones == "🐄 Activos Fisicos":
    gestionar_inversiones_fisicas()
    
elif opciones == "📘 Manual de Usuario":
    mostrar_manual_ia()

elif opciones == "💱 Divisas":
    mostrar_divisas()

elif opciones == "💸 Gestion de Gastos":
    mostrar_gestion_gastos()

elif opciones == "🛡️ Evaluacion de Riesgo":
    mostrar_evaluacion_riesgo(st.session_state.df)

elif opciones == "🎯 Seguimiento de Metas":
    mostrar_seguimiento_metas(st.session_state.df)
    
elif opciones == "🔥 Calculadora FIRE":
    if st.session_state.df is not None:
        df = st.session_state.df.copy()
        df['Dinero'] = pd.to_numeric(df['Dinero'].replace('[\$,]', '', regex=True), errors='coerce')
        df['Interes Mensual'] = pd.to_numeric(df['Interes Mensual'], errors='coerce').fillna(0)

        # Corregido: Calcular el capital productivo (solo el que genera ingresos)
        capital_productivo = df[df['Interes Mensual'] > 0]['Dinero'].sum()
        ingreso_pasivo_mensual = df['Interes Mensual'].sum()

        # Corregido: Usar capital_productivo en el calculo de la rentabilidad
        rentabilidad_aproximada = ((ingreso_pasivo_mensual * 12) / capital_productivo) * 100 if capital_productivo > 0 else 0

        # Corregido: Pasar el capital_productivo a la funcion calculadora_fire
        calculadora_fire(capital_productivo, ingreso_pasivo_mensual, rentabilidad_aproximada)
    else:
        st.warning("Primero debes cargar tu portafolio para usar la calculadora FIRE.")


elif opciones == "🛤️ Camino a tu meta":
    if st.session_state.df is not None:
        df = st.session_state.df.copy()
        df['Dinero'] = pd.to_numeric(df['Dinero'].replace('[\$,]', '', regex=True), errors='coerce')
        df['Interes Mensual'] = pd.to_numeric(df['Interes Mensual'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)

        # Calcular la rentabilidad anual como en la Calculadora FIRE
        capital_total = df['Dinero'].sum()
        ingreso_pasivo_mensual = df['Interes Mensual'].sum()
        rentabilidad = ((ingreso_pasivo_mensual * 12) / capital_total) * 100 if capital_total > 0 else 0

        target_capital_default = st.session_state.capital_meta_informe
        target_passive_income_default = st.session_state.ingreso_pasivo_objetivo_informe
        monthly_contribution_default = st.session_state.inversion_mensual_informe

        ruta_hacia_meta(
    df=df,
    capital_objetivo=target_capital_default,
    ingreso_pasivo_objetivo=target_passive_income_default,
    inversion_mensual=monthly_contribution_default
)

    else:
        st.warning("Primero debes cargar tu portafolio.")


elif opciones == "🏠 Inicio":
    
    if st.session_state.df is not None:
        mostrar_dashboard_interactivo(st.session_state.df)
    else:
        st.warning("Primero debes cargar tu portafolio.")



st.sidebar.markdown("---")
st.sidebar.caption("Desarrollado por Keyner Ruiz - IA Financiera")