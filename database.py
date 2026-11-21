import sqlite3
from pathlib import Path

# 資料庫檔案放在跟這支程式同一個資料夾
DB_PATH = Path(__file__).parent / "expenses.db"


def init_db():
    """第一次執行時建立資料表，已經存在就跳過"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            date     TEXT    NOT NULL,
            category TEXT    NOT NULL,
            item     TEXT    NOT NULL,
            amount   INTEGER NOT NULL CHECK (amount > 0)
        )
    """)
    conn.commit()
    conn.close()


def add_expense(date, category, item, amount):
    """新增一筆支出"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO expenses (date, category, item, amount) VALUES (?, ?, ?, ?)",
        (date, category, item, amount),
    )
    conn.commit()
    conn.close()


def get_expense(expense_id):
    """取出單筆支出，找不到回傳 None"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, date, category, item, amount FROM expenses WHERE id = ?",
        (expense_id,),
    ).fetchone()
    conn.close()
    return row


def list_expenses(month=None):
    """取出支出，新的排前面；有給 month（例如 "2026-11"）就只取那個月"""
    conn = sqlite3.connect(DB_PATH)
    if month:
        rows = conn.execute(
            "SELECT id, date, category, item, amount FROM expenses "
            "WHERE date LIKE ? ORDER BY date DESC, id DESC",
            (f"{month}-%",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, date, category, item, amount FROM expenses "
            "ORDER BY date DESC, id DESC"
        ).fetchall()
    conn.close()
    return rows


def get_category_totals(month=None):
    """各分類的總金額，花最多的排前面"""
    conn = sqlite3.connect(DB_PATH)
    if month:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE date LIKE ? GROUP BY category ORDER BY total DESC",
            (f"{month}-%",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "GROUP BY category ORDER BY total DESC"
        ).fetchall()
    conn.close()
    return rows


def update_expense(expense_id, date, category, item, amount):
    """修改一筆支出"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE expenses SET date = ?, category = ?, item = ?, amount = ? WHERE id = ?",
        (date, category, item, amount, expense_id),
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    """刪除指定編號的支出，回傳是否真的有刪到"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted