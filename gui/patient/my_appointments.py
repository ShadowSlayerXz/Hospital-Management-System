# gui/patient/my_appointments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_patient, cancel_appointment


class MyAppointments(tk.Frame):
    def __init__(self, master, patient_id):
        super().__init__(master, bg="#ecf0f1")
        self.patient_id = patient_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Doctor", "Department", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        widths = [60, 180, 150, 120, 80, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel Selected", command=self._cancel,
                  bg="#e74c3c", fg="white").pack(side="left", padx=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_appointments_by_patient(self.patient_id):
            self.tree.insert("", "end", values=appt)

    def _cancel(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment to cancel.")
            return
        values = self.tree.item(selected[0])["values"]
        appt_id, status = values[0], values[5]
        if status != "scheduled":
            messagebox.showinfo("Info", "Only scheduled appointments can be cancelled.")
            return
        if messagebox.askyesno("Confirm", "Cancel this appointment?"):
            if cancel_appointment(appt_id):
                self._refresh()
            else:
                messagebox.showerror("Error", "Failed to cancel appointment.")
