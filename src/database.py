import sqlite3
from pathlib import Path
from projects.weather_expense_tracker.src.schemas import ExpenseCreate

DB_PATH = Path(__file__).resolve().parent.parent / "expenses.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def insert_expense(expense: ExpenseCreate) -> dict:
    query = """
        INSERT INTO expenses (title, amount, category)
        VALUES (?, ?, ?)
    """
    params = (expense.title, expense.amount, expense.category)

    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        row_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, title, amount, category, created_at FROM expenses WHERE id = ?",
            (row_id,),
        ).fetchone()
        return dict(row)


def list_expenses() -> list[dict]:
    query = "SELECT id, title, amount, category, created_at FROM expenses ORDER BY id DESC"
    with get_db_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]


def get_expense_summary() -> dict:
    with get_db_connection() as conn:
        total_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0.0) as total, COUNT(*) as count FROM expenses"
        ).fetchone()

        category_rows = conn.execute(
            "SELECT category, SUM(amount) as cat_total FROM expenses GROUP BY category"
        ).fetchall()

    return {
        "total_amount": float(total_row["total"]),
        "expense_count": int(total_row["count"]),
        "category_totals": {row["category"]: float(row["cat_total"]) for row in category_rows},
    }