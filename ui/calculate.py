from datetime import date

import streamlit as st

from config import SHOP_RATES
from database import get_all_calculations, save_calculation
from payroll import calculate_salary, format_rubles, percent_share_of_total


def handle_calculate(
    employee: str | None,
    shop: str,
    revenue: float,
    fine: float,
    work_date: date,
) -> list[dict]:
    if not employee:
        st.error("Выберите сотрудника")
        return get_all_calculations()

    calculation = calculate_salary(shop, revenue, fine)
    save_calculation(
        work_date=work_date.strftime("%d.%m.%Y"),
        employee=employee,
        shop=shop,
        revenue=revenue,
        base_salary=calculation["base"],
        percent=calculation["percent"],
        fine=calculation["fine"],
        total=calculation["total"],
    )
    st.session_state.last_result = {
        "employee": employee,
        "shop": shop,
        "work_date": work_date,
        "revenue": revenue,
        "fine": fine,
        "calculation": calculation,
    }
    st.toast(f"Расчёт для {employee} сохранён", icon="✅")
    return get_all_calculations()


def render_result_preview(result_data: dict) -> None:
    result = result_data["calculation"]
    employee = result_data["employee"]
    shop = result_data["shop"]
    work_date = result_data["work_date"]
    revenue = result_data["revenue"]

    st.markdown(
        f"""
        <div class="result-card">
            <div class="label">Итого к выплате</div>
            <div class="amount">{format_rubles(result["total"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Оклад", format_rubles(result["base"]))
    m2.metric("5% от выручки", format_rubles(result["percent"]))
    m3.metric("Штраф", f"−{format_rubles(result['fine'])}")

    share = percent_share_of_total(result)
    if revenue > 0 and share is not None:
        st.progress(share)
        st.caption("Доля процента от итоговой выплаты")

    st.info(
        f"👤 **{employee}** · 🏪 {shop} · 📅 {work_date.strftime('%d.%m.%Y')}"
    )


def render_calculate_section(employees: list[dict], history: list[dict]) -> list[dict]:
    col_form, col_preview = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("### Данные сотрудника")

        has_employees = bool(employees)
        if not has_employees:
            st.warning(
                "⚠️ Список сотрудников пуст. Добавьте флористов в боковом меню в разделе «Сотрудники»."
            )
            employee = None
        else:
            employee = st.selectbox(
                "Сотрудник",
                [emp["name"] for emp in employees],
            )

        shop = st.selectbox("Магазин", list(SHOP_RATES.keys()))

        revenue = st.number_input(
            "Выручка, ₽",
            min_value=0.0,
            step=100.0,
            format="%.0f",
        )

        fine = st.number_input(
            "Штраф, ₽",
            min_value=0.0,
            step=100.0,
            format="%.0f",
        )

        work_date = st.date_input("Дата", value=date.today())

        calculate_btn = st.button(
            "💰 Рассчитать зарплату",
            type="primary",
            use_container_width=True,
            disabled=not has_employees,
        )

    with col_preview:
        st.markdown("### Расчёт")

        if calculate_btn:
            history = handle_calculate(employee, shop, revenue, fine, work_date)

        if st.session_state.last_result:
            render_result_preview(st.session_state.last_result)
        else:
            st.info("Заполните форму и нажмите «Рассчитать зарплату»")

    return history
