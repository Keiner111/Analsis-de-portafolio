import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def formato_pesos(val):
    """Formatea el numero con separador de miles como '.' y decimal como ','"""
    return f"${val:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_devaluacion(capital_productivo, ingreso_pasivo_mensual):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
        <h2 style='color: white; text-align: center; margin: 0;'>
            📊 Análisis de Devaluación e Inflación + Crecimiento con Reinversión
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Obtener el capital total del DataFrame si está disponible
    capital_inicial_real = capital_productivo
    if 'df' in st.session_state and st.session_state.df is not None:
        df_temp = st.session_state.df.copy()
        df_temp['Dinero'] = df_temp['Dinero'].replace('[\$,]', '', regex=True).astype(float)
        capital_inicial_real = df_temp['Dinero'].sum()

    # Mostrar información del capital con diseño mejorado y colores
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='color: white; text-align: center; margin: 0;'>
            💼 Información del Portafolio
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("💰 Capital Total", formato_pesos(capital_inicial_real))
    with col_info2:
        st.metric("🏦 Capital Productivo", formato_pesos(capital_productivo))
    with col_info3:
        st.metric("💵 Ingreso Mensual", formato_pesos(ingreso_pasivo_mensual))

    st.markdown("---")

    # Inicializar variables en st.session_state si no existen
    if "inflacion_anual_input" not in st.session_state:
        st.session_state.inflacion_anual_input = 3.0
    if "anios_input" not in st.session_state:
        st.session_state.anios_input = 2
    if "rentabilidad_mensual_input" not in st.session_state:
        st.session_state.rentabilidad_mensual_input = 1.79

    # Crear columnas para mejor organización
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0;'>
        <h4 style='color: white; text-align: center; margin: 0;'>
            ⚙️ Configuración del Análisis
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: #e3f2fd; padding: 12px; border-radius: 8px; border-left: 5px solid #2196f3;'>
            <strong style='font-size: 1.1em; color: #1565c0;'>📅 Parámetros de Inflación y Tiempo</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Entrada de usuario
        inflacion_anual = st.number_input(
            "Inflación anual estimada (%)",
            min_value=0.0,
            max_value=50.0,
            value=st.session_state.inflacion_anual_input,
            step=0.01,
            format="%.2f",
            key="inflacion_anual_key",
            help="Inflación anual esperada en Colombia (histórico: 3-10%)"
        )
        st.session_state.inflacion_anual_input = inflacion_anual

        anios = st.slider(
            "Período de análisis (años)",
            min_value=1,
            max_value=20,
            value=st.session_state.anios_input,
            key="anios_key",
            help="Tiempo de proyección del análisis"
        )
        st.session_state.anios_input = anios

    with col2:
        st.markdown("""
        <div style='background-color: #f3e5f5; padding: 12px; border-radius: 8px; border-left: 5px solid #9c27b0;'>
            <strong style='font-size: 1.1em; color: #6a1b9a;'>💎 Parámetros de Rentabilidad y Reinversión</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Rentabilidad mensual estimada
        rentabilidad_mensual_simulacion = st.number_input(
            "Rentabilidad mensual estimada (%)",
            min_value=0.0,
            max_value=20.0,
            value=st.session_state.rentabilidad_mensual_input,
            step=0.01,
            format="%.2f",
            key="rentabilidad_mensual_key",
            help="Rendimiento mensual esperado de tu inversión"
        ) / 100
        st.session_state.rentabilidad_mensual_input = rentabilidad_mensual_simulacion * 100

        # Reinversión con información clara
        porcentaje_reinversion_pct = st.slider(
            "Porcentaje de ganancias a reinvertir (%)",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
            help="¿Qué porcentaje de las ganancias reinviertes?"
        )
        
        valor_reinversion = (ingreso_pasivo_mensual * porcentaje_reinversion_pct) / 100
        valor_retiro = ingreso_pasivo_mensual - valor_reinversion
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.success(f"**↻ Reinversión:** {formato_pesos(valor_reinversion)}")
        with col_r2:
            st.info(f"**↓ Retiro:** {formato_pesos(valor_retiro)}")
        
        porcentaje_reinversion = porcentaje_reinversion_pct / 100

    # Selección del capital a analizar
    st.markdown("---")
    usar_capital_total = st.radio(
        "💼 ¿Qué capital deseas usar para el análisis?",
        options=[
            f"Capital Total ({formato_pesos(capital_inicial_real)})",
            f"Solo Capital Productivo ({formato_pesos(capital_productivo)})"
        ],
        help="El capital total incluye todas tus inversiones. El capital productivo solo las que generan intereses mensuales.",
        horizontal=True
    )
    
    capital_para_analisis = capital_inicial_real if "Total" in usar_capital_total else capital_productivo

    if inflacion_anual == 0:
        st.warning("⚠️ Por favor, ingresa un valor de inflación mayor a 0 para continuar.")
        return

    # Cálculos
    meses = anios * 12
    inflacion_mensual = inflacion_anual / 12 / 100

    # Simulación sin inversión
    poder_adquisitivo = []
    capital_ajustado = capital_para_analisis
    for mes in range(meses + 1):
        poder_adquisitivo.append(capital_ajustado)
        capital_ajustado /= (1 + inflacion_mensual)

    # Simulación con reinversión
    crecimiento_real = []
    capital_real = capital_para_analisis
    ingresos_acumulados = []
    ingreso_acumulado = 0
    
    for mes in range(meses + 1):
        crecimiento_real.append(capital_real)
        if mes > 0:
            ingreso_real = ingreso_pasivo_mensual * ((1 + inflacion_mensual) ** -mes)
            ingreso_acumulado += ingreso_real
            capital_real += ingreso_real * porcentaje_reinversion
            capital_real *= (1 + rentabilidad_mensual_simulacion)
            capital_real /= (1 + inflacion_mensual)
        ingresos_acumulados.append(ingreso_acumulado)

    # Escenarios de rentabilidad
    escenarios = {
        "Conservador": rentabilidad_mensual_simulacion * 0.7,
        "Base": rentabilidad_mensual_simulacion,
        "Optimista": rentabilidad_mensual_simulacion * 1.3
    }
    
    escenarios_data = {}
    for nombre, rentabilidad in escenarios.items():
        capital_escenario = capital_para_analisis
        valores_escenario = []
        for mes in range(meses + 1):
            valores_escenario.append(capital_escenario)
            if mes > 0:
                ingreso_real = ingreso_pasivo_mensual * ((1 + inflacion_mensual) ** -mes)
                capital_escenario += ingreso_real * porcentaje_reinversion
                capital_escenario *= (1 + rentabilidad)
                capital_escenario /= (1 + inflacion_mensual)
        escenarios_data[nombre] = valores_escenario

    # Resultados principales
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0;'>
        <h4 style='color: white; text-align: center; margin: 0;'>
            📈 Resultados del Análisis
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💼 Capital Inicial", formato_pesos(capital_para_analisis))
    
    with col2:
        perdida_valor = capital_para_analisis - poder_adquisitivo[-1]
        perdida_pct = (perdida_valor / capital_para_analisis) * 100
        st.metric(
            "📉 Sin Inversión", 
            formato_pesos(poder_adquisitivo[-1]),
            f"-{perdida_pct:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        ganancia_real = crecimiento_real[-1] - capital_para_analisis
        ganancia_pct = (ganancia_real / capital_para_analisis) * 100
        st.metric(
            "📊 Con Reinversión", 
            formato_pesos(crecimiento_real[-1]),
            f"+{ganancia_pct:.1f}%"
        )
    
    with col4:
        diferencia = crecimiento_real[-1] - poder_adquisitivo[-1]
        st.metric(
            "✨ Ganancia vs Inflación", 
            formato_pesos(diferencia),
            f"+{((diferencia / poder_adquisitivo[-1]) * 100):.1f}%"
        )

    # Gráfico principal mejorado
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0;'>
        <h4 style='color: #333; text-align: center; margin: 0;'>
            📉 Evolución del Capital en Términos Reales
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    meses_x = list(range(meses + 1))

    # Línea de inflación
    ax.plot(meses_x, poder_adquisitivo, label="Sin inversión (solo inflación)", 
            color="#e74c3c", linewidth=2.5, alpha=0.85, linestyle='--')
    
    # Escenarios de inversión
    colors = {'Conservador': '#f39c12', 'Base': '#27ae60', 'Optimista': '#3498db'}
    for nombre, valores in escenarios_data.items():
        alpha = 1.0 if nombre == "Base" else 0.65
        linewidth = 3.5 if nombre == "Base" else 2.2
        ax.plot(meses_x, valores, 
                label=f"{nombre} ({escenarios[nombre]*100:.2f}% mensual)", 
                color=colors[nombre], linewidth=linewidth, alpha=alpha)

    ax.set_title("Evolución del Poder Adquisitivo vs Inversión (COP)", 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel("Meses", fontsize=13, fontweight='bold')
    ax.set_ylabel("Valor en Pesos Colombianos", fontsize=13, fontweight='bold')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${int(x):,}".replace(",", "."))
    )
    
    # Área sombreada de ganancia
    ax.fill_between(meses_x, poder_adquisitivo, escenarios_data["Base"], 
                    alpha=0.15, color='#27ae60')
    
    plt.tight_layout()
    st.pyplot(fig)

    # Explicación de la gráfica
    st.markdown("""
    <div style='background-color: #e8eaf6; padding: 20px; border-radius: 10px; border-left: 5px solid #3f51b5; margin-top: 20px;'>
        <strong style='font-size: 1.2em; color: #1a237e;'>📖 Cómo interpretar esta gráfica:</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col_exp1, col_exp2 = st.columns([1, 1])
    
    with col_exp1:
        st.markdown("""
        <div style='background-color: #ffebee; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #c62828; font-size: 1.05em;'>🔴 Línea roja punteada (Sin inversión):</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Muestra cómo tu dinero pierde valor con el tiempo debido a la inflación. 
            Si solo guardas el dinero sin invertirlo, cada mes compra menos cosas.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #e65100; font-size: 1.05em;'>🟠 Línea naranja (Escenario Conservador):</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Proyección con una rentabilidad 30% menor a la estimada. 
            Representa un escenario pesimista o de bajo rendimiento.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #2e7d32; font-size: 1.05em;'>🟢 Línea verde (Escenario Base):</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Tu proyección principal basada en la rentabilidad que ingresaste. 
            Esta es la línea más importante y realista según tus parámetros.
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_exp2:
        st.markdown("""
        <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #01579b; font-size: 1.05em;'>🔵 Línea azul (Escenario Optimista):</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Proyección con una rentabilidad 30% mayor a la estimada. 
            Representa el mejor escenario posible.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #f1f8e9; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #33691e; font-size: 1.05em;'>💚 Área sombreada verde:</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Representa la ganancia que obtienes al invertir con reinversión vs. no hacer nada. 
            Mientras más grande sea esta área, mejor está funcionando tu estrategia.
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background-color: #ede7f6; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
            <strong style='color: #4527a0; font-size: 1.05em;'>💡 Conclusión:</strong><br>
            <span style='color: #333; font-weight: 500;'>
            Si las líneas de inversión están por encima de la línea roja, 
            significa que estás ganándole a la inflación y tu dinero está creciendo en términos reales.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Tabla detallada
    st.markdown("---")
    with st.expander("📋 Ver proyección detallada por años", expanded=False):
        anos_data = []
        for ano in range(1, anios + 1):
            mes_idx = ano * 12
            anos_data.append({
                "Año": ano,
                "Sin Inversión": formato_pesos(poder_adquisitivo[mes_idx]),
                "Conservador": formato_pesos(escenarios_data["Conservador"][mes_idx]),
                "Base": formato_pesos(escenarios_data["Base"][mes_idx]),
                "Optimista": formato_pesos(escenarios_data["Optimista"][mes_idx])
            })
        
        df_proyeccion = pd.DataFrame(anos_data)
        st.dataframe(df_proyeccion, use_container_width=True, hide_index=True)

    # Análisis de rentabilidad
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0;'>
        <h4 style='color: #333; text-align: center; margin: 0;'>
            💡 Análisis de Rentabilidad
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: #4ca699; padding: 12px; border-radius: 8px; border-left: 4px solid #4caf50; margin-bottom: 15px;'>
            <strong>📊 Rendimientos mensuales</strong>
        </div>
        """, unsafe_allow_html=True)
        
        rentabilidad_real_mensual = (ingreso_pasivo_mensual / capital_para_analisis * 100) if capital_para_analisis > 0 else 0
        inflacion_mensual_pct = inflacion_mensual * 100
        st.markdown(f"""
        <div style='color: #1b5e20; font-weight: 500; margin-top: 10px;'>
        • Tu portafolio: <strong style='font-size: 1.1em;'>{rentabilidad_real_mensual:.2f}%</strong><br>
        • Inflación: <strong style='font-size: 1.1em;'>{inflacion_mensual_pct:.2f}%</strong><br>
        • Rentabilidad real: <strong style='font-size: 1.1em;'>{rentabilidad_real_mensual - inflacion_mensual_pct:.2f}%</strong>
        </div>
        """, unsafe_allow_html=True)
        
        rentabilidad_anual_nominal = rentabilidad_real_mensual * 12
        rentabilidad_anual_real = rentabilidad_anual_nominal - inflacion_anual
        
        st.markdown("""
        <div style='background-color: #fff3e0; padding: 12px; border-radius: 8px; border-left: 5px solid #ff9800; margin-top: 15px;'>
            <strong style='font-size: 1.1em; color: #e65100;'>📅 Rendimientos anuales equivalentes</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='color: #bf360c; font-weight: 500; margin-top: 10px;'>
        • Nominal: <strong style='font-size: 1.1em;'>{rentabilidad_anual_nominal:.2f}%</strong><br>
        • Real (descontando inflación): <strong style='font-size: 1.1em;'>{rentabilidad_anual_real:.2f}%</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #e1f5fe; padding: 12px; border-radius: 8px; border-left: 5px solid #03a9f4; margin-bottom: 15px;'>
            <strong style='font-size: 1.1em; color: #01579b;'>🎯 Evaluación de tu estrategia</strong>
        </div>
        """, unsafe_allow_html=True)
        if rentabilidad_real_mensual > inflacion_mensual_pct * 1.5:
            st.success("✅ **Excelente:** Estás superando significativamente la inflación. Tu estrategia es muy efectiva.")
        elif rentabilidad_real_mensual > inflacion_mensual_pct:
            st.success("✅ **Bien:** Estás creciendo tu dinero más rápido que la inflación, lo cual es positivo.")
        elif rentabilidad_real_mensual == inflacion_mensual_pct:
            st.info("ℹ️ **Neutro:** Tu crecimiento compensa la inflación. Mantienes el poder adquisitivo.")
        else:
            st.warning("⚠️ **Atención:** Tus rendimientos están por debajo de la inflación. Considera optimizar tu estrategia.")

    # Recomendaciones
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); 
                padding: 15px; border-radius: 10px; margin: 20px 0;'>
        <h4 style='color: white; text-align: center; margin: 0;'>
            💡 Recomendaciones Personalizadas
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    if rentabilidad_real_mensual < inflacion_mensual_pct:
        st.markdown("""
        <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 5px solid #ff9800;'>
            <strong style='font-size: 1.1em; color: #e65100;'>🔍 Para mejorar tu situación:</strong><br><br>
            <span style='color: #333; font-weight: 500;'>
            🎯 Busca inversiones con mayor rentabilidad<br>
            🌐 Considera diversificar tu portafolio<br>
            📈 Evalúa opciones como fondos indexados, acciones o bienes raíces<br>
            💰 Aumenta el porcentaje de reinversión si es posible<br>
            📚 Educa tu conocimiento financiero para mejores decisiones
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 5px solid #4caf50;'>
            <strong style='font-size: 1.1em; color: #2e7d32;'>🎉 Para mantener y mejorar:</strong><br><br>
            <span style='color: #333; font-weight: 500;'>
            ✅ Mantén la disciplina de reinversión<br>
            💪 Considera aumentar aportes mensuales si es posible<br>
            🔄 Revisa periódicamente el desempeño vs inflación<br>
            🌟 Diversifica para reducir riesgos<br>
            📊 Registra tus avances y celebra tus logros
            </span>
        </div>
        """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Análisis Financiero - Inflación e Inversiones",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
        <h1 style='color: white; text-align: center; margin: 0;'>
            💰 Análisis Financiero: Inflación e Inversiones
        </h1>
        <p style='color: #e0e0e0; text-align: center; margin: 10px 0 0 0; font-size: 1.1em;'>
            Herramienta para proyectar el impacto de la inflación y estrategias de inversión
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar mejorado
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: white; text-align: center; margin: 0;'>
                ⚙️ Parámetros del Portafolio
            </h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("Configura los valores iniciales de tu inversión")
        
        capital_productivo = st.number_input(
            "💵 Capital productivo inicial (COP)",
            min_value=100000,
            value=10000000,
            step=100000,
            format="%d",
            help="Tu capital inicial que genera ingresos"
        )
        
        ingreso_pasivo_mensual = st.number_input(
            "💸 Ingreso pasivo mensual (COP)",
            min_value=1000,
            value=150000,
            step=1000,
            format="%d",
            help="Ingresos mensuales generados por tu capital"
        )
        
        st.markdown("---")
        
        if capital_productivo > 0:
            rentabilidad_actual = (ingreso_pasivo_mensual / capital_productivo) * 100
            st.markdown(f"""
            <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50;'>
                <strong style='color: #2e7d32;'>📊 Rentabilidad actual:</strong><br>
                <span style='color: #1b5e20;'>• Mensual: <strong>{rentabilidad_actual:.2f}%</strong></span><br>
                <span style='color: #1b5e20;'>• Anual: <strong>~{rentabilidad_actual * 12:.1f}%</strong></span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 5px solid #ff9800;'>
            <strong style='font-size: 1.05em; color: #e65100;'>💡 Tip:</strong> 
            <span style='color: #333; font-weight: 500;'>Ajusta los parámetros en la sección principal para explorar diferentes escenarios.</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Ejecutar análisis principal
    calcular_devaluacion(capital_productivo, ingreso_pasivo_mensual)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); 
                padding: 25px; border-radius: 10px; text-align: center;'>
        <p style='color: #1a237e; margin: 8px 0; font-size: 1.1em; font-weight: 600;'>
            📌 Recuerda: Los resultados son proyecciones basadas en los parámetros ingresados.
        </p>
        <p style='color: #283593; margin: 8px 0; font-size: 1em; font-weight: 500;'>
            Consulta con un asesor financiero para decisiones de inversión importantes.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Inicializar session_state.df si no existe
    if 'df' not in st.session_state:
        st.session_state.df = None
    main()