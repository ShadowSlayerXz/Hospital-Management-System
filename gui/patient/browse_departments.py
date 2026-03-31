# gui/patient/browse_departments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.department_dao import get_all_departments
from database.doctor_dao import get_doctors_by_department


class BrowseDepartments(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg="#ecf0f1")
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="Browse Departments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        top = tk.Frame(self, bg="#ecf0f1")
        top.pack(fill="both", expand=True, padx=20)

        left = tk.Frame(top, bg="#ecf0f1")
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="Departments", font=("Arial", 12, "bold"), bg="#ecf0f1").pack()
        self.dept_list = tk.Listbox(left, font=("Arial", 11), height=20, selectmode="single")
        self.dept_list.pack(fill="both", expand=True)
        self.dept_list.bind("<<ListboxSelect>>", self._on_dept_select)

        right = tk.Frame(top, bg="#ecf0f1")
        right.pack(side="left", fill="both", expand=True, padx=20)
        tk.Label(right, text="Doctors in Department", font=("Arial", 12, "bold"), bg="#ecf0f1").pack()
        cols = ("ID", "Name", "Experience", "Qualification")
        self.doctor_tree = ttk.Treeview(right, columns=cols, show="headings", height=15)
        widths = [50, 180, 100, 150]
        for c, w in zip(cols, widths):
            self.doctor_tree.heading(c, text=c)
            self.doctor_tree.column(c, width=w)
        self.doctor_tree.pack(fill="both", expand=True)

        tk.Button(self, text="Book Appointment with Selected Doctor",
                  command=self._book, bg="#27ae60", fg="white",
                  font=("Arial", 11)).pack(pady=10)

        self._load_departments()

    def _load_departments(self):
        self._dept_map = {}
        for dept_id, dept_name in get_all_departments():
            self.dept_list.insert("end", dept_name)
            self._dept_map[dept_name] = dept_id

    def _on_dept_select(self, event):
        selection = self.dept_list.curselection()
        if not selection:
            return
        dept_name = self.dept_list.get(selection[0])
        dept_id = self._dept_map[dept_name]
        for row in self.doctor_tree.get_children():
            self.doctor_tree.delete(row)
        for doc in get_doctors_by_department(dept_id):
            self.doctor_tree.insert("", "end", values=doc)

    def _book(self):
        selected = self.doctor_tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a doctor first.")
            return
        doctor_id = self.doctor_tree.item(selected[0])["values"][0]
        doctor_name = self.doctor_tree.item(selected[0])["values"][1]
        from gui.patient.book_appointment import BookAppointment
        for w in self.master.winfo_children():
            w.destroy()
        BookAppointment(self.master, self.app, doctor_id, doctor_name).pack(fill="both", expand=True)
