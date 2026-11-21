from datetime import date

import database


def ask_text(prompt):
    """一直問，直到使用者有輸入東西為止"""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("不能空白，請再輸入一次")


def ask_positive_int(prompt):
    """一直問，直到使用者輸入大於 0 的整數為止"""
    while True:
        text = input(prompt).strip()
        try:
            number = int(text)
        except ValueError:
            print("請輸入整數數字")
            continue
        if number <= 0:
            print("要大於 0")
            continue
        return number


def add():
    item = ask_text("品項：")
    category = input("分類（直接按 Enter 為「其他」）：").strip() or "其他"
    amount = ask_positive_int("金額：")
    today = date.today().isoformat()

    database.add_expense(today, category, item, amount)
    print(f"已記錄：{today}　[{category}]　{item}　{amount} 元")


def show():
    rows = database.list_expenses()
    if not rows:
        print("目前還沒有任何紀錄")
        return

    print("編號 | 日期       | 分類 | 品項 | 金額")
    print("-" * 40)
    for expense_id, day, category, item, amount in rows:
        print(f"{expense_id:>4} | {day} | {category} | {item} | {amount} 元")
    print("-" * 40)
    print(f"總支出：{database.get_total()} 元")


def delete():
    show()
    expense_id = ask_positive_int("要刪除的編號：")
    if database.delete_expense(expense_id):
        print(f"已刪除第 {expense_id} 筆")
    else:
        print(f"找不到第 {expense_id} 筆")


def main():
    database.init_db()

    while True:
        print("\n===== 記帳程式 =====")
        print("1. 新增一筆")
        print("2. 查看全部")
        print("3. 刪除一筆")
        print("0. 離開")
        choice = input("請選擇：").strip()

        if choice == "1":
            add()
        elif choice == "2":
            show()
        elif choice == "3":
            delete()
        elif choice == "0":
            print("掰掰！")
            break
        else:
            print("沒有這個選項，請輸入 0～3")


if __name__ == "__main__":
    main()