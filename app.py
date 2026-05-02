import oracledb
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import matplotlib.pyplot as plt
import hashlib
import logging
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_SERVICE

# ========== LOGGING SETUP ==========
logging.basicConfig(filename="app.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ========== THICK MODE (Oracle 11g) ==========
oracledb.init_oracle_client(lib_dir=r"C:\instantclient_21_8")   # change path if needed

DSN = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

def get_connection():
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DSN)
    except Exception as e:
        logging.error(str(e))
        messagebox.showerror("Database Error", "Could not connect to database.\nCheck credentials or Oracle service.")
        return None

# ========== GLOBALS ==========
current_user_id = None
current_username = None

# ========== HASH PASSWORD ==========
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

# ========== LOGIN / SIGNUP ==========
def login_screen():
    win = tk.Tk()
    win.title("Personal Finance Manager - Login")
    win.geometry("400x300")

    tk.Label(win, text="Login", font=("Arial", 20)).pack(pady=10)
    frame = tk.Frame(win)
    frame.pack(pady=20)

    tk.Label(frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_entry = tk.Entry(frame, width=25)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_entry = tk.Entry(frame, show="*", width=25)
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    def do_login():
        uname = username_entry.get()
        pwd = hash_password(password_entry.get())
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT user_id, full_name FROM users WHERE username = :1 AND password = :2", (uname, pwd))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            global current_user_id, current_username
            current_user_id = row[0]
            current_username = row[1]
            win.destroy()
            main_app()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_signup():
        win.destroy()
        signup_screen()

    tk.Button(win, text="Login", command=do_login, width=15).pack(pady=5)
    tk.Button(win, text="Sign Up", command=open_signup, width=15).pack(pady=5)
    win.mainloop()

def signup_screen():
    win = tk.Tk()
    win.title("Sign Up")
    win.geometry("400x300")

    tk.Label(win, text="Sign Up", font=("Arial", 20)).pack(pady=10)
    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5)
    name_entry = tk.Entry(frame, width=25)
    name_entry.grid(row=0, column=1)

    tk.Label(frame, text="Username:").grid(row=1, column=0, padx=5, pady=5)
    uname_entry = tk.Entry(frame, width=25)
    uname_entry.grid(row=1, column=1)

    tk.Label(frame, text="Password:").grid(row=2, column=0, padx=5, pady=5)
    pwd_entry = tk.Entry(frame, show="*", width=25)
    pwd_entry.grid(row=2, column=1)

    def do_signup():
        name = name_entry.get()
        uname = uname_entry.get()
        pwd = hash_password(pwd_entry.get())
        if not name or not uname or not pwd:
            messagebox.showerror("Error", "All fields required")
            return
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (full_name, username, password) VALUES (:1, :2, :3)",
                        (name, uname, pwd))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
            win.destroy()
            login_screen()
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", "Username already exists")
        finally:
            cur.close()
            conn.close()

    tk.Button(win, text="Sign Up", command=do_signup, width=15).pack(pady=10)
    tk.Button(win, text="Back to Login", command=lambda: [win.destroy(), login_screen()]).pack()
    win.mainloop()

# ========== MAIN APPLICATION (GUI) – SAME AS BEFORE, ONLY MINOR ERROR HANDLING ADDED ==========
def main_app():
    root = tk.Tk()
    root.title(f"Finance Manager - {current_username}")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')

    summary_frame = tk.LabelFrame(root, text="Monthly Summary", font=("Arial", 12, "bold"), bg='#f0f0f0')
    summary_frame.pack(fill="x", padx=10, pady=5)
    summary_label = tk.Label(summary_frame, text="", font=("Arial", 11), bg='#f0f0f0')
    summary_label.pack(pady=5)

    # Add Transaction Frame
    add_frame = tk.LabelFrame(root, text="Add Transaction", font=("Arial", 12, "bold"), bg='#f0f0f0')
    add_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(add_frame, text="Type:", bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    type_var = tk.StringVar(value="expense")
    type_menu = ttk.Combobox(add_frame, textvariable=type_var, values=["expense", "income"], state="readonly", width=12)
    type_menu.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_frame, text="Category:", bg='#f0f0f0').grid(row=0, column=2, padx=5, pady=5, sticky='w')
    cat_combo = ttk.Combobox(add_frame, width=15)
    cat_combo.grid(row=0, column=3, padx=5, pady=5)

    def update_categories(*args):
        t = type_var.get()
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT cat_name FROM categories WHERE cat_type = :1", (t,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        cat_combo['values'] = [row[0] for row in rows]
        if cat_combo['values']:
            cat_combo.current(0)
    type_var.trace_add('write', lambda *args: update_categories())
    update_categories()

    tk.Label(add_frame, text="Amount (Rs):", bg='#f0f0f0').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    amount_entry = tk.Entry(add_frame, width=15)
    amount_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(add_frame, text="Date:", bg='#f0f0f0').grid(row=1, column=2, padx=5, pady=5, sticky='w')
    date_entry = DateEntry(add_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_entry.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(add_frame, text="Note:", bg='#f0f0f0').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    note_entry = tk.Entry(add_frame, width=50)
    note_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='w')

    def add_transaction():
        ttype = type_var.get()
        cat_name = cat_combo.get()
        amt = amount_entry.get()
        tdate = date_entry.get()
        note = note_entry.get()
        if not amt or not cat_name:
            messagebox.showerror("Error", "Category and Amount required")
            return
        try:
            amt = float(amt)
        except:
            messagebox.showerror("Error", "Amount must be number")
            return
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("SELECT cat_id FROM categories WHERE cat_name = :1 AND cat_type = :2", (cat_name, ttype))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Error", "Category not found")
            cur.close()
            conn.close()
            return
        cat_id = row[0]
        try:
            cur.execute("""
                INSERT INTO transactions (user_id, cat_id, amount, trans_date, note)
                VALUES (:1, :2, :3, TO_DATE(:4, 'MM/DD/YY'), :5)
            """, (current_user_id, cat_id, amt, tdate, note))
            conn.commit()
            messagebox.showinfo("Success", "Transaction added!")
            amount_entry.delete(0, tk.END)
            note_entry.delete(0, tk.END)
            refresh_data()
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    tk.Button(add_frame, text="Add Transaction", command=add_transaction, bg='green', fg='white', width=15).grid(row=3, column=0, columnspan=4, pady=10)

    # Transaction List Frame
    list_frame = tk.LabelFrame(root, text="Recent Transactions", font=("Arial", 12, "bold"), bg='#f0f0f0')
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    columns = ("Date", "Category", "Type", "Amount", "Note")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # Charts
    chart_frame = tk.Frame(root, bg='#f0f0f0')
    chart_frame.pack(fill="x", padx=10, pady=5)

    def show_pie_chart():
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT c.cat_name, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.cat_id = c.cat_id
            WHERE t.user_id = :1 AND c.cat_type = 'expense'
            AND EXTRACT(MONTH FROM t.trans_date) = EXTRACT(MONTH FROM SYSDATE)
            AND EXTRACT(YEAR FROM t.trans_date) = EXTRACT(YEAR FROM SYSDATE)
            GROUP BY c.cat_name
        """, (current_user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            messagebox.showinfo("Info", "No expense data for this month")
            return
        categories = [r[0] for r in rows]
        amounts = [r[1] for r in rows]
        plt.figure(figsize=(6,4))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%')
        plt.title("Expense Breakdown (This Month)")
        plt.show()

    def show_bar_chart():
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT TO_CHAR(trans_date, 'Mon'), 
                   SUM(CASE WHEN c.cat_type='income' THEN t.amount ELSE 0 END),
                   SUM(CASE WHEN c.cat_type='expense' THEN t.amount ELSE 0 END)
            FROM transactions t
            JOIN categories c ON t.cat_id = c.cat_id
            WHERE t.user_id = :1 AND EXTRACT(YEAR FROM trans_date) = EXTRACT(YEAR FROM SYSDATE)
            GROUP BY TO_CHAR(trans_date, 'Mon'), EXTRACT(MONTH FROM trans_date)
            ORDER BY EXTRACT(MONTH FROM trans_date)
        """, (current_user_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            messagebox.showinfo("Info", "No data for this year")
            return
        months = [r[0] for r in rows]
        incomes = [r[1] for r in rows]
        expenses = [r[2] for r in rows]
        plt.figure(figsize=(8,4))
        x = range(len(months))
        plt.bar(x, incomes, width=0.4, label='Income', align='center')
        plt.bar(x, expenses, width=0.4, label='Expense', align='edge')
        plt.xticks(x, months)
        plt.xlabel("Month")
        plt.ylabel("Amount (Rs)")
        plt.title("Monthly Income vs Expense")
        plt.legend()
        plt.show()

    tk.Button(chart_frame, text="📊 Expense Pie Chart", command=show_pie_chart, bg='blue', fg='white', width=20).pack(side="left", padx=5)
    tk.Button(chart_frame, text="📈 Monthly Bar Chart", command=show_bar_chart, bg='purple', fg='white', width=20).pack(side="left", padx=5)

    def refresh_data():
        conn = get_connection()
        if not conn:
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                SUM(CASE WHEN c.cat_type='income' THEN t.amount ELSE 0 END),
                SUM(CASE WHEN c.cat_type='expense' THEN t.amount ELSE 0 END)
            FROM transactions t
            JOIN categories c ON t.cat_id = c.cat_id
            WHERE t.user_id = :1 
            AND EXTRACT(MONTH FROM t.trans_date) = EXTRACT(MONTH FROM SYSDATE)
            AND EXTRACT(YEAR FROM t.trans_date) = EXTRACT(YEAR FROM SYSDATE)
        """, (current_user_id,))
        row = cur.fetchone()
        total_income = row[0] or 0
        total_expense = row[1] or 0
        savings = total_income - total_expense
        summary_label.config(text=f"Income: Rs {total_income:.2f}   |   Expense: Rs {total_expense:.2f}   |   Savings: Rs {savings:.2f}")

        for item in tree.get_children():
            tree.delete(item)
        # Oracle 11g compatible using ROWNUM
        cur.execute("""
            SELECT * FROM (
                SELECT TO_CHAR(t.trans_date, 'DD-Mon-YY'), c.cat_name, c.cat_type, t.amount, t.note
                FROM transactions t
                JOIN categories c ON t.cat_id = c.cat_id
                WHERE t.user_id = :1
                ORDER BY t.trans_date DESC
            ) WHERE ROWNUM <= 20
        """, (current_user_id,))
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)
        cur.close()
        conn.close()

    def logout():
        root.destroy()
        login_screen()

    tk.Button(root, text="Logout", command=logout, bg='red', fg='white', width=10).pack(side="bottom", pady=5)
    refresh_data()
    root.mainloop()

if __name__ == "__main__":
    login_screen()