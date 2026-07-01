import calendar
import streamlit as st
from collections import defaultdict
from datetime import date, timedelta

from config import SHOP_RATES
from database import (
    add_employee,
    clear_history,
    delete_employee,
    get_all_calculations,
    get_all_employees,
    save_calculation,
)
from payroll import calculate_salary, format_rubles, percent_share_of_total

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #f8b4d9 0%, #e8a0bf 40%, #c9e4ca 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(232, 160, 191, 0.25);
}

.main-header h1 {
    color: #2d3436;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}

.main-header p {
    color: #636e72;
    margin: 0.5rem 0 0 0;
    font-size: 1rem;
}

.result-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.75rem 2rem;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.35);
}

.result-card .amount {
    font-size: 2.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.result-card .label {
    font-size: 0.9rem;
    opacity: 0.9;
    margin-top: 0.25rem;
}

div[data-testid="stMetric"] {
    background: #f8f9fa;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
}

div[data-testid="stMetric"] label {
    font-size: 0.85rem !important;
    color: #636e72 !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #2d3436 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 10px;
    padding: 0.6rem 2rem;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fdf6f9 0%, #f0f4f8 100%);
}

.shop-badge {
    display: inline-block;
    background: #fff;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 0.25rem 0;
    border: 1px solid #e9ecef;
    font-size: 0.9rem;
}
</style>
"""

MONEY_COLUMNS = {
    "Выручка": st.column_config.NumberColumn(format="%d ₽"),
    "Оклад": st.column_config.NumberColumn(format="%d ₽"),
    "Процент": st.column_config.NumberColumn(format="%d ₽"),
    "Штраф": st.column_config.NumberColumn(format="%d ₽"),
    "Итого": st.column_config.NumberColumn(format="%d ₽"),
    "Сумма": st.column_config.NumberColumn(format="%d ₽"),
}

PERIOD_OPTIONS = [
    "Всё время",
    "Текущий месяц",
    "Прошлый месяц",
    "1–15 число (текущий месяц)",
    "16–конец месяца (текущий)",
    "Произвольный период",
]


def parse_work_date(date_str: str) -> date:
    day, month, year = date_str.split(".")
    return date(int(year), int(month), int(day))


def get_history_date_bounds(history: list[dict]) -> tuple[date, date]:
    dates = [parse_work_date(row["Дата"]) for row in history]
    return min(dates), max(dates)


def get_period_bounds(preset: str, today: date, history: list[dict]) -> tuple[date, date]:
    if preset == "Всё время":
        return get_history_date_bounds(history)

    if preset == "Текущий месяц":
        return today.replace(day=1), today

    if preset == "Прошлый месяц":
        first_of_month = today.replace(day=1)
        last_day_prev = first_of_month - timedelta(days=1)
        return last_day_prev.replace(day=1), last_day_prev

    if preset == "1–15 число (текущий месяц)":
        period_end = min(today, date(today.year, today.month, 15))
        return date(today.year, today.month, 1), period_end

    if preset == "16–конец месяца (текущий)":
        last_day = calendar.monthrange(today.year, today.month)[1]
        period_start = date(today.year, today.month, 16)
        if today.day < 16:
            return period_start, period_start - timedelta(days=1)
        period_end = min(today, date(today.year, today.month, last_day))
        return period_start, period_end

    return today, today


def filter_history(
    history: list[dict],
    date_from: date,
    date_to: date,
    employee: str | None = None,
) -> list[dict]:
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    filtered = []
    for row in history:
        row_date = parse_work_date(row["Дата"])
        if date_from <= row_date <= date_to:
            if employee is None or row["Сотрудник"] == employee:
                filtered.append(row)
    return filtered


def aggregate_by_employee(rows: list[dict]) -> list[dict]:
    totals: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"Сумма": 0.0, "Расчётов": 0}
    )
    for row in rows:
        employee = row["Сотрудник"]
        totals[employee]["Сумма"] += row["Итого"]
        totals[employee]["Расчётов"] += 1

    return [
        {
            "Сотрудник": employee,
            "Расчётов": int(data["Расчётов"]),
            "Сумма": round(data["Сумма"], 2),
        }
        for employee, data in sorted(totals.items(), key=lambda item: item[0])
    ]


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
        column_config=MONEY_COLUMNS,
    )


def init_session_state() -> None:
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def render_header() -> None:
    st.markdown(
        """
        <div class="main-header">
            <h1>🌸 Зарплата флористов</h1>
            <p>Калькулятор выплат: оклад + 5% от выручки − штрафы</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


st.set_page_config(
    page_title="Зарплата флористов",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
init_session_state()

employees = get_all_employees()
history = get_all_calculations()

if not employees:
    st.session_state.last_result = None

render_header()

with st.sidebar:
    render_sidebar(employees, len(history))

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

render_analytics(history)



