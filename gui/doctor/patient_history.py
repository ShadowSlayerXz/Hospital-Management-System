# gui/doctor/patient_history.py
import tkinter as tk
from tkinter import ttk
from database.patient_dao import get_all_patients
from services.medical_record_services import get_patient_records


class PatientHistory(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Patient History",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        search_frame = tk.Frame(self, bg="#ecf0f1")
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Select Patient:", bg="#ecf0f1").pack(side="left", padx=5)
        self._patient_var = tk.StringVar()
        self._patient_combo = ttk.Combobox(search_frame, textvariable=self._patient_var,
                                            width=35, state="readonly")
        self._patient_combo.pack(side="left", padx=5)
        tk.Button(search_frame, text="View History", command=self._view,
                  bg="#2980b9", fg="white").pack(side="left", padx=5)

        patients = get_all_patients()
        self._patient_map = {f"[{p[0]}] {p[1]}": p[0] for p in patients}
        self._patient_combo["values"] = list(self._patient_map.keys())

        cols = ("Date", "Doctor", "Diagnosis", "Prescription", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        widths = [110, 150, 200, 200, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

    def _view(self):
        label = self._patient_var.get()
        if not label:
            return
        patient_id = self._patient_map[label]
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in get_patient_records(patient_id):
            # rec = (record_id, doctor_name, date, diagnosis, prescription, notes, created_at)
            self.tree.insert("", "end", values=(rec[2], rec[1], rec[3], rec[4], rec[5]))
