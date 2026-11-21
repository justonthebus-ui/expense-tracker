from datetime import date, datetime

import database


# ---------- 輸入工具 ----------

def ask_text(prompt, default=None):
    """問一段文字；有預設值時直接按 Enter 就用預設值"""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        if default is not None:
            return default
        print("不能空白，請再輸入一次")


def ask_positive_int(prompt, default=None):
    """問一個大於 0 的整數；有預設值時直接按 Enter 就用預設值"""
    while True:
        text = input(prompt).strip()
        if not text and default is not None:
            return default
        try:
            number = int(text)
        except ValueError:
            print("請輸入整數數字")
            continue
        if number <= 0:
            print("要大於 0")
            continue
        return number


def ask_date(prompt, default):
    """問日期（YYYY-MM-DD）；直接按 Enter 就用預設值"""
    while True:
        text = input(prompt).strip()
        if not text:
            return default
        try:
            return date.fromisoformat(text).isoformat()
        except ValueError:
            print("日期格式要像 2026-11-21")


def ask_month(prompt):
    """問月份（YYYY-MM）；直接按 Enter 代表這個月"""
    while True:
        text = input(prompt).strip()
        if not text:
            return date.today().strftime("%Y-%m")
        try:
            return datetime.strptime(text, "%Y-%m").strftime("%Y-%m")
        except ValueError:
            print("月份格式要像 2026-11")


# ---------- 顯示工具 ----------

def print_rows(rows):
    """把支出列表印成表格，並印出合計"""
    if not rows:
        print("沒有符合的紀錄")
        return
    print("編號 | 日期       | 分類 | 品項 | 金額")
    print("-" * 40)
    for expense_id, day, category, item, amount in rows:
        print(f"{expense_id:>4} | {day} | {category} | {item} | {amount} 元")
    print("-" * 40)
    total = sum(row[4] for row in rows)
    print(f"共 {len(rows)} 筆，合計 {total} 元")


# ---------- 選單功能 ----------

def add():
    today = date.today().isoformat()
    day = ask_date(f"日期（Enter = 今天 {today}）：", today)
    item = ask_text("品項：")
    category = ask_text("分類（Enter = 其他）：", "其他")
    amount = ask_positive_int("金額：")

    database.add_expense(day, category, item, amount)
    print(f"已記錄：{day}　[{category}]　{item}　{amount} 元")


def show_all():
    print_rows(database.list_expenses())


def show_month():
    month = ask_month("要看哪個月？（YYYY-MM，Enter = 本月）：")
    print(f"\n【{month}】")
    print_rows(database.list_expenses(month))


def show_category_totals():
    month = ask_month("統計哪個月？（YYYY-MM，Enter = 本月）：")
    rows = database.get_category_totals(month)
    if not rows:
        print("這個月沒有紀錄")
        return

    grand_total = sum(total for _, total in rows)
    print(f"\n【{month} 分類統計】")
    for category, total in rows:
        percent = total / grand_total * 100
        print(f"{category}：{total} 元（{percent:.1f}%）")
    print(f"總計：{grand_total} 元")


def edit():
    expense_id = ask_positive_int("要修改的編號：")
    row = database.get_expense(expense_id)
    if row is None:
        print(f"找不到第 {expense_id} 筆")
        return

    _, old_date, old_category, old_item, old_amount = row
    print("直接按 Enter 代表不修改")
    day = ask_date(f"日期（{old_date}）：", old_date)
    item = ask_text(f"品項（{old_item}）：", old_item)
    category = ask_text(f"分類（{old_category}）：", old_category)
    amount = ask_positive_int(f"金額（{old_amount}）：", old_amount)

    database.update_expense(expense_id, day, category, item, amount)
    print(f"已更新第 {expense_id} 筆")


def delete():
    expense_id = ask_positive_int("要刪除的編號：")
    row = database.get_expense(expense_id)
    if row is None:
        print(f"找不到第 {expense_id} 筆")
        return

    _, day, category, item, amount = row
    confirm = input(f"確定刪除「{day} {item} {amount} 元」？(y/n)：").strip().lower()
    if confirm == "y":
        database.delete_expense(expense_id)
        print(f"已刪除第 {expense_id} 筆")
    else:
        print("已取消")


# ---------- 主程式 ----------

MENU = {
    "1": ("新增一筆", add),
    "2": ("查看全部", show_all),
    "3": ("查看某個月", show_month),
    "4": ("分類統計", show_category_totals),
    "5": ("修改一筆", edit),
    "6": ("刪除一筆", delete),
}


def main():
    database.init_db()

    while True:
        print("\n===== 記帳程式 =====")
        for key, (label, _) in MENU.items():
            print(f"{key}. {label}")
        print("0. 離開")
        choice = input("請選擇：").strip()

        if choice == "0":
            print("掰掰！")
            break
        elif choice in MENU:
            _, action = MENU[choice]
            action()
        else:
            print("沒有這個選項，請重新輸入")


if __name__ == "__main__":
    main()