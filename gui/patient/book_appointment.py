# gui/patient/book_appointment.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from services.appointment_services import book_appointment

TIME_SLOTS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
]


class BookAppointment(tk.Frame):
    def __init__(self, master, app, doctor_id, doctor_name):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self.doctor_id = doctor_id
        self.doctor_name = doctor_name
        self._build()

    def _build(self):
        tk.Label(self, text="Book Appointment",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        tk.Label(self, text=f"Doctor: {self.doctor_name}",
                 font=("Arial", 12), bg="#ecf0f1", fg="#2c3e50").pack(pady=5)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=20)

        tk.Label(form, text="Select Date:", bg="#ecf0f1",
                 font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.date_entry = DateEntry(form, width=18, font=("Arial", 11),
                                    date_pattern="yyyy-mm-dd")
        self.date_entry.grid(row=0, column=1, padx=10)

        tk.Label(form, text="Select Time:", bg="#ecf0f1",
                 font=("Arial", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.time_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.time_var, values=TIME_SLOTS,
                     width=18, font=("Arial", 11), state="readonly").grid(row=1, column=1, padx=10)

        tk.Button(self, text="Confirm Booking", command=self._book,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=18).pack(pady=15)
        tk.Button(self, text="Back", command=self._back,
                  bg="#95a5a6", fg="white", font=("Arial", 10)).pack()

    def _book(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        time = self.time_var.get()
        if not time:
            messagebox.showwarning("Select Time", "Please select a time slot.")
            return

        patient_id = self.app.current_user["profile_id"]
        success, msg = book_appointment(patient_id, self.doctor_id, date, time)
        if success:
            messagebox.showinfo("Booking Confirmed", msg)
            self._back()
        else:
            messagebox.showerror("Booking Failed", msg)

    def _back(self):
        for w in self.master.winfo_children():
            w.destroy()
        from gui.patient.browse_departments import BrowseDepartments
        BrowseDepartments(self.master, self.app).pack(fill="both", expand=True)
