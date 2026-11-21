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


def list_expenses():
    """取出所有支出，新的排前面"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, date, category, item, amount FROM expenses ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()
    return rows


def get_total():
    """計算總支出"""
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
    conn.close()
    return total


def delete_expense(expense_id):
    """刪除指定編號的支出，回傳是否真的有刪到"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted