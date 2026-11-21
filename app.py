from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for

import database

app = Flask(__name__)
# flash 訊息需要 secret_key；這是本機自己用的小程式，固定字串就好
app.secret_key = "expense-tracker-local"

database.init_db()


# ---------- 表單檢查工具 ----------

def parse_month(text):
    """把 YYYY-MM 轉成標準格式，格式不對就回傳本月"""
    try:
        return datetime.strptime(text, "%Y-%m").strftime("%Y-%m")
    except (TypeError, ValueError):
        return date.today().strftime("%Y-%m")


def read_expense_form(form):
    """從表單讀出日期、分類、品項、金額；有錯回傳 (None, 錯誤訊息)"""
    try:
        day = date.fromisoformat(form.get("date", "").strip()).isoformat()
    except ValueError:
        return None, "日期格式要像 2026-11-21"

    item = form.get("item", "").strip()
    if not item:
        return None, "品項不能空白"

    category = form.get("category", "").strip() or "其他"

    try:
        amount = int(form.get("amount", "").strip())
    except ValueError:
        return None, "金額要是整數"
    if amount <= 0:
        return None, "金額要大於 0"

    return (day, category, item, amount), None


# ---------- 頁面 ----------

@app.route("/")
def index():
    month = parse_month(request.args.get("month"))
    rows = database.list_expenses(month)
    totals = database.get_category_totals(month)
    grand_total = sum(total for _, total in totals)
    return render_template(
        "index.html",
        month=month,
        rows=rows,
        totals=totals,
        grand_total=grand_total,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add():
    data, error = read_expense_form(request.form)
    if error:
        flash(error, "error")
    else:
        database.add_expense(*data)
        day, category, item, amount = data
        flash(f"已記錄：{day} [{category}] {item} {amount} 元", "success")
        # 新增完跳到那筆資料所在的月份
        return redirect(url_for("index", month=day[:7]))
    return redirect(url_for("index"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    row = database.get_expense(expense_id)
    if row is None:
        flash(f"找不到第 {expense_id} 筆", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        data, error = read_expense_form(request.form)
        if error:
            flash(error, "error")
            return render_template("edit.html", row=row, form=request.form)
        database.update_expense(expense_id, *data)
        flash(f"已更新第 {expense_id} 筆", "success")
        return redirect(url_for("index", month=data[0][:7]))

    return render_template("edit.html", row=row, form=None)


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    row = database.get_expense(expense_id)
    if row and database.delete_expense(expense_id):
        flash(f"已刪除「{row[1]} {row[3]} {row[4]} 元」", "success")
        return redirect(url_for("index", month=row[1][:7]))
    flash(f"找不到第 {expense_id} 筆", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
