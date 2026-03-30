# gui/doctor/my_reviews.py
import tkinter as tk
from tkinter import ttk
from services.review_services import get_doctor_reviews


class MyReviews(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Reviews",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Patient", "Date", "Rating", "Comment")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [180, 120, 80, 350]
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
        for rev in get_doctor_reviews(self.doctor_id):
            # rev = (review_id, patient_name, appointment_date, rating, comment, created_at)
            stars = "★" * rev[3] + "☆" * (5 - rev[3])
            self.tree.insert("", "end", values=(rev[1], rev[2], stars, rev[4] or ""))
