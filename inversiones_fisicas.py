import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(page_title="Gestión de Activos Físicos", page_icon="🏢", layout="wide")

# Define el nombre del archivo para guardar los activos físicos
PHYSICAL_ASSETS_FILE = "physical_assets.json"

# --- Parámetros Agronómicos para Arroz (Valores de Referencia) ---
PH_ARROZ_MIN = 5.5
PH_ARROZ_MAX = 7.0
TEMP_ARROZ_MIN = 20.0
TEMP_ARROZ_MAX = 35.0
AGUA_ARROZ_REQUERIDA_MM = 1200  # mm de agua total requerida durante el ciclo de cultivo

# Parámetros adicionales para otros cultivos
CULTIVOS_PARAMETROS = {
    "Arroz": {"ph_min": 5.5, "ph_max": 7.0, "temp_min": 20, "temp_max": 35, "agua_mm": 1200},
    "Maíz": {"ph_min": 6.0, "ph_max": 7.5, "temp_min": 15, "temp_max": 30, "agua_mm": 800},
    "Café": {"ph_min": 6.0, "ph_max": 7.0, "temp_min": 18, "temp_max": 24, "agua_mm": 1500},
    "Cacao": {"ph_min": 6.0, "ph_max": 7.5, "temp_min": 21, "temp_max": 32, "agua_mm": 1800},
    "Plátano": {"ph_min": 5.5, "ph_max": 7.0, "temp_min": 26, "temp_max": 30, "agua_mm": 1200}
}

def formato_pesos(valor):
    """Formatea valores monetarios en pesos colombianos"""
    if pd.isna(valor) or valor is None:
        return "$0"
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def load_physical_assets():
    """Carga los activos físicos desde un archivo JSON"""
    if os.path.exists(PHYSICAL_ASSETS_FILE):
        with open(PHYSICAL_ASSETS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_physical_assets(assets_list):
    """Guarda los activos físicos en un archivo JSON"""
    with open(PHYSICAL_ASSETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(assets_list, f, indent=4, ensure_ascii=False)

def calcular_depreciacion(valor_adquisicion, vida_util_anos, anos_transcurridos):
    """Calcula la depreciación lineal de un activo"""
    if vida_util_anos <= 0 or anos_transcurridos <= 0:
        return 0
    depreciacion_anual = valor_adquisicion / vida_util_anos
    return min(depreciacion_anual * anos_transcurridos, valor_adquisicion)

def evaluar_condicion_agronomica(tipo_cultivo, ph_suelo, temp_cultivo, agua_disponible):
    """Evalúa las condiciones agronómicas para un cultivo específico"""
    if tipo_cultivo not in CULTIVOS_PARAMETROS:
        return True, []
    
    params = CULTIVOS_PARAMETROS[tipo_cultivo]
    condiciones_ok = True
    alertas = []
    
    if ph_suelo is not None:
        if not (params["ph_min"] <= ph_suelo <= params["ph_max"]):
            condiciones_ok = False
            alertas.append(f"❌ pH del suelo ({ph_suelo}) fuera del rango óptimo ({params['ph_min']}-{params['ph_max']})")
        else:
            alertas.append(f"✅ pH del suelo ({ph_suelo}) adecuado")
    
    if temp_cultivo is not None:
        if not (params["temp_min"] <= temp_cultivo <= params["temp_max"]):
            condiciones_ok = False
            alertas.append(f"❌ Temperatura ({temp_cultivo}°C) fuera del rango óptimo ({params['temp_min']}-{params['temp_max']}°C)")
        else:
            alertas.append(f"✅ Temperatura ({temp_cultivo}°C) adecuada")
    
    if agua_disponible is not None:
        if agua_disponible < params["agua_mm"] * 0.9:
            condiciones_ok = False
            alertas.append(f"❌ Agua disponible ({agua_disponible} mm) insuficiente (requiere {params['agua_mm']} mm)")
        elif agua_disponible < params["agua_mm"]:
            alertas.append(f"⚠️ Agua disponible ({agua_disponible} mm) límite")
        else:
            alertas.append(f"✅ Agua disponible ({agua_disponible} mm) suficiente")
    
    return condiciones_ok, alertas

def generar_recomendacion(tipo, roi_acumulado, rentabilidad, ratio_cb, periodo_recuperacion, **kwargs):
    """Genera recomendaciones específicas según el tipo de activo"""
    
    if tipo == "Cultivo":
        tipo_cultivo = kwargs.get('tipo_cultivo', 'Arroz')
        ph_suelo = kwargs.get('ph_suelo')
        temp_cultivo = kwargs.get('temp_cultivo')
        agua_disponible = kwargs.get('agua_disponible')
        
        condiciones_ok, alertas_agronomicas = evaluar_condicion_agronomica(
            tipo_cultivo, ph_suelo, temp_cultivo, agua_disponible
        )
        
        recomendaciones = alertas_agronomicas.copy()
        
        # Evaluación económica
        if roi_acumulado >= 40 and rentabilidad >= 10 and condiciones_ok:
            recomendaciones.append("✅ Cultivo altamente rentable y viable agronómicamente")
        elif roi_acumulado >= 25 and condiciones_ok:
            recomendaciones.append("⚠️ Rentabilidad moderada. Considerar optimizaciones")
        elif not condiciones_ok:
            recomendaciones.append("❌ Condiciones agronómicas críticas requieren atención inmediata")
        else:
            recomendaciones.append("❌ Baja rentabilidad. Evaluar cambio de cultivo o técnicas")
        
        return " | ".join(recomendaciones)
    
    elif tipo == "Semoviente":
        if roi_acumulado >= 36 and ratio_cb >= 2:
            return "✅ Ganadería rentable con buen control de costos"
        elif roi_acumulado >= 20:
            return "⚠️ Rentabilidad media. Revisar manejo técnico y sanitario"
        else:
            return "❌ Alto riesgo. Reconsiderar escala o manejo del hato"
    
    elif tipo == "Bien raiz":
        if periodo_recuperacion <= 10 and roi_acumulado >= 25:
            return "✅ Excelente inversión inmobiliaria para renta pasiva"
        elif roi_acumulado >= 10:
            return "⚠️ Rentabilidad baja pero estable. Evaluar plusvalía"
        else:
            return "❌ Retorno muy lento. No recomendado sin valorización"
    
    elif tipo == "Infraestructura":
        if roi_acumulado >= 30:
            return "✅ Infraestructura eficiente con buen retorno"
        elif roi_acumulado >= 15:
            return "⚠️ Rentabilidad moderada. Posible subutilización"
        else:
            return "❌ Inversión no recuperada. Revisar uso y mantenimiento"
    
    elif tipo == "Maquinaria":
        if ratio_cb >= 2 and periodo_recuperacion <= 5:
            return "✅ Maquinaria altamente eficiente y productiva"
        elif roi_acumulado >= 15:
            return "⚠️ Útil pero costosa. Optimizar uso y mantenimiento"
        else:
            return "❌ Subutilizada. Considerar venta o alquiler"
    
    else:
        if roi_acumulado >= 30:
            return "✅ Buena inversión alternativa"
        elif roi_acumulado >= 10:
            return "⚠️ Rentabilidad aceptable"
        else:
            return "❌ Retorno insuficiente"

def eliminar_activo_seguro(activo_a_eliminar, activos_list):
    """Elimina un activo específico sin afectar la lista completa"""
    # Extraer el ID del activo seleccionado
    if " - ID:" in activo_a_eliminar:
        id_eliminar = int(activo_a_eliminar.split(" - ID:")[-1].split(")")[0])
        activos_filtrados = [a for a in activos_list if a.get("ID") != id_eliminar]
    else:
        # Método alternativo por descripción + tipo
        partes = activo_a_eliminar.split(" (")
        descripcion_eliminar = partes[0]
        tipo_eliminar = partes[1].rstrip(")") if len(partes) > 1 else ""
        
        activos_filtrados = [
            a for a in activos_list 
            if not (a["Descripción"] == descripcion_eliminar and a["Tipo"] == tipo_eliminar)
        ]
    
    return activos_filtrados

def gestionar_venta_ganado(activo_ganadero, datos_venta):
    """Gestiona la venta de ganado manteniendo el activo base"""
    # Calcular ganancia por la venta
    peso_vendido = datos_venta['peso_kg']
    precio_por_kg = datos_venta['precio_kg']
    costo_crianza_por_animal = datos_venta.get('costo_crianza', 0)
    cantidad = datos_venta['cantidad']
    
    ingreso_venta = cantidad * peso_vendido * precio_por_kg
    costo_total_venta = cantidad * costo_crianza_por_animal
    utilidad_venta = ingreso_venta - costo_total_venta
    
    # Registrar la transacción en el historial del activo
    if 'historial_ventas' not in activo_ganadero:
        activo_ganadero['historial_ventas'] = []
    
    venta_registro = {
        'fecha': datos_venta['fecha'],
        'tipo_animal': datos_venta['tipo_animal'],
        'cantidad': cantidad,
        'peso_promedio_kg': peso_vendido,
        'precio_por_kg': precio_por_kg,
        'ingreso_total': ingreso_venta,
        'costo_crianza_total': costo_total_venta,
        'utilidad': utilidad_venta,
        'comprador': datos_venta.get('comprador', ''),
        'observaciones': datos_venta.get('observaciones', '')
    }
    
    activo_ganadero['historial_ventas'].append(venta_registro)
    
    # Actualizar métricas del activo principal
    actualizar_metricas_ganaderas(activo_ganadero)
    
    return activo_ganadero, venta_registro

def actualizar_metricas_ganaderas(activo_ganadero):
    """Actualiza las métricas financieras considerando las ventas"""
    historial = activo_ganadero.get('historial_ventas', [])
    
    if historial:
        # Calcular ingresos adicionales por ventas en el último año
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=365)
        
        ventas_ultimo_ano = [
            v for v in historial 
            if datetime.fromisoformat(v['fecha']) >= fecha_limite
        ]
        
        # Calcular ingresos y costos adicionales por ventas
        ingresos_ventas_anual = sum(v['ingreso_total'] for v in ventas_ultimo_ano)
        costos_ventas_anual = sum(v['costo_crianza_total'] for v in ventas_ultimo_ano)
        
        # Sumar a los ingresos base del activo
        ingreso_base = activo_ganadero.get('Ingreso Anual', 0)
        activo_ganadero['Ingreso Anual Total'] = ingreso_base + ingresos_ventas_anual
        
        # Actualizar costos totales
        costos_base = activo_ganadero.get('Costos Mensuales', 0) * 12
        activo_ganadero['Costos Anuales Total'] = costos_base + costos_ventas_anual
        
        # Recalcular ROI considerando ventas
        valor_inversion = activo_ganadero.get('Valor de Adquisición', 0)
        utilidad_total = activo_ganadero['Ingreso Anual Total'] - activo_ganadero['Costos Anuales Total']
        
        if valor_inversion > 0:
            activo_ganadero['ROI con Ventas (%)'] = (utilidad_total / valor_inversion) * 100
            # Actualizar también el ROI principal
            horizonte = activo_ganadero.get('Horizonte', 5)
            activo_ganadero['ROI Acumulado (%)'] = (utilidad_total * horizonte / valor_inversion) * 100
        
        # Estadísticas de ventas
        activo_ganadero['Total Animales Vendidos'] = sum(v['cantidad'] for v in historial)
        activo_ganadero['Utilidad Total Ventas'] = sum(v['utilidad'] for v in historial)
        if historial:
            activo_ganadero['Precio Promedio por KG'] = sum(v['precio_por_kg'] for v in historial) / len(historial)

def crear_dashboard_financiero(df_activos):
    """Crea visualizaciones del desempeño financiero"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de ROI por tipo de activo
        roi_por_tipo = df_activos.groupby('Tipo')['ROI Acumulado (%)'].mean().reset_index()
        fig_roi = px.bar(roi_por_tipo, x='Tipo', y='ROI Acumulado (%)', 
                        title='ROI Promedio por Tipo de Activo',
                        color='ROI Acumulado (%)', color_continuous_scale='RdYlGn')
        fig_roi.update_layout(height=400)
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Gráfico de distribución de valor por tipo
        valor_por_tipo = df_activos.groupby('Tipo')['Valor Actual'].sum().reset_index()
        fig_valor = px.pie(valor_por_tipo, values='Valor Actual', names='Tipo', 
                          title='Distribución de Valor por Tipo de Activo')
        fig_valor.update_layout(height=400)
        st.plotly_chart(fig_valor, use_container_width=True)
    
    # Análisis de rentabilidad vs riesgo
    st.subheader("Análisis Rentabilidad vs Período de Recuperación")
    fig_scatter = px.scatter(df_activos, x='Periodo de Recuperación (años)', y='ROI Acumulado (%)',
                           size='Valor Actual', color='Tipo', hover_name='Descripción',
                           title='Matriz Riesgo-Rentabilidad')
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

def tab_ventas_ganaderas():
    """Nueva pestaña para gestionar ventas de ganado"""
    st.header("🐄 Gestión de Ventas Ganaderas")
    
    # Filtrar solo activos semovientes
    activos_ganado = [a for a in st.session_state.activos_fisicos if a['Tipo'] == 'Semoviente']
    
    if not activos_ganado:
        st.info("📝 No hay activos semovientes registrados para gestionar ventas")
        return
    
    # Seleccionar activo ganadero
    nombres_ganado = [f"{a['Descripción']} - {a.get('Tipo Ganado', 'N/A')}" for a in activos_ganado]
    ganado_seleccionado = st.selectbox("Seleccionar hato ganadero", nombres_ganado)
    
    if ganado_seleccionado:
        # Encontrar el activo seleccionado
        descripcion_seleccionada = ganado_seleccionado.split(" - ")[0]
        activo_seleccionado = next(
            (a for a in activos_ganado if a['Descripción'] == descripcion_seleccionada), 
            None
        )
        
        if activo_seleccionado:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Información del Hato")
                st.write(f"**Tipo de ganado:** {activo_seleccionado.get('Tipo Ganado', 'N/A')}")
                st.write(f"**Número de animales:** {activo_seleccionado.get('Número Animales', 'N/A')}")
                st.write(f"**ROI actual:** {activo_seleccionado.get('ROI Acumulado (%)', 0):.1f}%")
                
                # Mostrar historial de ventas si existe
                historial = activo_seleccionado.get('historial_ventas', [])
                if historial:
                    st.write(f"**Animales vendidos:** {sum(v['cantidad'] for v in historial)}")
                    st.write(f"**Utilidad total ventas:** {formato_pesos(sum(v['utilidad'] for v in historial))}")
                    
                    # Mostrar ROI con ventas si existe
                    roi_con_ventas = activo_seleccionado.get('ROI con Ventas (%)')
                    if roi_con_ventas:
                        st.write(f"**ROI con ventas:** {roi_con_ventas:.1f}%")
            
            with col2:
                st.subheader("💰 Registrar Nueva Venta")
                
                with st.form("venta_ganado"):
                    fecha_venta = st.date_input("Fecha de venta", value=date.today())
                    tipo_animal = st.selectbox("Tipo de animal vendido", 
                        ["Ternero", "Ternera", "Novillo", "Novilla", "Toro", "Vaca", "Buey"])
                    
                    col_form1, col_form2 = st.columns(2)
                    
                    with col_form1:
                        cantidad = st.number_input("Cantidad de animales", min_value=1, step=1)
                        peso_kg = st.number_input("Peso promedio (kg)", min_value=50.0, step=10.0, format="%.1f")
                    
                    with col_form2:
                        precio_kg = st.number_input("Precio por kg (COP)", min_value=1000.0, step=500.0, format="%.0f")
                        costo_crianza = st.number_input("Costo de crianza por animal (COP)", min_value=0.0, step=50000.0, format="%.0f")
                    
                    comprador = st.text_input("Comprador (opcional)")
                    observaciones = st.text_area("Observaciones", height=80)
                    
                    # Calcular automáticamente
                    ingreso_total = cantidad * peso_kg * precio_kg
                    costo_total = cantidad * costo_crianza
                    utilidad_estimada = ingreso_total - costo_total
                    
                    st.success(f"💰 Ingreso estimado: {formato_pesos(ingreso_total)}")
                    st.success(f"💸 Costo total: {formato_pesos(costo_total)}")
                    if utilidad_estimada >= 0:
                        st.success(f"📈 Utilidad estimada: {formato_pesos(utilidad_estimada)}")
                    else:
                        st.error(f"📉 Pérdida estimada: {formato_pesos(abs(utilidad_estimada))}")
                    
                    registrar_venta = st.form_submit_button("💾 Registrar Venta", type="primary")
                
                if registrar_venta:
                    datos_venta = {
                        'fecha': fecha_venta.isoformat(),
                        'tipo_animal': tipo_animal,
                        'cantidad': cantidad,
                        'peso_kg': peso_kg,
                        'precio_kg': precio_kg,
                        'costo_crianza': costo_crianza,
                        'comprador': comprador,
                        'observaciones': observaciones
                    }
                    
                    # Procesar la venta
                    activo_actualizado, registro_venta = gestionar_venta_ganado(activo_seleccionado, datos_venta)
                    
                    # Actualizar el activo en la lista
                    for i, activo in enumerate(st.session_state.activos_fisicos):
                        if activo['ID'] == activo_seleccionado['ID']:
                            st.session_state.activos_fisicos[i] = activo_actualizado
                            break
                    
                    save_physical_assets(st.session_state.activos_fisicos)
                    st.success("✅ Venta registrada correctamente!")
                    st.rerun()
            
            # Mostrar historial de ventas
            if activo_seleccionado.get('historial_ventas'):
                st.markdown("---")
                st.subheader("📋 Historial de Ventas")
                
                df_ventas = pd.DataFrame(activo_seleccionado['historial_ventas'])
                df_ventas['Fecha'] = pd.to_datetime(df_ventas['fecha']).dt.strftime('%d/%m/%Y')
                
                # Mostrar tabla de ventas
                columnas_mostrar = ['Fecha', 'tipo_animal', 'cantidad', 'peso_promedio_kg', 
                                  'precio_por_kg', 'ingreso_total', 'utilidad']
                
                st.dataframe(
                    df_ventas[columnas_mostrar].rename(columns={
                        'tipo_animal': 'Tipo Animal',
                        'cantidad': 'Cantidad',
                        'peso_promedio_kg': 'Peso Prom. (kg)',
                        'precio_por_kg': 'Precio/kg',
                        'ingreso_total': 'Ingreso Total',
                        'utilidad': 'Utilidad'
                    }).style.format({
                        'Precio/kg': lambda x: formato_pesos(x),
                        'Ingreso Total': lambda x: formato_pesos(x),
                        'Utilidad': lambda x: formato_pesos(x)
                    }),
                    use_container_width=True
                )
                
                # Mostrar resumen de ventas
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric("Total Vendido", formato_pesos(df_ventas['ingreso_total'].sum()))
                with col_res2:
                    st.metric("Total Animales", int(df_ventas['cantidad'].sum()))
                with col_res3:
                    st.metric("Utilidad Total", formato_pesos(df_ventas['utilidad'].sum()))

def seccion_administracion_mejorada():
    """Sección de administración con eliminación segura"""
    st.header("🔧 Administración del Sistema")
    
    if st.session_state.activos_fisicos:
        # Eliminar activo (VERSIÓN MEJORADA)
        st.subheader("🗑️ Eliminar Activo")
        
        # Crear lista más descriptiva con IDs únicos
        opciones_eliminar = ["Ninguno"]
        for activo in st.session_state.activos_fisicos:
            descripcion_completa = f"{activo['Descripción']} ({activo['Tipo']}) - ID:{activo['ID']}"
            opciones_eliminar.append(descripcion_completa)
        
        activo_a_eliminar = st.selectbox("Seleccionar activo a eliminar", opciones_eliminar)
        
        if activo_a_eliminar != "Ninguno":
            # Mostrar detalles del activo seleccionado
            try:
                id_seleccionado = int(activo_a_eliminar.split(" - ID:")[1])
                activo_detalle = next((a for a in st.session_state.activos_fisicos if a['ID'] == id_seleccionado), None)
                
                if activo_detalle:
                    st.info(f"""
                    **Activo seleccionado:**
                    - Tipo: {activo_detalle['Tipo']}
                    - Valor: {formato_pesos(activo_detalle['Valor Actual'])}
                    - ROI: {activo_detalle['ROI Acumulado (%)']}%
                    """)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        confirmar = st.checkbox("Confirmo que deseo eliminar este activo")
                    with col2:
                        if confirmar and st.button("🗑️ Eliminar activo", type="secondary"):
                            # Usar la función de eliminación segura
                            st.session_state.activos_fisicos = eliminar_activo_seguro(
                                activo_a_eliminar, st.session_state.activos_fisicos
                            )
                            save_physical_assets(st.session_state.activos_fisicos)
                            st.success(f"✅ Activo eliminado correctamente.")
                            st.rerun()
            except (ValueError, IndexError):
                st.error("Error al procesar la selección del activo")
        
        st.markdown("---")
        
        # Exportar datos
        st.subheader("📤 Exportar Datos")
        if st.button("📥 Descargar datos como CSV"):
            df_export = pd.DataFrame(st.session_state.activos_fisicos)
            csv = df_export.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"activos_fisicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Limpiar todos los datos
        st.subheader("⚠️ Zona Peligrosa")
        if st.button("🚨 Eliminar TODOS los activos", type="secondary"):
            if st.checkbox("Confirmo que deseo eliminar todos los datos"):
                st.session_state.activos_fisicos = []
                save_physical_assets([])
                st.warning("⚠️ Todos los activos han sido eliminados.")
                st.rerun()
    else:
        st.info("📝 No hay datos para administrar")

def gestionar_inversiones_fisicas():
    """Función principal para gestionar activos físicos"""
    
    st.title("🏢 Sistema de Gestión de Activos Físicos")
    st.markdown("---")
    
    # Inicializar session state
    if "activos_fisicos" not in st.session_state:
        st.session_state.activos_fisicos = load_physical_assets()
    
    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Registro de Activos", 
        "📊 Dashboard", 
        "📋 Listado Completo", 
        "🐄 Ventas Ganaderas",
        "🔧 Administración"
    ])
    
    with tab1:
        st.header("Registro de Nuevo Activo")
        
        # Selección del tipo de activo
        tipo_activo = st.selectbox("🏷️ Selecciona el tipo de activo", 
            ["Seleccionar...", "Bien raíz", "Cultivo", "Semoviente", "Infraestructura", "Maquinaria", "Otro"])
        
        if tipo_activo == "Seleccionar...":
            st.info("👆 Selecciona un tipo de activo para continuar")
            return
        
        # Formularios específicos por tipo de activo
        with st.form("form_fisico"):
            # Campos comunes para todos los activos
            st.subheader("📋 Información General")
            col1, col2 = st.columns(2)
            
            with col1:
                descripcion = st.text_input("Descripción del activo")
                ubicacion = st.text_input("Ubicación")
                fecha_adquisicion = st.date_input("Fecha de adquisición", value=date.today())
            
            with col2:
                valor_adquisicion = st.number_input("Valor de adquisición (COP)", min_value=0.0, step=100000.0, format="%.0f")
                valor_inicial = st.number_input("Valor actual/estimado (COP)", min_value=0.0, step=100000.0, format="%.0f")
                horizonte = st.number_input("Horizonte de análisis (años)", min_value=1, max_value=50, step=1, value=5)
            
            st.markdown("---")
            
            # Variables para campos específicos
            (tipo_cultivo, ph_suelo, temp_cultivo, agua_disponible, superficie_hectareas, 
             rendimiento_ton_ha, precio_ton, costos_hectarea) = (None,) * 8
            
            (tipo_ganado, numero_animales, peso_promedio, precio_kg, tasa_natalidad, 
             tasa_mortalidad, costos_animal_mes, ciclo_produccion) = (None,) * 8
            
            (tipo_inmueble, area_m2, canon_arriendo_mes, gastos_admin_mes, 
             impuestos_anuales, valorizacion_anual) = (None,) * 6
            
            (tipo_infraestructura, capacidad_operacion, tarifa_uso, horas_uso_mes, 
             costos_mantenimiento_mes, costos_operacion_mes) = (None,) * 6
            
            (tipo_maquina, marca_modelo, año_fabricacion, horas_trabajo_mes, 
             tarifa_hora, combustible_mes, mantenimiento_mes) = (None,) * 7
            
            # FORMULARIO ESPECÍFICO PARA CULTIVOS
            if tipo_activo == "Cultivo":
                st.subheader("🌾 Información del Cultivo")
                col3, col4 = st.columns(2)
                
                with col3:
                    tipo_cultivo = st.selectbox("Tipo de cultivo", list(CULTIVOS_PARAMETROS.keys()))
                    superficie_hectareas = st.number_input("Superficie (hectáreas)", min_value=0.1, step=0.1, format="%.2f")
                    rendimiento_ton_ha = st.number_input("Rendimiento esperado (ton/ha)", min_value=0.1, step=0.1, format="%.2f")
                    precio_ton = st.number_input("Precio por tonelada (COP)", min_value=0.0, step=1000.0, format="%.0f")
                
                with col4:
                    costos_hectarea = st.number_input("Costos de producción por hectárea/año (COP)", min_value=0.0, step=10000.0, format="%.0f")
                    ph_suelo = st.slider("pH del Suelo", min_value=4.0, max_value=8.5, value=6.0, step=0.1)
                    temp_cultivo = st.slider("Temperatura promedio (°C)", min_value=10.0, max_value=45.0, value=25.0, step=0.5)
                    agua_disponible = st.number_input("Agua disponible (mm/ciclo)", 
                        min_value=0.0, value=float(CULTIVOS_PARAMETROS.get(tipo_cultivo, {"agua_mm": 1000})["agua_mm"]), step=50.0)
                
                # Mostrar parámetros óptimos
                if tipo_cultivo:
                    params = CULTIVOS_PARAMETROS[tipo_cultivo]
                    st.info(f"""
                    **Parámetros óptimos para {tipo_cultivo}:**
                    - pH: {params['ph_min']} - {params['ph_max']}
                    - Temperatura: {params['temp_min']}°C - {params['temp_max']}°C  
                    - Agua: {params['agua_mm']} mm/ciclo
                    """)
                
                # Calcular ingresos y costos automáticamente
                ingreso_anual = superficie_hectareas * rendimiento_ton_ha * precio_ton if all([superficie_hectareas, rendimiento_ton_ha, precio_ton]) else 0
                costos_mensuales = (superficie_hectareas * costos_hectarea) / 12 if all([superficie_hectareas, costos_hectarea]) else 0
                vida_util = 1  # Los cultivos son anuales
                
                st.success(f"💰 Ingreso anual estimado: {formato_pesos(ingreso_anual)}")
                st.success(f"💸 Costos mensuales estimados: {formato_pesos(costos_mensuales)}")
            
            # FORMULARIO ESPECÍFICO PARA SEMOVIENTES
            elif tipo_activo == "Semoviente":
                st.subheader("🐄 Información Ganadera")
                col3, col4 = st.columns(2)
                
                with col3:
                    tipo_ganado = st.selectbox("Tipo de ganado", ["Bovinos carne", "Bovinos leche", "Porcinos", "Aves postura", "Aves engorde", "Ovinos", "Caprinos"])
                    numero_animales = st.number_input("Número de animales", min_value=1, step=1)
                    peso_promedio = st.number_input("Peso promedio (kg)", min_value=1.0, step=1.0, format="%.1f")
                    precio_kg = st.number_input("Precio por kg (COP)", min_value=0.0, step=100.0, format="%.0f")
                
                with col4:
                    tasa_natalidad = st.slider("Tasa de natalidad anual (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
                    tasa_mortalidad = st.slider("Tasa de mortalidad anual (%)", min_value=0.0, max_value=20.0, value=3.0, step=1.0)
                    costos_animal_mes = st.number_input("Costos por animal/mes (COP)", min_value=0.0, step=1000.0, format="%.0f")
                    ciclo_produccion = st.number_input("Ciclo de producción (meses)", min_value=1, max_value=60, step=1, value=12)
                
                # Calcular ingresos y costos
                if tipo_ganado in ["Bovinos carne", "Porcinos", "Aves engorde"]:
                    # Para ganado de carne: venta por peso
                    ingreso_anual = numero_animales * peso_promedio * precio_kg * (tasa_natalidad/100) if all([numero_animales, peso_promedio, precio_kg]) else 0
                else:
                    # Para leche y huevos: producción continua
                    ingreso_anual = numero_animales * precio_kg * 365 if all([numero_animales, precio_kg]) else 0  # precio_kg sería precio por litro o docena
                
                costos_mensuales = numero_animales * costos_animal_mes if all([numero_animales, costos_animal_mes]) else 0
                vida_util = 8  # Vida útil promedio del ganado
                
                st.success(f"💰 Ingreso anual estimado: {formato_pesos(ingreso_anual)}")
                st.success(f"💸 Costos mensuales estimados: {formato_pesos(costos_mensuales)}")
            
            # FORMULARIO ESPECÍFICO PARA BIENES RAÍCES
            elif tipo_activo == "Bien raíz":
                st.subheader("🏠 Información Inmobiliaria")
                col3, col4 = st.columns(2)
                
                with col3:
                    tipo_inmueble = st.selectbox("Tipo de inmueble", ["Casa", "Apartamento", "Local comercial", "Oficina", "Bodega", "Lote", "Finca", "Otro"])
                    area_m2 = st.number_input("Área (m²)", min_value=1.0, step=1.0, format="%.1f")
                    canon_arriendo_mes = st.number_input("Canon de arriendo mensual (COP)", min_value=0.0, step=10000.0, format="%.0f")
                
                with col4:
                    gastos_admin_mes = st.number_input("Gastos administración/mes (COP)", min_value=0.0, step=1000.0, format="%.0f")
                    impuestos_anuales = st.number_input("Impuestos anuales (COP)", min_value=0.0, step=10000.0, format="%.0f")
                    valorizacion_anual = st.slider("Valorización esperada anual (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
                
                # Calcular ingresos y costos
                ingreso_anual = (canon_arriendo_mes * 12) + (valor_inicial * valorizacion_anual/100) if all([canon_arriendo_mes, valor_inicial]) else 0
                costos_mensuales = gastos_admin_mes + (impuestos_anuales/12) if impuestos_anuales else gastos_admin_mes or 0
                vida_util = 50  # Vida útil de inmuebles
                
                st.success(f"💰 Ingreso anual estimado: {formato_pesos(ingreso_anual)}")
                st.success(f"💸 Costos mensuales estimados: {formato_pesos(costos_mensuales)}")
            
            # FORMULARIO ESPECÍFICO PARA INFRAESTRUCTURA
            elif tipo_activo == "Infraestructura":
                st.subheader("🏗️ Información de Infraestructura")
                col3, col4 = st.columns(2)
                
                with col3:
                    tipo_infraestructura = st.selectbox("Tipo de infraestructura", 
                        ["Planta procesamiento", "Sistema de riego", "Invernadero", "Establo", "Galón", "Silo", "Centro acopio", "Otro"])
                    capacidad_operacion = st.number_input("Capacidad operativa (unidad/mes)", min_value=1.0, step=1.0, format="%.1f")
                    tarifa_uso = st.number_input("Tarifa por unidad de uso (COP)", min_value=0.0, step=100.0, format="%.0f")
                
                with col4:
                    horas_uso_mes = st.number_input("Horas de uso por mes", min_value=1.0, max_value=744.0, step=1.0, format="%.0f")
                    costos_mantenimiento_mes = st.number_input("Costos mantenimiento/mes (COP)", min_value=0.0, step=10000.0, format="%.0f")
                    costos_operacion_mes = st.number_input("Costos operación/mes (COP)", min_value=0.0, step=10000.0, format="%.0f")
                
                # Calcular ingresos y costos
                ingreso_anual = (capacidad_operacion * tarifa_uso * 12) if all([capacidad_operacion, tarifa_uso]) else 0
                costos_mensuales = costos_mantenimiento_mes + costos_operacion_mes if costos_mantenimiento_mes or costos_operacion_mes else 0
                vida_util = 25  # Vida útil de infraestructura
                
                st.success(f"💰 Ingreso anual estimado: {formato_pesos(ingreso_anual)}")
                st.success(f"💸 Costos mensuales estimados: {formato_pesos(costos_mensuales)}")
            
            # FORMULARIO ESPECÍFICO PARA MAQUINARIA
            elif tipo_activo == "Maquinaria":
                st.subheader("🚜 Información de Maquinaria")
                col3, col4 = st.columns(2)
                
                with col3:
                    tipo_maquina = st.selectbox("Tipo de maquinaria", 
                        ["Tractor", "Cosechadora", "Sembradora", "Fumigadora", "Arado", "Rastra", "Ordeñadora", "Picadora", "Otro"])
                    marca_modelo = st.text_input("Marca y modelo")
                    año_fabricacion = st.number_input("Año de fabricación", min_value=1980, max_value=date.today().year, step=1)
                    horas_trabajo_mes = st.number_input("Horas de trabajo por mes", min_value=1.0, max_value=744.0, step=1.0, format="%.0f")
                
                with col4:
                    tarifa_hora = st.number_input("Tarifa por hora de trabajo (COP)", min_value=0.0, step=1000.0, format="%.0f")
                    combustible_mes = st.number_input("Costos combustible/mes (COP)", min_value=0.0, step=10000.0, format="%.0f")
                    mantenimiento_mes = st.number_input("Costos mantenimiento/mes (COP)", min_value=0.0, step=5000.0, format="%.0f")
                
                # Calcular ingresos y costos
                ingreso_anual = (horas_trabajo_mes * tarifa_hora * 12) if all([horas_trabajo_mes, tarifa_hora]) else 0
                costos_mensuales = combustible_mes + mantenimiento_mes if combustible_mes or mantenimiento_mes else 0
                vida_util = 15  # Vida útil de maquinaria
                
                st.success(f"💰 Ingreso anual estimado: {formato_pesos(ingreso_anual)}")
                st.success(f"💸 Costos mensuales estimados: {formato_pesos(costos_mensuales)}")
            
            # FORMULARIO PARA OTROS ACTIVOS
            else:  # tipo_activo == "Otro"
                st.subheader("📦 Información del Activo")
                col3, col4 = st.columns(2)
                
                with col3:
                    ingreso_anual = st.number_input("Ingreso anual esperado (COP)", min_value=0.0, step=10000.0, format="%.0f")
                    costos_mensuales = st.number_input("Costos mensuales (COP)", min_value=0.0, step=5000.0, format="%.0f")
                
                with col4:
                    vida_util = st.number_input("Vida útil estimada (años)", min_value=1, max_value=100, step=1, value=10)
                    st.text_area("Observaciones adicionales", height=100)
            
            enviar = st.form_submit_button("🔄 Agregar Activo y Evaluar", type="primary")
        
        if enviar and descripcion and valor_inicial > 0 and valor_adquisicion > 0 and ingreso_anual is not None:
            # Validaciones adicionales
            if fecha_adquisicion > date.today():
                st.error("❌ La fecha de adquisición no puede ser futura")
                return
            
            try:
                # Cálculos financieros
                años_transcurridos = (date.today() - fecha_adquisicion).days / 365.25
                depreciacion = calcular_depreciacion(valor_adquisicion, vida_util, años_transcurridos)
                
                ingreso_total = ingreso_anual
                costo_total_anual = costos_mensuales * 12
                utilidad_neta_anual = ingreso_total - costo_total_anual
                utilidad_neta_horizonte = utilidad_neta_anual * horizonte
                
                rentabilidad = (ingreso_total / valor_adquisicion) * 100 if valor_adquisicion else 0
                ratio_costo_beneficio = ingreso_total / costo_total_anual if costo_total_anual > 0 else float('inf')
                roi_acumulado = (utilidad_neta_anual * horizonte / valor_adquisicion) * 100 if valor_adquisicion > 0 else 0
                periodo_recuperacion = valor_adquisicion / utilidad_neta_anual if utilidad_neta_anual > 0 else float('inf')
                
                # Generar recomendación
                recomendacion = generar_recomendacion(
                    tipo_activo, roi_acumulado, rentabilidad, ratio_costo_beneficio, periodo_recuperacion,
                    tipo_cultivo=tipo_cultivo, ph_suelo=ph_suelo, temp_cultivo=temp_cultivo, agua_disponible=agua_disponible
                )
                
                # Crear nuevo activo con campos específicos
                nuevo_activo = {
                    "ID": len(st.session_state.activos_fisicos) + 1,
                    "Tipo": tipo_activo,
                    "Descripción": descripcion,
                    "Ubicación": ubicacion,
                    "Valor Actual": valor_inicial,
                    "Valor de Adquisición": valor_adquisicion,
                    "Fecha Adquisición": fecha_adquisicion.isoformat(),
                    "Depreciación Acumulada": depreciacion,
                    "Ingreso Anual": ingreso_anual,
                    "Costos Mensuales": costos_mensuales,
                    "Horizonte": horizonte,
                    "Vida Útil": vida_util,
                    "Años Transcurridos": round(años_transcurridos, 2),
                    "Rentabilidad (%)": round(rentabilidad, 2),
                    "Utilidad Neta Anual": utilidad_neta_anual,
                    "Utilidad Neta Horizonte": utilidad_neta_horizonte,
                    "Ratio C/B": round(ratio_costo_beneficio, 2),
                    "ROI Acumulado (%)": round(roi_acumulado, 2),
                    "Periodo de Recuperación (años)": round(periodo_recuperacion, 2) if periodo_recuperacion != float('inf') else "∞",
                    "Recomendación": recomendacion,
                    "Fecha Registro": datetime.now().isoformat()
                }
                
                # Agregar campos específicos según el tipo de activo
                if tipo_activo == "Cultivo":
                    nuevo_activo.update({
                        "Tipo Cultivo": tipo_cultivo,
                        "Superficie (ha)": superficie_hectareas,
                        "Rendimiento (ton/ha)": rendimiento_ton_ha,
                        "Precio por tonelada": precio_ton,
                        "Costos por hectárea": costos_hectarea,
                        "pH Suelo": ph_suelo,
                        "Temperatura (°C)": temp_cultivo,
                        "Agua Disponible (mm)": agua_disponible
                    })
                
                elif tipo_activo == "Semoviente":
                    nuevo_activo.update({
                        "Tipo Ganado": tipo_ganado,
                        "Número Animales": numero_animales,
                        "Peso Promedio (kg)": peso_promedio,
                        "Precio por kg": precio_kg,
                        "Tasa Natalidad (%)": tasa_natalidad,
                        "Tasa Mortalidad (%)": tasa_mortalidad,
                        "Costos por animal/mes": costos_animal_mes,
                        "Ciclo Producción (meses)": ciclo_produccion
                    })
                
                elif tipo_activo == "Bien raíz":
                    nuevo_activo.update({
                        "Tipo Inmueble": tipo_inmueble,
                        "Área (m²)": area_m2,
                        "Canon Arriendo/mes": canon_arriendo_mes,
                        "Gastos Admin/mes": gastos_admin_mes,
                        "Impuestos Anuales": impuestos_anuales,
                        "Valorización Anual (%)": valorizacion_anual
                    })
                
                elif tipo_activo == "Infraestructura":
                    nuevo_activo.update({
                        "Tipo Infraestructura": tipo_infraestructura,
                        "Capacidad Operación": capacidad_operacion,
                        "Tarifa por Uso": tarifa_uso,
                        "Horas Uso/mes": horas_uso_mes,
                        "Costos Mantenimiento/mes": costos_mantenimiento_mes,
                        "Costos Operación/mes": costos_operacion_mes
                    })
                
                elif tipo_activo == "Maquinaria":
                    nuevo_activo.update({
                        "Tipo Maquinaria": tipo_maquina,
                        "Marca y Modelo": marca_modelo,
                        "Año Fabricación": año_fabricacion,
                        "Horas Trabajo/mes": horas_trabajo_mes,
                        "Tarifa por Hora": tarifa_hora,
                        "Costos Combustible/mes": combustible_mes,
                        "Costos Mantenimiento/mes": mantenimiento_mes
                    })
                
                st.session_state.activos_fisicos.append(nuevo_activo)
                save_physical_assets(st.session_state.activos_fisicos)
                st.success("✅ Activo físico agregado correctamente.")
                st.rerun()
                
            except (ValueError, TypeError, ZeroDivisionError) as e:
                st.error(f"❌ Error en los cálculos: {str(e)}")
    
    with tab2:
        if st.session_state.activos_fisicos:
            df_activos = pd.DataFrame(st.session_state.activos_fisicos)
            
            # Métricas principales
            st.header("📊 Dashboard Financiero")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_valor = df_activos["Valor Actual"].sum()
                st.metric("Valor Total Activos", formato_pesos(total_valor))
            with col2:
                total_ingreso = df_activos["Ingreso Anual"].sum()
                st.metric("Ingreso Anual Total", formato_pesos(total_ingreso))
            with col3:
                rentabilidad_promedio = df_activos["Rentabilidad (%)"].mean()
                st.metric("Rentabilidad Promedio", f"{rentabilidad_promedio:.1f}%")
            with col4:
                roi_promedio = df_activos["ROI Acumulado (%)"].mean()
                st.metric("ROI Promedio", f"{roi_promedio:.1f}%")
            
            st.markdown("---")
            crear_dashboard_financiero(df_activos)
            
        else:
            st.info("📝 Registra tu primer activo para ver el dashboard")
    
    with tab3:
        if st.session_state.activos_fisicos:
            st.header("📋 Listado Completo de Activos")
            
            df_activos = pd.DataFrame(st.session_state.activos_fisicos)
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                tipos_seleccionados = st.multiselect("Filtrar por tipo", 
                    df_activos["Tipo"].unique(), default=df_activos["Tipo"].unique())
            with col2:
                roi_min = st.number_input("ROI mínimo (%)", value=0.0)
            with col3:
                ordenar_por = st.selectbox("Ordenar por", 
                    ["ROI Acumulado (%)", "Rentabilidad (%)", "Valor Actual", "Fecha Registro"])
            
            # Aplicar filtros
            df_filtrado = df_activos[
                (df_activos["Tipo"].isin(tipos_seleccionados)) & 
                (df_activos["ROI Acumulado (%)"] >= roi_min)
            ].sort_values(ordenar_por, ascending=False)
            
            # Mostrar tabla
            columnas_mostrar = ["Tipo", "Descripción", "Valor Actual", "Rentabilidad (%)", 
                              "ROI Acumulado (%)", "Periodo de Recuperación (años)", "Recomendación"]
            
            st.dataframe(
                df_filtrado[columnas_mostrar].style.format({
                    "Valor Actual": lambda x: formato_pesos(x),
                    "Rentabilidad (%)": "{:.1f}%",
                    "ROI Acumulado (%)": "{:.1f}%",
                    "Periodo de Recuperación (años)": lambda x: f"{x:.1f}" if x != "∞" else "∞"
                }),
                use_container_width=True,
                height=400
            )
            
            # Recomendaciones detalladas
            st.subheader("💡 Recomendaciones Detalladas")
            for _, activo in df_filtrado.iterrows():
                with st.expander(f"{activo['Descripción']} ({activo['Tipo']}) - ROI: {activo['ROI Acumulado (%)']}%"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Valor actual:** {formato_pesos(activo['Valor Actual'])}")
                        st.write(f"**Rentabilidad:** {activo['Rentabilidad (%)']}%")
                        st.write(f"**Período recuperación:** {activo['Periodo de Recuperación (años)']} años")
                    with col2:
                        if activo['Tipo'] == 'Cultivo' and activo.get('Tipo Cultivo'):
                            st.write(f"**Cultivo:** {activo['Tipo Cultivo']}")
                            if activo.get('pH Suelo'):
                                st.write(f"**pH Suelo:** {activo['pH Suelo']}")
                            if activo.get('Temperatura (°C)'):
                                st.write(f"**Temperatura:** {activo['Temperatura (°C)']}°C")
                    
                    st.markdown(f"**Recomendación:** {activo['Recomendación']}")
        else:
            st.info("📝 No hay activos registrados")
    
    with tab4:
        tab_ventas_ganaderas()
    
    with tab5:
        seccion_administracion_mejorada()

# Ejecutar la aplicación
if __name__ == "__main__":
    gestionar_inversiones_fisicas()