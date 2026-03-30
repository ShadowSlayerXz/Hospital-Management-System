# gui/doctor/write_record.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_doctor
from services.medical_record_services import add_record


class WriteRecord(tk.Frame):
    def __init__(self, master, doctor_id):
        super().__init__(master, bg="#ecf0f1")
        self.doctor_id = doctor_id
        self._build()

    def _build(self):
        tk.Label(self, text="Write Medical Record",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Select Appointment:", bg="#ecf0f1", font=("Arial", 11)).pack()
        self._appt_var = tk.StringVar()
        self._appt_combo = ttk.Combobox(self, textvariable=self._appt_var,
                                         width=55, state="readonly", font=("Arial", 10))
        self._appt_combo.pack(pady=5)
        self._load_appointments()

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=10)

        tk.Label(form, text="Diagnosis:", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=0, column=0, sticky="nw", padx=10, pady=5)
        self.diagnosis_text = tk.Text(form, width=45, height=4, font=("Arial", 10))
        self.diagnosis_text.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form, text="Prescription:", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=1, column=0, sticky="nw", padx=10, pady=5)
        self.prescription_text = tk.Text(form, width=45, height=4, font=("Arial", 10))
        self.prescription_text.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form, text="Notes (optional):", bg="#ecf0f1", font=("Arial", 11)).grid(
            row=2, column=0, sticky="nw", padx=10, pady=5)
        self.notes_text = tk.Text(form, width=45, height=3, font=("Arial", 10))
        self.notes_text.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self, text="Save Record", command=self._save,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=10)

    def _load_appointments(self):
        appts = get_appointments_by_doctor(self.doctor_id)
        self._appt_map = {}
        choices = []
        for appt in appts:
            appt_id, patient, date, time, status = appt
            label = f"[{appt_id}] {patient} — {date} {time} ({status})"
            choices.append(label)
            self._appt_map[label] = appt_id
        self._appt_combo["values"] = choices

    def _save(self):
        label = self._appt_var.get()
        if not label:
            messagebox.showwarning("Select", "Please select an appointment.")
            return
        appt_id = self._appt_map[label]
        diagnosis = self.diagnosis_text.get("1.0", "end").strip()
        prescription = self.prescription_text.get("1.0", "end").strip()
        notes = self.notes_text.get("1.0", "end").strip()

        if not diagnosis:
            messagebox.showwarning("Input Error", "Diagnosis is required.")
            return

        success, msg = add_record(appt_id, diagnosis, prescription, notes)
        if success:
            messagebox.showinfo("Saved", msg)
            self.diagnosis_text.delete("1.0", "end")
            self.prescription_text.delete("1.0", "end")
            self.notes_text.delete("1.0", "end")
            self._appt_var.set("")
        else:
            messagebox.showerror("Error", msg)
