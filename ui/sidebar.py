import streamlit as st

from config import SHOP_RATES
from database import add_employee, clear_history, delete_employee


def render_sidebar(employees: list[dict], history_count: int) -> None:
    st.markdown("### 📍 Магазины")
    for shop_name, rate in SHOP_RATES.items():
        st.markdown(
            f'<div class="shop-badge">🏪 <b>{shop_name}</b> — {rate:,} ₽/день</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("### 📋 Формула")
    st.markdown(
        """
        **Итого** = Оклад + 5% × Выручка − Штраф

        Оклад зависит от магазина.
        Процент от выручки — **5%**.
        """
    )

    st.divider()
    st.markdown("### 👥 Сотрудники")

    new_employee_name = st.text_input(
        "Новый сотрудник",
        placeholder="Имя флориста",
        key="new_employee_name",
        label_visibility="collapsed",
    )
    if st.button("➕ Добавить", key="add_employee_btn", use_container_width=True):
        result = add_employee(new_employee_name)
        if result == "ok":
            st.rerun()
        elif result == "duplicate":
            st.sidebar.warning("Такой сотрудник уже есть")
        else:
            st.sidebar.warning("Введите имя сотрудника")

    if employees:
        for emp in employees:
            st.markdown(f"• {emp['name']}")

        employee_names = {emp["id"]: emp["name"] for emp in employees}
        delete_employee_id = st.selectbox(
            "Удалить сотрудника",
            options=list(employee_names.keys()),
            format_func=lambda emp_id: employee_names[emp_id],
            key="delete_employee_select",
        )
        if st.button("🗑 Удалить", key="delete_employee_btn", use_container_width=True):
            if delete_employee(delete_employee_id):
                if st.session_state.last_result:
                    last_employee = st.session_state.last_result.get("employee")
                    if last_employee == employee_names.get(delete_employee_id):
                        st.session_state.last_result = None
                st.rerun()
            else:
                st.sidebar.error("Не удалось удалить сотрудника")
    else:
        st.caption("Список пуст")

    st.divider()
    if history_count:
        st.markdown(f"**Расчётов в истории:** {history_count}")
        if st.button("🗑 Очистить историю", key="clear_history_btn", use_container_width=True):
            clear_history()
            st.rerun()
