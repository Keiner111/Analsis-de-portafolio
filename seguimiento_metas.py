import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Función para formatear valores monetarios en pesos colombianos
def formato_pesos(valor):
    """
    Formatea un valor numérico como pesos colombianos.
    Ejemplo: 1234567.89 -> $ 1.234.567
    """
    return f"${valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def mostrar_seguimiento_metas(df):
    """
    Muestra el módulo de seguimiento de metas financieras.
    Permite al usuario definir, ver y seguir el progreso de sus metas.
    """
    st.header("🎯 Seguimiento de Metas Financieras")

    st.markdown("""
    Aquí puedes definir tus metas financieras (ej. comprar una casa, jubilación, educación)
    y seguir tu progreso hacia ellas.
    """)

    # Inicializar la lista de metas en st.session_state si no existe
    if 'financial_goals' not in st.session_state:
        st.session_state.financial_goals = []

    # --- Añadir nueva meta ---
    st.subheader("➕ Añadir Nueva Meta")
    with st.form("add_goal_form"):
        goal_name = st.text_input("Nombre de la Meta (ej. Fondo para la casa)")
        target_amount = st.number_input("Monto Objetivo (COP)", min_value=0.0, step=100000.0, format="%.2f")
        target_date = st.date_input("Fecha Límite", min_value=datetime.now().date() + timedelta(days=30))
        
        add_goal_button = st.form_submit_button("Guardar Meta")

    if add_goal_button and goal_name and target_amount > 0:
        st.session_state.financial_goals.append({
            "name": goal_name,
            "target_amount": target_amount,
            "target_date": target_date
        })
        st.success(f"Meta '{goal_name}' añadida correctamente.")
        st.rerun() # Recargar para mostrar la meta en la lista

    st.markdown("---")

    # --- Mostrar y seguir metas existentes ---
    st.subheader("📋 Mis Metas")

    if not st.session_state.financial_goals:
        st.info("Aún no has definido ninguna meta. ¡Empieza añadiendo una!")
        return

    # Limpiar y convertir 'Dinero' del portafolio a numérico
    current_capital = 0.0
    if df is not None:
        df_cleaned = df.copy()
        df_cleaned['Dinero'] = pd.to_numeric(df_cleaned['Dinero'].replace('[\$,]', '', regex=True), errors='coerce').fillna(0)
        current_capital = df_cleaned['Dinero'].sum()
    else:
        st.warning("Carga tu portafolio para ver cómo tu capital actual contribuye a tus metas.")

    # Display each goal with progress
    for i, goal in enumerate(st.session_state.financial_goals):
        goal_name = goal["name"]
        target_amount = goal["target_amount"]
        target_date = goal["target_date"]

        st.markdown(f"#### {goal_name}")
        st.write(f"**Monto Objetivo:** {formato_pesos(target_amount)}")
        st.write(f"**Fecha Límite:** {target_date.strftime('%d/%m/%Y')}")

        # Calculate progress
        progress_ratio = min(current_capital / target_amount, 1.0) if target_amount > 0 else 0
        progress_percentage = progress_ratio * 100

        st.progress(progress_ratio, text=f"Progreso: {progress_percentage:.1f}%")

        # Calculate remaining time
        today = datetime.now().date()
        remaining_days = (target_date - today).days
        
        if remaining_days > 0:
            remaining_months = remaining_days / 30.44 # Average days per month
            st.write(f"Tiempo Restante: {int(remaining_months)} meses y {int(remaining_days % 30.44)} días")
            
            # Calculate required monthly contribution (simple linear calculation)
            remaining_amount = target_amount - current_capital
            if remaining_amount > 0 and remaining_months > 0:
                required_monthly_contribution = remaining_amount / remaining_months
                st.info(f"Para alcanzar esta meta, necesitarías aportar aproximadamente **{formato_pesos(required_monthly_contribution)}** mensualmente.")
            elif remaining_amount <= 0:
                st.success("¡Felicidades! Has alcanzado o superado el monto objetivo para esta meta.")
            else:
                st.info("Aún no tienes capital para esta meta o el tiempo restante es muy corto.")
        elif remaining_days <= 0 and current_capital >= target_amount:
            st.success("¡Felicidades! Has alcanzado esta meta a tiempo.")
        elif remaining_days <= 0 and current_capital < target_amount:
            st.error("¡Atención! La fecha límite para esta meta ha pasado y no se ha alcanzado el monto objetivo.")
        
        # Option to delete goal
        if st.button(f"Eliminar Meta '{goal_name}'", key=f"delete_goal_{i}"):
            st.session_state.financial_goals.pop(i)
            st.success(f"Meta '{goal_name}' eliminada.")
            st.rerun()

        st.markdown("---")

