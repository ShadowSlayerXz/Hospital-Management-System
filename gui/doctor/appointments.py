# gui/doctor/appointments.py
import tkinter as tk
from tkinter import ttk
from database.appointment_dao import get_appointments_by_doctor


class DoctorAppointments(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Patient", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 200, 120, 80, 100]
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
        for appt in get_appointments_by_doctor(self.doctor_id):
            self.tree.insert("", "end", values=appt)
