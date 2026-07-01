from datetime import date

import streamlit as st

from analytics import (
    PERIOD_OPTIONS,
    aggregate_by_employee,
    filter_history,
    get_history_date_bounds,
    get_period_bounds,
)
from payroll import format_rubles


def _money_columns() -> dict:
    return {
        "Выручка": st.column_config.NumberColumn(format="%d ₽"),
        "Оклад": st.column_config.NumberColumn(format="%d ₽"),
        "Процент": st.column_config.NumberColumn(format="%d ₽"),
        "Штраф": st.column_config.NumberColumn(format="%d ₽"),
        "Итого": st.column_config.NumberColumn(format="%d ₽"),
        "Сумма": st.column_config.NumberColumn(format="%d ₽"),
    }


def render_analytics(history: list[dict]) -> None:
    st.divider()
    st.markdown("### 📊 Аналитика выплат")

    if not history:
        st.info("История расчётов пуста. Выполните первый расчёт, чтобы увидеть аналитику.")
        return

    filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.2, 1])

    with filter_col1:
        period_preset = st.selectbox("Период", PERIOD_OPTIONS, key="analytics_period")

    today = date.today()
    if period_preset == "Произвольный период":
        min_date, max_date = get_history_date_bounds(history)
        with filter_col2:
            date_from = st.date_input(
                "С",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="analytics_date_from",
            )
        with filter_col3:
            date_to = st.date_input(
                "По",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="analytics_date_to",
            )
    else:
        date_from, date_to = get_period_bounds(period_preset, today, history)
        st.caption(
            f"📅 {date_from.strftime('%d.%m.%Y')} — {date_to.strftime('%d.%m.%Y')}"
        )

    employees_in_history = sorted({row["Сотрудник"] for row in history})
    employee_filter = st.selectbox(
        "Сотрудник",
        ["Все сотрудники", *employees_in_history],
        key="analytics_employee",
    )
    selected_employee = None if employee_filter == "Все сотрудники" else employee_filter

    filtered = filter_history(history, date_from, date_to, selected_employee)

    if not filtered:
        st.warning(
            f"Нет расчётов за период "
            f"{date_from.strftime('%d.%m.%Y')} — {date_to.strftime('%d.%m.%Y')}"
            + (f" для сотрудника **{selected_employee}**" if selected_employee else "")
            + "."
        )
        return

    total_payout = sum(row["Итого"] for row in filtered)
    summary_col1, summary_col2 = st.columns(2)
    summary_col1.metric("Итого за период", format_rubles(total_payout))
    summary_col2.metric("Количество расчётов", len(filtered))

    st.markdown("#### По сотрудникам")
    by_employee = aggregate_by_employee(filtered)
    st.dataframe(
        by_employee,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Расчётов": st.column_config.NumberColumn(format="%d"),
            "Сумма": st.column_config.NumberColumn(format="%d ₽"),
        },
    )

    st.markdown("#### Детали расчётов")
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config=_money_columns(),
    )
