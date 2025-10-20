import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

# Define el nombre del archivo para guardar los gastos y presupuestos
GASTOS_PRESUPUESTOS_FILE = "gastos_presupuestos.json"

# Función para formatear valores monetarios en pesos colombianos (miles con punto, decimales con coma)
def formato_pesos(valor):
    # Formatea el numero con separador de miles como '.' y decimal como ','
    # Primero se formatea con coma para miles y punto para decimales (estilo anglosajon)
    # Luego se invierten los separadores para el formato colombiano
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def load_gastos_presupuestos():
    """
    Carga los gastos y presupuestos desde un archivo JSON.
    Retorna un diccionario con los datos o valores por defecto si el archivo no existe o está vacío.
    """
    if os.path.exists(GASTOS_PRESUPUESTOS_FILE):
        with open(GASTOS_PRESUPUESTOS_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Convertir la lista de diccionarios de gastos a DataFrame
                if 'gastos_df' in data and isinstance(data['gastos_df'], list):
                    df = pd.DataFrame(data['gastos_df'])
                    if not df.empty:
                        # Asegurarse de que la columna 'Fecha' se convierta a datetime
                        df['Fecha'] = pd.to_datetime(df['Fecha'])
                    data['gastos_df'] = df
                else:
                    data['gastos_df'] = pd.DataFrame(columns=['Fecha', 'Descripcion', 'Monto', 'Categoria'])
                
                if 'presupuestos' not in data:
                    data['presupuestos'] = {}

                return data
            except json.JSONDecodeError:
                # Si el archivo está vacío o mal formado, retornar valores por defecto
                return {
                    "gastos_df": pd.DataFrame(columns=['Fecha', 'Descripcion', 'Monto', 'Categoria']),
                    "presupuestos": {}
                }
    # Si el archivo no existe, retornar valores por defecto
    return {
        "gastos_df": pd.DataFrame(columns=['Fecha', 'Descripcion', 'Monto', 'Categoria']),
        "presupuestos": {}
    }

def save_gastos_presupuestos(data_dict):
    """
    Guarda los gastos y presupuestos en un archivo JSON.
    Convierte el DataFrame de gastos a formato de lista para JSON.
    """
    data_to_save = data_dict.copy()
    if isinstance(data_to_save['gastos_df'], pd.DataFrame):
        # Convertir la columna 'Fecha' a string antes de guardar para evitar TypeError
        temp_df = data_to_save['gastos_df'].copy()
        if 'Fecha' in temp_df.columns and not temp_df['Fecha'].empty:
            temp_df['Fecha'] = temp_df['Fecha'].dt.strftime('%Y-%m-%d')
        data_to_save['gastos_df'] = temp_df.to_dict(orient='records')
    
    with open(GASTOS_PRESUPUESTOS_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=4)


# Función para categorizar gastos (basada en reglas simples)
def categorizar_gasto(descripcion):
    desc = descripcion.lower()

    # INGRESOS
    if "tesoro naci" in desc or "interbanc dir" in desc or "nomina" in desc or "salario" in desc:
        return ("Ingreso", "Salario / Tesorería")
    if "transferencia desde nequi" in desc or "transf qr keyner" in desc or "pago de cliente" in desc or "honorarios" in desc:
        return ("Ingreso", "Transferencia / Honorarios")
    if "consignacion" in desc or "deposito" in desc:
        return ("Ingreso", "Consignación / Depósito")
    if "abono intereses" in desc or "rendimientos" in desc:
        return ("Financiero", "Intereses ganados")
    if "bono" in desc or "regalo" in desc:
        return ("Ingreso", "Bonos / Regalos")
    if "reembolso" in desc or "devolucion" in desc:
        return ("Ingreso", "Reembolso / Devolución")
    if "venta" in desc or "ingreso extra" in desc:
        return ("Ingreso", "Ventas / Ingresos Extra")

    # GASTOS
    if "transferencia a nequi" in desc or "transf qr nequi" in desc or "pago a proveedor" in desc:
        return ("Gasto", "Transferencia a terceros")
    if "retiro cajero" in desc or "retiro corresponsal" in desc or "efectivo" in desc:
        return ("Gasto", "Retiros en efectivo")
    if "pago suc virt tc" in desc or "mora tarjeta" in desc or "cuota tarjeta" in desc:
        return ("Gasto", "Pago de tarjeta de crédito")
    if "cuota manejo" in desc or "comision bancaria" in desc or "gmf" in desc:
        return ("Financiero", "Comisión bancaria")
    if "pago pse" in desc or "compra en" in desc or "pago qr" in desc or "adquisicion" in desc:
        if any(keyword in desc for keyword in ["supermercado", "alimentos", "mercado", "d1", "exito", "jumbo", "tiendas ar", "tienda d1", "exito maga", "fruver", "carniceria", "panaderia", "farmatodo", "la rebaja"]):
            return ("Gasto", "Alimentos y Compras")
        elif any(keyword in desc for keyword in ["restaurante", "cafe", "bar", "comida rapida", "crepes de la villa", "pollos crock", "cali pollos", "pizzeria", "sushi", "domicilios", "rappipay"]):
            return ("Gasto", "Comida Fuera")
        elif any(keyword in desc for keyword in ["ropa", "zapatos", "moda", "boutique", "tienda de ropa", "falabella", "arturo calle"]):
            return ("Gasto", "Vestimenta")
        elif any(keyword in desc for keyword in ["cine", "concierto", "teatro", "ocio", "entretenimiento", "viaje", "bold*event", "parque", "museo", "vacaciones", "hotel", "tiquetes", "netflix", "spotify", "disney+"]):
            return ("Gasto", "Ocio y Entretenimiento")
        elif any(keyword in desc for keyword in ["salud", "medico", "farmacia", "hospital", "seguro medico", "odontologo", "terapia", "medicamentos", "drogueria", "eps"]):
            return ("Gasto", "Salud")
        elif any(keyword in desc for keyword in ["educacion", "curso", "universidad", "libros", "matricula", "diplomado", "taller", "colegio", "academia"]):
            return ("Gasto", "Educación")
        elif any(keyword in desc for keyword in ["gimnasio", "deporte", "entrenamiento", "suplementos", "sportlife", "smartfit"]):
            return ("Gasto", "Deporte y Bienestar")
        elif any(keyword in desc for keyword in ["mascota", "veterinaria", "alimento mascotas", "petshop"]):
            return ("Gasto", "Mascotas")
        elif any(keyword in desc for keyword in ["electronicos", "tecnologia", "celular", "computador", "gadget", "alkosto", "falabella tecnologia"]):
            return ("Gasto", "Tecnología")
        elif any(keyword in desc for keyword in ["muebles", "hogar", "decoracion", "electrodomesticos", "reparacion hogar", "ferreteria", "homecenter", "construccion"]):
            return ("Gasto", "Hogar y Mantenimiento")
        else:
            return ("Gasto", "Compras y Pagos Varios")
    
    if "transf a comunicacion" in desc or "pago celular" in desc or "recarga" in desc or "claro" in desc or "tigo" in desc or "movistar":
        return ("Gasto", "Comunicación")
    if any(keyword in desc for keyword in ["arriendo", "hipoteca", "servicios", "luz", "agua", "gas", "internet", "administracion", "impuestos predial", "alquiler"]):
        return ("Gasto", "Vivienda y Servicios")
    if any(keyword in desc for keyword in ["transporte", "gasolina", "bus", "taxi", "uber", "metro", "peajes", "mantenimiento vehiculo", "parqueadero", "transmilenio"]):
        return ("Gasto", "Transporte")
    if any(keyword in desc for keyword in ["seguros", "poliza", "seguro vida", "seguro auto", "seguro hogar"]):
        return ("Gasto", "Seguros")
    if any(keyword in desc for keyword in ["impuestos", "dian", "renta", "iva"]):
        return ("Gasto", "Impuestos")
    if any(keyword in desc for keyword in ["donacion", "caridad", "fundacion"]):
        return ("Gasto", "Donaciones")
    if any(keyword in desc for keyword in ["belleza", "peluqueria", "estetica", "spa", "cosmeticos"]):
        return ("Gasto", "Cuidado Personal")
    if any(keyword in desc for keyword in ["regalo", "celebracion", "fiesta", "evento"]):
        return ("Gasto", "Regalos y Celebraciones")

    # INVERSIÓN
    if "apertura inv" in desc or "compra acciones" in desc or "fondo de inversion" in desc or "cdt" in desc or "bolsa" in desc or "broker":
        return ("Inversión", "Inversión en Mercados")
    if "pago pse lulo bank" in desc or "nu colombia" in desc or "daviplata" in desc or "banco digital" in desc or "tyba" in desc or "afin" in desc:
        return ("Inversión", "Neobancos / Plataformas Digitales")
    if "compra cripto" in desc or "binance" in desc or "exchange cripto" in desc or "coinbase" in desc:
        return ("Inversión", "Criptomonedas")

    # TRANSFERENCIAS INTERNAS (entre cuentas propias, no son gasto ni ingreso real)
    if "cta suc virtual" in desc or "suc virtual" in desc or "keyner andres" in desc or "transferencia entre cuentas" in desc or "mis cuentas":
        return ("Transferencia Interna", "Entre cuentas propias")

    # OTROS
    return ("Otros", "Sin clasificar")

# --- Función principal del módulo ---
def mostrar_gestion_gastos():
    st.header("💸 Gestión de Presupuesto y Gastos")

    st.markdown("""
    Aquí puedes registrar tus gastos para tener un control detallado de tus finanzas personales.
    Puedes subir un archivo CSV con tus transacciones o añadir gastos manualmente.

    **Formato CSV esperado:** `Fecha,Descripcion,Monto`
    """)

    # Cargar los gastos y presupuestos al inicio de la sesión
    if 'gastos_df' not in st.session_state or 'presupuestos' not in st.session_state:
        loaded_data = load_gastos_presupuestos()
        st.session_state.gastos_df = loaded_data['gastos_df']
        st.session_state.presupuestos = loaded_data['presupuestos']

    # --- Cargar gastos desde CSV ---
    st.subheader("📥 Cargar Gastos desde CSV")
    uploaded_file = st.file_uploader("Sube tu archivo CSV de transacciones", type=["csv"])

    if uploaded_file is not None:
        with st.spinner("Cargando y categorizando gastos desde CSV..."): # Spinner para carga CSV
            try:
                df_csv = pd.read_csv(uploaded_file)
                # Validar columnas
                if not all(col in df_csv.columns for col in ['Fecha', 'Descripcion', 'Monto']):
                    st.error("El archivo CSV debe contener las columnas 'Fecha', 'Descripcion' y 'Monto'.")
                    return

                # Limpiar y convertir tipos
                df_csv['Fecha'] = pd.to_datetime(df_csv['Fecha'], errors='coerce')
                df_csv['Monto'] = pd.to_numeric(df_csv['Monto'], errors='coerce')
                df_csv = df_csv.dropna(subset=['Fecha', 'Monto']) # Eliminar filas con valores nulos después de la conversión

                # Categorizar los gastos del CSV y almacenar como "Categoría - Subcategoría"
                df_csv['Categoria'] = df_csv['Descripcion'].apply(lambda x: f"{categorizar_gasto(x)[0]} - {categorizar_gasto(x)[1]}")

                # Concatenar con los gastos existentes
                st.session_state.gastos_df = pd.concat([st.session_state.gastos_df, df_csv], ignore_index=True)
                st.session_state.gastos_df = st.session_state.gastos_df.drop_duplicates(subset=['Fecha', 'Descripcion', 'Monto']) # Evitar duplicados
                
                # Guardar los datos actualizados
                save_gastos_presupuestos({
                    "gastos_df": st.session_state.gastos_df,
                    "presupuestos": st.session_state.presupuestos
                })
                st.success("Gastos cargados y categorizados correctamente desde CSV.")
                st.rerun() # Recargar para mostrar los datos actualizados
            except Exception as e:
                st.error(f"Error al leer el archivo CSV: {e}")

    # --- Añadir gasto manualmente ---
    st.subheader("➕ Añadir Transacción Manualmente") # Changed title
    with st.form("form_gasto_manual"):
        fecha_gasto = st.date_input("Fecha de la transacción", datetime.now()) # Changed label
        descripcion_gasto = st.text_input("Descripción de la transacción") # Changed label
        monto_gasto = st.number_input("Monto (COP)", min_value=0.0, step=1000.0, format="%.2f")
        
        # Nuevo: Selector de tipo de transacción (Gasto o Ingreso)
        tipo_transaccion = st.radio("Tipo de Transacción", ["Gasto", "Ingreso"], key="tipo_transaccion_radio")

        # Permitir al usuario seleccionar la categoría si lo desea
        # Generar una lista de categorías únicas y subcategorías combinadas para el selectbox
        categorias_existentes = []
        if not st.session_state.gastos_df.empty:
            categorias_existentes = sorted(list(st.session_state.gastos_df['Categoria'].unique()))

        categoria_principal_sugerida, subcategoria_sugerida = categorizar_gasto(descripcion_gasto)
        categoria_sugerida_completa = f"{categoria_principal_sugerida} - {subcategoria_sugerida}"
        
        # Asegurarse de que la categoría sugerida esté en la lista de opciones
        if categoria_sugerida_completa not in categorias_existentes:
            categorias_existentes.insert(0, categoria_sugerida_completa) # Poner la sugerida al principio
        
        selected_categoria = st.selectbox(
            "Categoría (automática o selecciona)",
            options=categorias_existentes,
            index=categorias_existentes.index(categoria_sugerida_completa) if categoria_sugerida_completa in categorias_existentes else 0,
            key="manual_categoria_select"
        )

        submit_button = st.form_submit_button("Añadir Transacción") # Changed label

    if submit_button and descripcion_gasto and monto_gasto > 0:
        with st.spinner("Añadiendo y categorizando transacción..."): # Changed label
            try:
                # Determinar el monto final basado en el tipo de transacción seleccionado
                if tipo_transaccion == "Gasto":
                    final_monto = -monto_gasto
                else: # Es un Ingreso
                    final_monto = monto_gasto
                
                nuevo_gasto = pd.DataFrame([{
                    'Fecha': pd.to_datetime(fecha_gasto),
                    'Descripcion': descripcion_gasto,
                    'Monto': final_monto,
                    'Categoria': selected_categoria # Guardar la categoría completa
                }])
                st.session_state.gastos_df = pd.concat([st.session_state.gastos_df, nuevo_gasto], ignore_index=True)
                st.session_state.gastos_df = st.session_state.gastos_df.drop_duplicates(subset=['Fecha', 'Descripcion', 'Monto'])
                
                # Guardar los datos actualizados
                save_gastos_presupuestos({
                    "gastos_df": st.session_state.gastos_df,
                    "presupuestos": st.session_state.presupuestos
                })
                st.success("✅ Transacción añadida y categorizada correctamente.") # Changed label
                st.rerun() # Recargar para mostrar los datos actualizados
            except Exception as e:
                st.error(f"Error al añadir transacción: {e}") # Changed label

    # --- Mostrar y Analizar Gastos ---
    if not st.session_state.gastos_df.empty:
        df_gastos = st.session_state.gastos_df.copy()
        df_gastos['Mes'] = df_gastos['Fecha'].dt.to_period('M') # Columna para agrupar por mes

        st.subheader("📋 Resumen de Transacciones") # Changed title
        # Ordenar por fecha para mejor visualización
        df_gastos_display = df_gastos.sort_values(by='Fecha', ascending=False).copy()
        df_gastos_display['Monto'] = df_gastos_display['Monto'].apply(formato_pesos)
        df_gastos_display['Fecha'] = df_gastos_display['Fecha'].dt.strftime('%Y-%m-%d') # Formato de fecha para display
        st.dataframe(df_gastos_display[['Fecha', 'Descripcion', 'Monto', 'Categoria']], use_container_width=True)

        st.subheader("📊 Resumen Mensual de Flujos")
        # Filtrar por mes actual para el resumen
        mes_actual = pd.Period(datetime.now().strftime('%Y-%m'), freq='M')
        df_mes_actual = df_gastos[df_gastos['Mes'] == mes_actual]

        total_ingresos_mes = df_mes_actual[df_mes_actual['Monto'] > 0]['Monto'].sum()
        total_gastos_mes = df_mes_actual[df_mes_actual['Monto'] < 0]['Monto'].abs().sum()
        balance_mes = total_ingresos_mes - total_gastos_mes

        col_inc, col_exp, col_bal = st.columns(3)
        with col_inc:
            st.metric("Total Ingresos (Mes Actual)", formato_pesos(total_ingresos_mes))
        with col_exp:
            st.metric("Total Gastos (Mes Actual)", formato_pesos(total_gastos_mes))
        with col_bal:
            st.metric("Balance Neto (Mes Actual)", formato_pesos(balance_mes))

        st.markdown("---") # Visual separator

        st.subheader("📊 Hábitos de Gasto e Ingreso") # Updated title for section

        # Gasto por categoría (Pie Chart)
        # Agrupar por la categoría completa (principal - subcategoría)
        df_solo_gastos = df_gastos[
            df_gastos['Categoria'].apply(lambda x: x.split(' - ')[0] in ["Gasto", "Financiero", "Retiros en efectivo", "Comisión bancaria", "Otros"])
        ].copy()
        df_solo_gastos['Monto_Abs'] = df_solo_gastos['Monto'].abs() 

        gastos_por_categoria = df_solo_gastos.groupby('Categoria')['Monto_Abs'].sum().sort_values(ascending=False)
        if not gastos_por_categoria.empty and gastos_por_categoria.sum() > 0: # Añadir check para evitar pie chart con suma 0
            fig1, ax1 = plt.subplots(figsize=(8, 8))
            ax1.pie(gastos_por_categoria, labels=gastos_por_categoria.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
            ax1.axis('equal')
            ax1.set_title('Distribución de Gastos por Categoría')
            st.pyplot(fig1)
            plt.close(fig1) # Cierra la figura para liberar memoria
        else:
            st.info("No hay gastos válidos para mostrar la distribución por categoría.")

        # Gasto mensual (Bar Chart)
        gastos_mensuales = df_solo_gastos.groupby('Mes')['Monto_Abs'].sum().sort_index()
        if not gastos_mensuales.empty and gastos_mensuales.sum() > 0: # Añadir check para evitar bar chart con suma 0
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            bars = ax2.bar(gastos_mensuales.index.astype(str), gastos_mensuales.values, color='lightcoral')
            ax2.set_title('Gastos Totales por Mes')
            ax2.set_xlabel('Mes')
            ax2.set_ylabel('Monto (COP)')
            ax2.ticklabel_format(style='plain', axis='y')
            ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: formato_pesos(x)))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Añadir valores en COP sobre cada barra
            for bar in bars:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval + (yval * 0.01), formato_pesos(yval), ha='center', va='bottom', fontsize=9) # Ajuste para que el texto no se superponga
            
            st.pyplot(fig2)
            plt.close(fig2) # Cierra la figura para liberar memoria
        else:
            st.info("No hay gastos válidos para mostrar el total mensual.")
        
        # NUEVO: Gráfico de Ingresos Mensuales (Bar Chart)
        # Se asegura que las condiciones booleanas se combinen correctamente con '&' y paréntesis
        df_solo_ingresos = df_gastos[
            (df_gastos['Categoria'].apply(lambda x: x.split(' - ')[0] in ["Ingreso", "Financiero"])) & (df_gastos['Monto'] > 0)
        ].copy()
        
        ingresos_mensuales = df_solo_ingresos.groupby('Mes')['Monto'].sum().sort_index()
        if not ingresos_mensuales.empty and ingresos_mensuales.sum() > 0:
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            bars = ax3.bar(ingresos_mensuales.index.astype(str), ingresos_mensuales.values, color='lightgreen')
            ax3.set_title('Ingresos Totales por Mes')
            ax3.set_xlabel('Mes')
            ax3.set_ylabel('Monto (COP)')
            ax3.ticklabel_format(style='plain', axis='y')
            ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: formato_pesos(x)))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Añadir valores en COP sobre cada barra
            for bar in bars:
                yval = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2, yval + (yval * 0.01), formato_pesos(yval), ha='center', va='bottom', fontsize=9) # Ajuste para que el texto no se superponga
            
            st.pyplot(fig3)
            plt.close(fig3)
        else:
            st.info("No hay ingresos válidos para mostrar el total mensual.")


        # --- Presupuesto y Alertas ---
        st.subheader("💰 Presupuesto por Categoría y Alertas")

        # Usar solo las categorías que son consideradas "gastos" para el presupuesto
        # Se extrae la categoría principal de las categorías ya combinadas
        categorias_para_presupuesto_set = set()
        for cat_completa in df_gastos['Categoria'].unique():
            cat_principal = cat_completa.split(' - ')[0]
            if cat_principal in ["Gasto", "Financiero", "Retiros en efectivo", "Comisión bancaria", "Otros"]: # "Otros" también puede ser un gasto
                categorias_para_presupuesto_set.add(cat_completa)
        
        categorias_para_presupuesto = sorted(list(categorias_para_presupuesto_set))
        alertas_activas = False

        st.markdown("Establece tu presupuesto mensual para cada categoría:")
        if not categorias_para_presupuesto:
            st.info("No hay categorías de gastos para establecer un presupuesto. Añade gastos para ver las opciones.")
        else:
            for categoria in categorias_para_presupuesto:
                # Usar un key único para cada number_input
                current_budget = st.session_state.presupuestos.get(categoria, 0.0)
                st.session_state.presupuestos[categoria] = st.number_input(
                    f"Presupuesto para {categoria} (COP)",
                    min_value=0.0,
                    value=current_budget,
                    step=10000.0,
                    format="%.2f",
                    key=f"budget_{categoria}"
                )
            
            # Botón para guardar presupuestos manualmente
            if st.button("Guardar Presupuestos"):
                save_gastos_presupuestos({
                    "gastos_df": st.session_state.gastos_df,
                    "presupuestos": st.session_state.presupuestos
                })
                st.success("Presupuestos guardados correctamente.")
                st.rerun()

            # Calcular gastos actuales por categoría para el mes actual (solo gastos)
            mes_actual = pd.Period(datetime.now().strftime('%Y-%m'), freq='M')
            gastos_mes_actual_filtrados = df_solo_gastos[df_solo_gastos['Mes'] == mes_actual].groupby('Categoria')['Monto_Abs'].sum()

            st.markdown("---")
            st.markdown("### 🔔 Alertas de Presupuesto (Mes Actual)")
            if gastos_mes_actual_filtrados.empty:
                st.info("No hay gastos registrados para el mes actual.")
            else:
                for categoria in categorias_para_presupuesto:
                    gasto_actual = gastos_mes_actual_filtrados.get(categoria, 0.0)
                    presupuesto = st.session_state.presupuestos.get(categoria, 0.0)

                    if presupuesto > 0:
                        if gasto_actual > presupuesto:
                            st.error(f"🚨 ¡Alerta! Has excedido tu presupuesto para **{categoria}**.\n"
                                     f"Gasto actual: {formato_pesos(gasto_actual)} / Presupuesto: {formato_pesos(presupuesto)}")
                            alertas_activas = True
                        elif gasto_actual > presupuesto * 0.8:
                            st.warning(f"⚠️ Estás cerca de exceder tu presupuesto para **{categoria}**.\n"
                                       f"Gasto actual: {formato_pesos(gasto_actual)} / Presupuesto: {formato_pesos(presupuesto)}")
                            alertas_activas = True
                        else:
                            remaining_budget = presupuesto - gasto_actual
                            st.info(f"✅ Vas bien en **{categoria}**.\n"
                                     f"Gasto actual: {formato_pesos(gasto_actual)} / Presupuesto: {formato_pesos(presupuesto)} / Restante: {formato_pesos(remaining_budget)}")
                    elif gasto_actual > 0: # Si no hay presupuesto pero hay gastos
                        st.info(f"Gasto en **{categoria}**: {formato_pesos(gasto_actual)} (sin presupuesto establecido).")
                
                if not alertas_activas:
                    st.success("¡Excelente! No hay alertas de presupuesto activas para el mes actual.")

    else:
        st.info("Aún no se han registrado gastos. ¡Empieza a añadir tus transacciones!")
