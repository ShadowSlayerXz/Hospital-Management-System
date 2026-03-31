# gui/patient/review_doctor.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.appointment_dao import get_appointments_by_patient
from database.review_dao import get_review_by_appointment
from database.db_connection import get_connection
from services.review_services import submit_review


class ReviewDoctor(tk.Frame):
    def __init__(self, master, current_user):
        super().__init__(master, bg="#ecf0f1")
        self.current_user = current_user
        self._build()

    def _build(self):
        tk.Label(self, text="Review Doctor",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Select a completed appointment to review:",
                 bg="#ecf0f1", font=("Arial", 11)).pack()
        self._appt_var = tk.StringVar()
        self._appt_combo = ttk.Combobox(self, textvariable=self._appt_var,
                                         width=60, state="readonly", font=("Arial", 10))
        self._appt_combo.pack(pady=5)
        self._appt_map = {}
        self._load_appointments()

        tk.Label(self, text="Rating (1–5 stars):", bg="#ecf0f1", font=("Arial", 11)).pack(pady=(15, 2))
        self._rating_var = tk.IntVar(value=5)
        star_frame = tk.Frame(self, bg="#ecf0f1")
        star_frame.pack()
        for i in range(1, 6):
            tk.Radiobutton(star_frame, text=f"{'★' * i}", variable=self._rating_var,
                           value=i, bg="#ecf0f1", font=("Arial", 13)).pack(side="left", padx=5)

        tk.Label(self, text="Comment (optional):", bg="#ecf0f1", font=("Arial", 11)).pack(pady=(15, 2))
        self.comment_text = tk.Text(self, width=60, height=4, font=("Arial", 10))
        self.comment_text.pack(pady=5)

        tk.Button(self, text="Submit Review", command=self._submit,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=10)

    def _load_appointments(self):
        patient_id = self.current_user["profile_id"]
        all_appts = get_appointments_by_patient(patient_id)
        choices = []
        for appt in all_appts:
            appt_id, doctor_name, dept, date, time, status = appt
            if status != "completed":
                continue
            if get_review_by_appointment(appt_id):
                continue
            label = f"[{appt_id}] Dr. {doctor_name} — {date} ({dept})"
            choices.append(label)
            self._appt_map[label] = appt
        self._appt_combo["values"] = choices
        if not choices:
            tk.Label(self, text="No completed appointments available to review.",
                     bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 10)).pack()

    def _get_doctor_id(self, appointment_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT doctor_id FROM appointment WHERE appointment_id = %s;", (appointment_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            conn.close()

    def _submit(self):
        label = self._appt_var.get()
        if not label:
            messagebox.showwarning("Select", "Please select an appointment.")
            return
        appt = self._appt_map[label]
        appt_id = appt[0]
        rating = self._rating_var.get()
        comment = self.comment_text.get("1.0", "end").strip() or None

        patient_id = self.current_user["profile_id"]
        doctor_id = self._get_doctor_id(appt_id)
        if not doctor_id:
            messagebox.showerror("Error", "Could not find doctor for this appointment.")
            return

        success, msg = submit_review(appt_id, patient_id, doctor_id, rating, comment)
        if success:
            messagebox.showinfo("Thank You", msg)
            self.comment_text.delete("1.0", "end")
            self._appt_var.set("")
            self._appt_map = {}
            self._load_appointments()
        else:
            messagebox.showerror("Error", msg)
