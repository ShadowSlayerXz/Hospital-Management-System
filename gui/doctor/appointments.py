# gui/doctor/appointments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_doctor
from services.billing_services import complete_appointment_and_bill


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

        btn_row = tk.Frame(self, bg="#ecf0f1")
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="Mark as Completed & Generate Bill",
                  command=self._complete_selected,
                  bg="#27ae60", fg="white", font=("Arial", 10)).pack(side="left", padx=10)
        tk.Button(btn_row, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(side="left", padx=10)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_appointments_by_doctor(self.doctor_id):
            self.tree.insert("", "end", values=appt)

    def _complete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a scheduled appointment.")
            return
        values = self.tree.item(selected[0], "values")
        appt_id, _, _, _, status = values
        if status != "scheduled":
            messagebox.showwarning("Invalid", f"Appointment is already '{status}'.")
            return
        ok, msg = complete_appointment_and_bill(int(appt_id))
        if ok:
            messagebox.showinfo("Done", msg)
            self._refresh()
        else:
            messagebox.showerror("Error", msg)
