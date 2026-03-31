# gui/patient/my_records.py
import tkinter as tk
from tkinter import ttk
from services.medical_record_services import get_patient_records


class MyRecords(tk.Frame):
    def __init__(self, master, patient_id):
        super().__init__(master, bg="#ecf0f1")
        self.patient_id = patient_id
        self._build()

    def _build(self):
        tk.Label(self, text="My Medical Records",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        cols = ("Date", "Doctor", "Diagnosis", "Prescription", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        widths = [110, 150, 200, 200, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        tk.Label(self, text="Details:", font=("Arial", 11, "bold"), bg="#ecf0f1").pack(anchor="w", padx=20)
        self.detail_text = tk.Text(self, height=8, font=("Arial", 10), state="disabled")
        self.detail_text.pack(padx=20, pady=5, fill="x")

        tk.Button(self, text="Refresh", command=self._refresh,
                  bg="#2980b9", fg="white").pack(pady=5)
        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self._records = get_patient_records(self.patient_id)
        for rec in self._records:
            # rec = (record_id, doctor_name, date, diagnosis, prescription, notes, created_at)
            self.tree.insert("", "end", values=(
                rec[2], rec[1],
                rec[3][:40] if rec[3] else "",
                rec[4][:40] if rec[4] else "",
                rec[5][:30] if rec[5] else ""
            ))

    def _on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        idx = self.tree.index(selected[0])
        if idx >= len(self._records):
            return
        rec = self._records[idx]
        text = (
            f"Date: {rec[2]}\n"
            f"Doctor: {rec[1]}\n\n"
            f"Diagnosis:\n{rec[3]}\n\n"
            f"Prescription:\n{rec[4] or 'N/A'}\n\n"
            f"Notes:\n{rec[5] or 'N/A'}"
        )
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")
