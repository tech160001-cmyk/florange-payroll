import calendar
from collections import defaultdict
from datetime import date, timedelta

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
