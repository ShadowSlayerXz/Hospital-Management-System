# gui/admin/all_bills.py
import tkinter as tk
from tkinter import ttk
from database.bill_dao import get_all_bills


class AllBills(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="All Bills",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Bill ID", "Patient", "Doctor", "Date", "Amount (KES)", "Issued At")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        widths = [80, 160, 160, 110, 120, 180]
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
        for bill in get_all_bills():
            self.tree.insert("", "end", values=bill)
