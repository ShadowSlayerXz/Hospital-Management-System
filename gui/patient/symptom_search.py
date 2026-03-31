# gui/patient/symptom_search.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.symptom_services import suggest_for_symptoms


class SymptomSearch(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Symptom Search",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        tk.Label(self, text="Describe your symptoms:", bg="#ecf0f1", font=("Arial", 11)).pack()
        self.symptom_var = tk.StringVar()
        tk.Entry(self, textvariable=self.symptom_var, width=50,
                 font=("Arial", 11)).pack(pady=5)
        tk.Button(self, text="Search", command=self._search,
                  bg="#2980b9", fg="white", font=("Arial", 11)).pack(pady=5)

        tk.Label(self, text="Suggested Doctors:", bg="#ecf0f1",
                 font=("Arial", 12, "bold")).pack(pady=(15, 5))

        cols = ("Doctor ID", "Doctor Name", "Department", "Experience", "Qualification")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        widths = [80, 180, 160, 100, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Book with Selected Doctor", command=self._book,
                  bg="#27ae60", fg="white", font=("Arial", 11)).pack(pady=8)

    def _search(self):
        text = self.symptom_var.get().strip()
        if not text:
            messagebox.showwarning("Input", "Please describe your symptoms.")
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        suggestions = suggest_for_symptoms(text)
        if not suggestions:
            messagebox.showinfo("No Results", "No departments found for those symptoms. Try browsing departments.")
            return
        for dept_id, dept_name, doctors in suggestions:
            for doc in doctors:
                self.tree.insert("", "end", values=(doc[0], doc[1], dept_name, doc[2], doc[3]))

    def _book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        values = self.tree.item(selected[0])["values"]
        doctor_id, doctor_name = values[0], values[1]
        from gui.patient.book_appointment import BookAppointment
        for w in self.master.winfo_children():
            w.destroy()
        BookAppointment(self.master, self.app, doctor_id, doctor_name).pack(fill="both", expand=True)
