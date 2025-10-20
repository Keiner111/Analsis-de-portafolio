import streamlit as st
import pandas as pd

# Funcion para formatear valores monetarios en pesos colombianos
def formato_pesos(valor):
    # Formatea el numero con separador de miles como '.' y decimal como ','
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def chat_ia(df):
    st.header("🤖 Chat Financiero Simulado")

    st.markdown("""
    ¡Hola! Soy tu asistente financiero. Puedes hacerme preguntas sobre tu portafolio cargado.
    Por ejemplo:
    - ¿Cual es mi inversion mas rentable?
    - ¿Cuanto ingreso pasivo estoy generando?
    - ¿Que tipo de inversiones tengo?
    - ¿Cual es mi rentabilidad promedio?
    - ¿Cual es mi capital total?
    - ¿Cuanto dinero tengo en activos fisicos?
    - ¿Cuanto tengo invertido en bienes raices?
    - ¿Cual es el total de mis inversiones en criptomonedas?
    - ¿Que debo hacer si quiero alcanzar mi meta financiera en X tiempo?
    - ¿Como se calcula la devaluacion?
    """)

    # Inicializar el historial de mensajes en st.session_state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores del historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de usuario
    pregunta = st.chat_input("Escribe tu pregunta aqui:")

    if pregunta:
        # Añadir la pregunta del usuario al historial
        st.session_state.messages.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)

        with st.chat_message("assistant"):
            # Lógica de respuesta basada en palabras clave
            respuesta = ""
            if df is None or df.empty:
                respuesta = "Por favor, carga tu portafolio primero para que pueda analizar tus datos."
            else:
                try:
                    df_cleaned = df.copy()
                    df_cleaned['Dinero'] = pd.to_numeric(df_cleaned['Dinero'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
                    df_cleaned['Interes Mensual'] = pd.to_numeric(df_cleaned['Interes Mensual'], errors='coerce').fillna(0)

                    pregunta_lower = pregunta.lower()

                    if "inversion mas rentable" in pregunta_lower:
                        if not df_cleaned.empty and 'Interes Mensual' in df_cleaned.columns:
                            top_inversion = df_cleaned.sort_values(by='Interes Mensual', ascending=False).iloc[0]
                            respuesta = f"Tu inversion mas rentable es '{top_inversion['Items']}' con {formato_pesos(top_inversion['Interes Mensual'])} COP de ingreso mensual."
                        else:
                            respuesta = "No puedo determinar la inversion mas rentable sin datos de 'Interes Mensual' o si el portafolio esta vacio."
                    elif "ingreso pasivo" in pregunta_lower:
                        total_ingreso_pasivo = df_cleaned['Interes Mensual'].sum()
                        respuesta = f"Tu ingreso pasivo mensual total es de {formato_pesos(total_ingreso_pasivo)} COP."
                    elif "que tipo de inversiones tengo" in pregunta_lower or "tipos de inversion" in pregunta_lower:
                        if 'Tipo de inversion' in df_cleaned.columns:
                            tipos = df_cleaned['Tipo de inversion'].unique()
                            respuesta = f"Tienes inversiones de los siguientes tipos: {', '.join(tipos)}."
                        else:
                            respuesta = "No se encontraron datos de 'Tipo de inversion' en tu portafolio."
                    elif "rentabilidad promedio" in pregunta_lower:
                        total_capital = df_cleaned['Dinero'].sum()
                        total_ingreso_pasivo = df_cleaned['Interes Mensual'].sum()
                        if total_capital > 0:
                            rentabilidad_promedio_mensual = (total_ingreso_pasivo / total_capital) * 100
                            respuesta = f"La rentabilidad mensual promedio de tu portafolio es del {rentabilidad_promedio_mensual:.2f}%."
                        else:
                            respuesta = "No puedo calcular la rentabilidad promedio sin un capital total."
                    elif "capital total" in pregunta_lower:
                        total_capital = df_cleaned['Dinero'].sum()
                        respuesta = f"Tu capital total actual es de {formato_pesos(total_capital)} COP."
                    elif "dinero en activos fisicos" in pregunta_lower or "activos fisicos" in pregunta_lower:
                        activos_fisicos_df = df_cleaned[df_cleaned['Tipo de inversion'].isin(['Animal- semoviente', 'Activo Fisico'])]
                        total_activos_fisicos = activos_fisicos_df['Dinero'].sum()
                        if total_activos_fisicos > 0:
                            detalle = ", ".join([f"{row['Items']} ({formato_pesos(row['Dinero'])})" for _, row in activos_fisicos_df.iterrows()])
                            respuesta = f"Tienes {formato_pesos(total_activos_fisicos)} COP en activos fisicos. Detalles: {detalle}."
                        else:
                            respuesta = "No se identificaron activos fisicos especificos en tu portafolio cargado."
                    elif "bienes raices" in pregunta_lower:
                        bienes_raices_df = df_cleaned[df_cleaned['Tipo de inversion'] == 'Bienes Raices']
                        total_bienes_raices = bienes_raices_df['Dinero'].sum()
                        if total_bienes_raices > 0:
                            detalle = ", ".join([f"{row['Items']} ({formato_pesos(row['Dinero'])})" for _, row in bienes_raices_df.iterrows()])
                            respuesta = f"Tienes {formato_pesos(total_bienes_raices)} COP invertidos en bienes raices. Detalles: {detalle}."
                        else:
                            respuesta = "No se encontraron inversiones en bienes raices en tu portafolio."
                    elif "criptomonedas" in pregunta_lower or "cripto" in pregunta_lower:
                        cripto_df = df_cleaned[df_cleaned['Tipo de inversion'] == 'Criptomoneda']
                        total_cripto = cripto_df['Dinero'].sum()
                        if total_cripto > 0:
                            detalle = ", ".join([f"{row['Items']} ({formato_pesos(row['Dinero'])})" for _, row in cripto_df.iterrows()])
                            respuesta = f"Tienes {formato_pesos(total_cripto)} COP invertidos en criptomonedas. Detalles: {detalle}."
                        else:
                            respuesta = "No se encontraron inversiones en criptomonedas en tu portafolio."
                    elif "aumento el capital" in pregunta_lower:
                        respuesta = "Aumentar el capital incrementara tu ingreso pasivo proporcionalmente si se mantiene la rentabilidad. Puedes usar la seccion 'Proyecciones' para simular esto."
                    elif "meta financiera" in pregunta_lower or "meta fire" in pregunta_lower or "camino a tu meta" in pregunta_lower:
                        respuesta = "Para analizar tu meta financiera o FIRE, por favor, usa las secciones 'Camino a tu meta' o 'Calculadora FIRE' en el menu lateral."
                    elif "devaluacion" in pregunta_lower:
                        respuesta = "La devaluacion es la perdida de valor de una moneda frente a otras. Puedes analizar su impacto en la seccion 'Devaluacion e Inflacion'."
                    else:
                        respuesta = "Lo siento, aun no puedo responder esa pregunta. Intenta con otra formulacion o visita la seccion correspondiente en el menu lateral."

                except Exception as e:
                    respuesta = f"🚨 Ocurrio un error al procesar tu pregunta: {e}. Por favor, verifica el formato de tus datos."

            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
    elif df is None:
        st.warning("Por favor, carga tu portafolio primero para usar el chat financiero.")