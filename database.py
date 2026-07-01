import sqlite3
from pathlib import Path
from typing import Literal

DB_PATH = Path(__file__).parent / "payroll.db"

AddEmployeeResult = Literal["ok", "empty", "duplicate"]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payroll_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_date TEXT NOT NULL,
                employee TEXT NOT NULL,
                shop TEXT NOT NULL,
                revenue REAL NOT NULL,
                base_salary REAL NOT NULL,
                percent REAL NOT NULL,
                fine REAL NOT NULL,
                total REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()


def save_calculation(
    work_date: str,
    employee: str,
    shop: str,
    revenue: float,
    base_salary: float,
    percent: float,
    fine: float,
    total: float,
) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO payroll_history
                (work_date, employee, shop, revenue, base_salary, percent, fine, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (work_date, employee, shop, revenue, base_salary, percent, fine, total),
        )
        conn.commit()


def get_all_calculations() -> list[dict]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT work_date, employee, shop, revenue, base_salary, percent, fine, total
            FROM payroll_history
            ORDER BY created_at DESC
            """
        ).fetchall()
    return [
        {
            "Дата": row["work_date"],
            "Сотрудник": row["employee"],
            "Магазин": row["shop"],
            "Выручка": row["revenue"],
            "Оклад": row["base_salary"],
            "Процент": row["percent"],
            "Штраф": row["fine"],
            "Итого": row["total"],
        }
        for row in rows
    ]


def clear_history() -> None:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM payroll_history")
        conn.commit()


def get_all_employees() -> list[dict]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name FROM employees ORDER BY name"
        ).fetchall()
    return [{"id": row["id"], "name": row["name"]} for row in rows]


def add_employee(name: str) -> AddEmployeeResult:
    cleaned_name = name.strip()
    if not cleaned_name:
        return "empty"

    init_db()
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO employees (name) VALUES (?)", (cleaned_name,))
            conn.commit()
    except sqlite3.IntegrityError:
        return "duplicate"
    return "ok"


def delete_employee(employee_id: int) -> bool:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
    return cursor.rowcount > 0
