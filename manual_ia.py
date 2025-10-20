import streamlit as st

def mostrar_manual_ia():
    st.title("📘 Manual de Usuario - IA Financiera")

    st.markdown("""
    Bienvenido al módulo de ayuda. Aquí aprenderás a usar cada función de tu asistente financiero.

    ---
    ### 🧠 Funcionalidades clave:

    - 📥 **Cargar Portafolio:** Sube tu archivo `.xlsx` con tus inversiones.
    - 📊 **Análisis del Portafolio:** Revisa capital, ingresos pasivos y KPIs.
    - 🧾 **Generar Informe:** Obtén un resumen en Word con gráficos y recomendaciones.
    - ♻️ **Rebalanceo:** Recibe sugerencias automáticas para mejorar tu estrategia.
    - 🔥 **Calculadora FIRE:** Calcula cuándo podrías lograr la libertad financiera.
    - 🛤️ **Ruta hacia la meta:** Proyecta cuánto te tomará alcanzar tu capital objetivo.
    - 🐄 **Activos Físicos:** Evalúa inversiones como ganado, cultivos o maquinaria.
    - 📉 **Inflación y Devaluación:** Ajusta tus rendimientos frente al costo de vida.
    - 💱 **Divisas:** Consulta tasas de cambio actualizadas.
    - ⏳ **Histórico del Portafolio:** Visualiza cómo ha evolucionado tu patrimonio mes a mes.
    - 💬 **Chat Financiero:** Interactúa con una IA entrenada para responder sobre tu portafolio.
    
    ---
    ### 📄 Formato del archivo Excel

    Tu archivo `.xlsx` debe incluir las siguientes columnas con nombres exactos:

    | Columna                        | Descripción                                                     |
    |--------------------------------|------------------------------------------------------------------|
    | Items                          | ID o número de fila                                              |
    | Personas                       | Nombre del titular de la inversión                               |
    | Dinero                         | Monto invertido en pesos colombianos                             |
    | Porcentaje                     | Participación en la inversión (%)                                |
    | Tipo de inversión              | Ejemplo: Renta fija, Variable, Físico                            |
    | Interes anual (%)              | Tasa de interés anual estimada (%)                               |
    | Interes Mensual                | Ingreso mensual en COP                                           |
    | Meta Mensual (%)               | Porcentaje de la meta de ingreso mensual                         |
    | Rendimiento Real -Inflacion (%)| Tasa real ajustada por inflación (%)                             |
    | Rendimiento total calculado    | Retorno total estimado                                           |
    | Ingreso Mensual Necesario      | Lo que necesitas generar mensualmente                            |
    | Tasa Mensual Necesaria (%)     | Tasa mínima mensual requerida para lograr la meta                |

    #### 🧪 Ejemplo:

    | Items | Personas   | Dinero    | Porcentaje | Tipo de inversión | Interes anual (%) | Interes Mensual | Meta Mensual (%) | Rendimiento Real -Inflacion (%) | Rendimiento total calculado | Ingreso Mensual Necesario | Tasa Mensual Necesaria (%) |
    |-------|------------|-----------|------------|--------------------|--------------------|------------------|-------------------|-------------------------------|-----------------------------|----------------------------|-----------------------------|
    | 1     | Omar Ruiz  | 10,510,000| 27.75%     | Renta fija         | 24                 | 210,200          | 32%               | 18.95                         | 5.26                        | 316,560.70                | 3.012%                      |

    ---
    ### ⚠️ Recomendaciones importantes:

    - 📌 Las columnas `Dinero` e `Interes Mensual` deben tener **solo números**, sin `$` ni `%`.
    - 📅 Si usas una columna de fecha (`Fecha de Inversión`), debe estar en formato **YYYY-MM-DD**.
    - 🔢 Usa **punto (.) como separador decimal**, no coma (,).
    - ✅ Guarda tu archivo en formato **Excel (.xlsx)**.
    - 🚫 No cambies los nombres de las columnas.

    ---
    ### 📥 Descargar plantilla de ejemplo
    """)

    try:
        with open("plantilla_portafolio.xlsx", "rb") as file:
            st.download_button(
                label="📄 Descargar plantilla Excel de ejemplo",
                data=file,
                file_name="plantilla_portafolio.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo 'plantilla_portafolio.xlsx'. Asegúrate de colocarlo en el mismo directorio.")
