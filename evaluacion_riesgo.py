import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os # Importar el módulo os para verificar la existencia del archivo

# Define el nombre del archivo para guardar los niveles de riesgo
RISK_LEVELS_FILE = "user_risk_levels.json"

# Function to format currency in Colombian Pesos
def formato_pesos(valor):
    """
    Formatea un valor numérico como Pesos Colombianos.
    Ejemplo: 1234567.89 -> $ 1.234.567
    """
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def load_user_risk_levels():
    """
    Carga los niveles de riesgo definidos por el usuario desde un archivo JSON.
    Retorna un diccionario vacío si el file no existe o está vacío.
    """
    if os.path.exists(RISK_LEVELS_FILE):
        with open(RISK_LEVELS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Manejar archivo JSON vacío o mal formado
                return {}
    return {}

def save_user_risk_levels(risk_levels_dict):
    """
    Guarda los niveles de riesgo definidos por el usuario en un archivo JSON.
    """
    with open(RISK_LEVELS_FILE, 'w') as f:
        json.dump(risk_levels_dict, f, indent=4)

def mostrar_evaluacion_riesgo(df):
    """
    Muestra el módulo de Evaluación de Riesgo del Portafolio y Perfil de Inversor.
    Incluye un cuestionario, análisis de sensibilidad, y análisis de diversificación.
    """
    st.header("🛡️ Evaluación de Riesgo y Perfil de Inversor")

    # --- INICIALIZACIÓN ROBUSTA DE st.session_state.user_risk_levels ---
    # Asegura que user_risk_levels siempre exista en session_state cuando esta función se ejecuta
    if 'user_risk_levels' not in st.session_state:
        st.session_state.user_risk_levels = load_user_risk_levels()
    # -------------------------------------------------------------------

    # --- 1. Cuestionario Interactivo de Perfil de Riesgo ---
    st.subheader("📝 Cuestionario de Perfil de Riesgo")
    st.markdown("""
    Responde las siguientes preguntas para determinar tu perfil de inversor.
    Tu perfil de riesgo es crucial para alinear tus inversiones con tus objetivos y tolerancia a la volatilidad.
    """)

    # Questions and scores
    questions = [
        {
            "question": "¿Cuál es tu principal objetivo al invertir?",
            "options": {
                "Preservar mi capital y obtener rendimientos modestos.": 1,
                "Crecer mi capital a largo plazo, aceptando cierta volatilidad.": 2,
                "Maximizar el crecimiento, asumiendo riesgos significativos.": 3
            },
            "key": "q1"
        },
        {
            "question": "¿Qué harías si tus inversiones cayeran un 20% en un mes?",
            "options": {
                "Vendería todo para evitar mayores pérdidas.": 1,
                "Mantendría mis inversiones y esperaría una recuperación.": 2,
                "Consideraría invertir más para aprovechar los precios bajos.": 3
            },
            "key": "q3"
        },
        {
            "question": "¿Cuál es tu horizonte de inversión?",
            "options": {
                "Menos de 1 año.": 1,
                "De 1 a 5 años.": 2,
                "Más de 5 años.": 3
            },
            "key": "q4"
        },
        {
            "question": "¿Qué nivel de conocimiento tienes sobre productos de inversión?",
            "options": {
                "Básico (solo conozco lo fundamental).": 1,
                "Intermedio (entiendo varios tipos de activos y riesgos).": 2,
                "Avanzado (conozco estrategias complejas y mercados).": 3
            },
            "key": "q5"
        },
        {
            "question": "¿Cómo reaccionarías si una de tus inversiones más grandes perdiera la mitad de su valor?",
            "options": {
                "Entraría en pánico y la vendería inmediatamente.": 1,
                "Me preocuparía, pero mantendría la calma y analizaría la situación.": 2,
                "Lo vería como una oportunidad para comprar más a un precio reducido.": 3
            },
            "key": "q6"
        }
    ]

    total_score = 0
    answers = {}
    risk_profile = "" # Initialize risk_profile here

    with st.form("risk_profile_form"):
        for q_data in questions:
            selected_option = st.radio(q_data["question"], list(q_data["options"].keys()), key=q_data["key"])
            answers[q_data["key"]] = selected_option
            
        submitted = st.form_submit_button("Determinar Perfil de Riesgo")

    if submitted:
        for q_data in questions:
            total_score += q_data["options"][answers[q_data["key"]]]

        if total_score <= 7:
            risk_profile = "Conservador 🐢"
            st.info(f"Tu puntuación total es **{total_score}**. Tu perfil de inversor es **{risk_profile}**.")
            st.markdown("""
            Como inversor **Conservador**, tu prioridad es la seguridad y la preservación del capital.
            Prefieres inversiones de bajo riesgo con retornos estables, aunque sean modestos.
            Tu portafolio ideal podría incluir bonos, CDTs, fondos de renta fija y activos de bajo riesgo.
            """)
        elif 8 <= total_score <= 11:
            risk_profile = "Moderado ⚖️"
            st.warning(f"Tu puntuación total es **{total_score}**. Tu perfil de inversor es **{risk_profile}**.")
            st.markdown("""
            Como inversor **Moderado**, buscas un equilibrio entre la seguridad y el crecimiento.
            Estás dispuesto a asumir un riesgo moderado para obtener retornos superiores a los de las inversiones conservadoras.
            Tu portafolio podría combinar renta fija con una porción de renta variable (acciones, fondos mixtos).
            """)
        else: # total_score >= 12
            risk_profile = "Agresivo 🚀"
            st.error(f"Tu puntuación total es **{total_score}**. Tu perfil de inversor es **{risk_profile}**.")
            st.markdown("""
            Como inversor **Agresivo**, tu objetivo principal es maximizar el crecimiento de tu capital,
            y estás dispuesto a asumir riesgos significativos y tolerar fluctuaciones de mercado.
            Tu portafolio podría tener una alta exposición a renta variable, criptomonedas y otras inversiones de alto potencial.
            """)
    else:
        st.info("Responde el cuestionario para conocer tu perfil de riesgo.")

    st.markdown("---")

    # --- NUEVA SECCIÓN: Recomendación de Asignación Ideal ---
    if submitted: # Only show recommendations after the profile is determined
        st.subheader("🎯 Recomendación de Asignación Ideal de Portafolio")
        st.markdown(f"""
        Basado en tu perfil **{risk_profile.split(' ')[0]}**, aquí tienes una sugerencia de cómo podrías
        distribuir tu capital entre diferentes clases de activos para alinear tu portafolio con tu tolerancia al riesgo.
        """)

        # Define ideal allocations based on risk profile
        ideal_allocations = {
            "Conservador": {
                "Renta Fija": 65,
                "Renta Variable": 15,
                "Activos Reales/Alternativos": 10,
                "Efectivo/Liquidez": 10
            },
            "Moderado": {
                "Renta Fija": 35,
                "Renta Variable": 45,
                "Activos Reales/Alternativos": 15,
                "Efectivo/Liquidez": 5
            },
            "Agresivo": {
                "Renta Fija": 5,
                "Renta Variable": 65,
                "Activos Reales/Alternativos": 25,
                "Efectivo/Liquidez": 5
            }
        }

        # Get the allocation for the determined risk profile
        # Use .split(' ')[0] to get "Conservador", "Moderado", or "Agresivo" without the emoji
        profile_key = risk_profile.split(' ')[0] 
        allocation_data = ideal_allocations.get(profile_key, {})

        if allocation_data:
            df_allocation = pd.DataFrame(allocation_data.items(), columns=['Clase de Activo', 'Porcentaje (%)'])
            
            st.dataframe(df_allocation.style.format({"Porcentaje (%)": "{:.0f}%"}))

            # Plotting ideal allocation
            fig_alloc, ax_alloc = plt.subplots(figsize=(10, 6))
            bars_alloc = ax_alloc.bar(df_allocation["Clase de Activo"], df_allocation["Porcentaje (%)"], color=['#4CAF50', '#FFC107', '#2196F3', '#9E9E9E'])
            ax_alloc.set_title(f'Asignación Ideal para Perfil {profile_key}')
            ax_alloc.set_ylabel('Porcentaje (%)')
            ax_alloc.set_ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            for bar in bars_alloc:
                yval = bar.get_height()
                ax_alloc.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.0f}%', ha='center', va='bottom')

            st.pyplot(fig_alloc)
            plt.close(fig_alloc)

            st.markdown("""
            **Clases de Activos:**
            * **Renta Fija:** Bonos, CDTs, fondos de inversión de bajo riesgo.
            * **Renta Variable:** Acciones, fondos de inversión de acciones, ETFs.
            * **Activos Reales/Alternativos:** Bienes raíces, materias primas, inversiones en negocios privados.
            * **Efectivo/Liquidez:** Cuentas de ahorro, fondos del mercado monetario.
            """)
        else:
            st.info("No se encontró una recomendación de asignación para tu perfil de riesgo.")
    
    st.markdown("---")

    # --- Pre-requisite check for portfolio data ---
    if df is None:
        st.warning("Por favor, carga tu portafolio en la sección '📥 Cargar Portafolio' para realizar los análisis de sensibilidad y ponderación de riesgo.")
        return

    # Clean and convert 'Dinero' column to numeric
    df_cleaned = df.copy()
    df_cleaned['Dinero'] = pd.to_numeric(df_cleaned['Dinero'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
    capital_total = df_cleaned['Dinero'].sum()

    if capital_total == 0:
        st.info("Tu capital total es cero. Por favor, asegúrate de que tu portafolio tenga inversiones para los análisis.")
        return

    st.metric("Capital Total Actual", formato_pesos(capital_total))
    st.markdown("---")

    # --- 2. Análisis de Sensibilidad del Portafolio ---
    st.subheader("📈 Análisis de Sensibilidad del Portafolio")
    st.markdown("""
    Este análisis te muestra cómo podría comportarse tu capital total en diferentes escenarios económicos.
    """)

    # Define scenarios with percentage changes for the total capital
    scenarios = {
        "Optimista (Crecimiento fuerte)": 0.15,  # 15% growth
        "Moderado (Crecimiento estable)": 0.05,  # 5% growth
        "Pesimista (Caída del mercado)": -0.10,  # 10% drop
        "Recesión (Caída severa)": -0.25    # 25% drop
    }

    scenario_data = []
    for scenario_name, change_factor in scenarios.items():
        projected_value = capital_total * (1 + change_factor)
        scenario_data.append({
            "Escenario": scenario_name,
            "Cambio (%)": change_factor * 100,
            "Valor Proyectado": projected_value
        })

    df_scenarios = pd.DataFrame(scenario_data)
    
    st.dataframe(df_scenarios.style.format({
        "Cambio (%)": "{:.2f}%",
        "Valor Proyectado": lambda x: formato_pesos(x)
    }))

    # Plotting sensitivity analysis
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df_scenarios["Escenario"], df_scenarios["Valor Proyectado"], 
                  color=['green' if x >= capital_total else 'red' for x in df_scenarios["Valor Proyectado"]])
    
    ax.axhline(y=capital_total, color='blue', linestyle='--', label='Capital Actual')
    
    ax.set_title("Proyección del Capital en Diferentes Escenarios Económicos")
    ax.set_ylabel("Valor Proyectado (COP)")
    ax.set_xlabel("Escenario")
    ax.ticklabel_format(style='plain', axis='y')
    ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: formato_pesos(x)))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    # --- 3. Ponderación de Riesgo del Portafolio ---
    st.subheader("⚖️ Ponderación de Riesgo del Portafolio")
    st.markdown("""
    Esta sección evalúa el riesgo de tu portafolio basándose en la distribución de tu capital
    entre diferentes tipos de inversión y su nivel de riesgo inherente.
    """)

    if 'Tipo de inversion' not in df_cleaned.columns:
        st.info("La columna 'Tipo de inversion' no se encontró en tu portafolio. No se puede calcular la ponderación de riesgo.")
        return

    # Clean 'Tipo de inversion' column for consistent mapping
    df_cleaned['Tipo de inversion_cleaned'] = df_cleaned['Tipo de inversion'].astype(str).str.lower().str.strip()

    # Calculate total capital per investment type using the cleaned column
    diversification_data = df_cleaned.groupby('Tipo de inversion_cleaned')['Dinero'].sum().sort_values(ascending=False)

    if diversification_data.empty or diversification_data.sum() == 0:
        st.info("No hay datos de inversión para calcular la ponderación de riesgo y la diversificación.")
    else:
        st.markdown("Asigna un nivel de riesgo (1: Bajo, 2: Medio, 3: Alto) a cada tipo de inversión:")
        
        # Get unique investment types from the loaded data, ensuring they are stripped
        unique_investment_types_stripped = [t.strip() for t in diversification_data.index.tolist()]

        # Create selectboxes for user to define risk levels, arranged in columns
        num_cols = 2 # Number of columns for a compact layout
        cols = st.columns(num_cols) 
        assigned_risk_levels = {}
        
        # Determine the number of rows needed for the selectboxes
        num_rows = (len(unique_investment_types_stripped) + num_cols - 1) // num_cols

        for i, inv_type_stripped in enumerate(unique_investment_types_stripped):
            with cols[i % num_cols]: # Distribute selectboxes evenly between columns
                # Get current value from session state or default to 1
                default_risk = st.session_state.user_risk_levels.get(inv_type_stripped, 1)
                
                selected_risk = st.selectbox(
                    f"'{inv_type_stripped}'", # Shorter label for compactness
                    options=[1, 2, 3],
                    index=default_risk - 1, # Adjust index for 0-based list
                    key=f"risk_level_{inv_type_stripped}" # Use stripped name for unique key
                )
                # Store the selected value in session state with the stripped key
                st.session_state.user_risk_levels[inv_type_stripped] = selected_risk
                # Also populate local dict for current run's df_ponderation
                assigned_risk_levels[inv_type_stripped] = selected_risk
        
        # Save updated risk levels after all selections are made
        # This will be called on every rerun triggered by a selectbox change
        save_user_risk_levels(st.session_state.user_risk_levels)


        # Calculate percentage allocation
        total_invested = diversification_data.sum()
        diversification_percentage = (diversification_data / total_invested) * 100

        # Create a DataFrame for ponderation calculation
        # The 'Tipo de Inversión' column will hold the cleaned names
        df_ponderation = pd.DataFrame({
            "Tipo de Inversión": diversification_data.index, # This index is already cleaned
            "Capital (COP)": diversification_data.values,
            "Porcentaje (%)": diversification_percentage.values
        })

        # Map user-defined risk levels to investment types using the cleaned names
        df_ponderation['Nivel de Riesgo'] = df_ponderation['Tipo de Inversión'].apply(
            lambda x: assigned_risk_levels.get(x, 0) # x is already cleaned here, use assigned_risk_levels
        )

        # Calculate Ponderación (Riesgo × Porcentaje)
        df_ponderation['Ponderación (Riesgo × Porcentaje)'] = df_ponderation['Nivel de Riesgo'] * df_ponderation['Porcentaje (%)']

        total_ponderation = df_ponderation['Ponderación (Riesgo × Porcentaje)'].sum()

        st.dataframe(df_ponderation.style.format({
            "Capital (COP)": lambda x: formato_pesos(x),
            "Porcentaje (%)": "{:.2f}%",
            "Ponderación (Riesgo × Porcentaje)": "{:.2f}%"
        }))

        st.metric("Ponderación Total del Portafolio", f"{total_ponderation:.2f}%")

        # Interpret the total ponderation
        st.markdown("### Clasificación del Portafolio por Riesgo:")
        if total_ponderation <= 100:
            st.success(f"Tu portafolio es **Conservador** (Ponderación: {total_ponderation:.2f}%).")
            st.markdown("Un portafolio conservador se enfoca en la preservación del capital y busca rendimientos estables con bajo riesgo.")
        elif 101 <= total_ponderation <= 200:
            st.warning(f"Tu portafolio es **Equilibrado** (Ponderación: {total_ponderation:.2f}%).")
            st.markdown("Un portafolio equilibrado busca un balance entre crecimiento y seguridad, asumiendo un riesgo moderado para obtener retornos superiores.")
        else: # total_ponderation > 200
            st.error(f"Tu portafolio es **Agresivo** (Ponderación: {total_ponderation:.2f}%).")
            st.markdown("Un portafolio agresivo prioriza el crecimiento máximo del capital, asumiendo riesgos significativos y tolerando alta volatilidad.")
        
        st.markdown("""
        **Niveles de Riesgo por Tipo de Inversión:**
        - **1 (Bajo riesgo):** Inversiones estables y predecibles, con baja probabilidad de pérdida. Ej: Renta fija, CDTs, efectivo.
        - **2 (Riesgo medio):** Inversiones con cierta volatilidad, pero con un equilibrio entre riesgo y rendimiento. Ej: Neo bancos, terrenos en zonas urbanas, fondos indexados.
        - **3 (Alto riesgo):** Inversiones volátiles, con mayor probabilidad de pérdida pero también de altos rendimientos. Ej: Acciones individuales, criptomonedas, terrenos en zonas rurales, animales-semovientes.
        """)

        st.markdown("---")

        # --- 4. Análisis de Diversificación del Portafolio (Gráfico de Barras) ---
        st.subheader("📊 Análisis de Diversificación del Portafolio")
        st.markdown("""
        La diversificación es clave para reducir el riesgo. Este análisis muestra cómo tu capital
        está distribuido entre los diferentes tipos de inversión.
        """)

        # Bar chart for diversification
        fig_div, ax_div = plt.subplots(figsize=(10, 6))
        bars = ax_div.bar(df_ponderation["Tipo de Inversión"], df_ponderation["Porcentaje (%)"], color='skyblue')
        ax_div.set_title('Distribución del Capital por Tipo de Inversión')
        ax_div.set_xlabel('Tipo de Inversión')
        ax_div.set_ylabel('Porcentaje (%)')
        ax_div.set_ylim(0, 100) # Ensure y-axis goes from 0 to 100%
        plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
        plt.tight_layout()

        # Add percentage labels on top of each bar
        for bar in bars:
            yval = bar.get_height()
            ax_div.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}%', ha='center', va='bottom') # +1 for slight offset

        st.pyplot(fig_div)
        plt.close(fig_div)

        st.markdown("---")

        # --- 5. Recomendaciones de Diversificación ---
        st.subheader("💡 Recomendaciones de Diversificación")
        st.markdown("""
        Basado en la distribución de tu portafolio, aquí tienes algunas recomendaciones para optimizar tu diversificación:
        """)

        # Dynamic recommendations based on diversification_percentage
        if not diversification_percentage.empty:
            # Check for high concentration
            highly_concentrated = diversification_percentage[diversification_percentage > 50]
            if not highly_concentrated.empty:
                for inv_type, pct in highly_concentrated.items():
                    st.warning(f"⚠️ **Alta Concentración:** Tienes un **{pct:.1f}%** de tu capital en '{inv_type}'. Considera diversificar en otras clases de activos para reducir el riesgo asociado a una sola inversión.")
            
            # Check for very low allocation
            very_low_allocation = diversification_percentage[diversification_percentage < 5]
            if not very_low_allocation.empty:
                for inv_type, pct in very_low_allocation.items():
                    if pct > 0: # Only suggest if there's some allocation, not zero
                        st.info(f"ℹ️ **Baja Asignación:** Tu asignación en '{inv_type}' es del **{pct:.1f}%**. Si este tipo de inversión se alinea con tus objetivos, podrías considerar aumentarla para obtener un impacto más significativo en tu portafolio.")

            # General advice
            st.markdown("""
            * **Evalúa tu perfil de riesgo:** Asegúrate de que la distribución actual de tu portafolio se alinee con tu perfil de riesgo (conservador, moderado, agresivo) determinado en el cuestionario. Si no coinciden, considera ajustar tus inversiones.
            * **Considera diferentes clases de activos:** Diversifica no solo por tipo de inversión (renta fija, acciones, bienes raíces), sino también por sectores, geografías y monedas. Esto puede ayudar a mitigar el riesgo específico de un mercado o industria.
            * **Rebalancea periódicamente:** Con el tiempo, el rendimiento de tus inversiones puede alterar la distribución original de tu portafolio. Rebalancear significa vender activos que han crecido mucho para comprar los que han quedado rezagados, volviendo a tu asignación de activos deseada. Esto te ayuda a mantener tu nivel de riesgo objetivo.
            * **Invierte en activos con baja correlación:** Busca inversiones que no se muevan en la misma dirección al mismo tiempo. Por ejemplo, cuando la renta variable baja, la renta fija podría subir. Combinar este tipo de activos puede suavizar las fluctuaciones de tu portafolio.
            * **Revisa tus objetivos:** A medida que tus objetivos financieros y tu horizonte de inversión cambian, también debería hacerlo tu estrategia de diversificación. Una persona joven con un horizonte de inversión largo puede permitirse más riesgo que alguien cercano a la jubilación.
            * **Consulta a un experto:** Para una estrategia de diversificación más personalizada y detallada, considera buscar el asesoramiento de un profesional financiero.
            """)
        else:
            st.info("Carga tu portafolio para recibir recomendaciones de diversificación.")