# gui/admin/all_users.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.user_dao import get_all_users


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
        users = get_all_users()
        if users is None:
            messagebox.showerror("Error", "Failed to load users.")
            return
        for user in users:
            self.tree.insert("", "end", values=user)
