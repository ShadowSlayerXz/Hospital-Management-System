# gui/admin/all_users.py
import tkinter as tk
from tkinter import ttk
from database.db_connection import get_connection


def _get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, user_name, user_email, user_role FROM users ORDER BY user_role, user_name;")
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching users:", e)
        return []
    finally:
        cursor.close()
        conn.close()


class AllUsers(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="All Users",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Name", "Email", "Role")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 200, 250, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for user in _get_all_users():
            self.tree.insert("", "end", values=user)
