# gui/admin/all_appointments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_all_appointments
from services.billing_services import complete_appointment_and_bill


class AllAppointments(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="All Appointments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("ID", "Patient", "Doctor", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=18)
        widths = [50, 160, 160, 110, 80, 100]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Mark as Completed", command=self._complete,
                  bg="#27ae60", fg="white", font=("Arial", 11)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white", font=("Arial", 11)).pack(side="left")

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for appt in get_all_appointments():
            self.tree.insert("", "end", values=appt)

    def _complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select an appointment to complete.")
            return
        values = self.tree.item(selected[0])["values"]
        appt_id = values[0]
        status = values[5]
        if status == "completed":
            messagebox.showinfo("Info", "This appointment is already completed.")
            return
        if messagebox.askyesno("Confirm", "Mark as completed and generate bill?"):
            success, msg = complete_appointment_and_bill(appt_id)
            if success:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
            self._refresh()
