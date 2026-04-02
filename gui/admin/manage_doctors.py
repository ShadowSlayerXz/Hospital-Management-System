# gui/admin/manage_doctors.py
import tkinter as tk
from tkinter import ttk, messagebox

from database.doctor_dao import get_all_doctors, delete_doctor
from database.department_dao import get_all_departments
from services.auth_services import register_doctor


class ManageDoctors(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Manage Doctors",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)

        labels = ["Name:", "Email:", "Password:", "Experience (years):", "Qualification:"]
        self._vars = {}
        keys = ["name", "email", "password", "experience", "qualification"]
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(form, text=lbl, bg="#ecf0f1").grid(row=i, column=0, sticky="e", padx=5, pady=3)
            var = tk.StringVar()
            if key == "experience":
                tk.Spinbox(form, textvariable=var, from_=0, to=50, width=24).grid(row=i, column=1, padx=5)
            else:
                show = "*" if key == "password" else ""
                tk.Entry(form, textvariable=var, width=25, show=show).grid(row=i, column=1, padx=5)
            self._vars[key] = var

        tk.Label(form, text="Department:", bg="#ecf0f1").grid(row=5, column=0, sticky="e", padx=5, pady=3)
        self._dept_var = tk.StringVar()
        self._dept_combo = ttk.Combobox(form, textvariable=self._dept_var, width=23, state="readonly")
        self._dept_combo.grid(row=5, column=1, padx=5)
        self._load_departments()

        tk.Button(form, text="Add Doctor", command=self._add,
                  bg="#27ae60", fg="white").grid(row=6, column=1, pady=10, sticky="e")

        cols = ("ID", "Name", "Department", "Experience", "Qualification")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        widths = [50, 180, 150, 100, 150]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)

        tk.Button(self, text="Delete Selected", command=self._delete,
                  bg="#e74c3c", fg="white").pack(pady=5)

        self._refresh()

    def _load_departments(self):
        depts = get_all_departments()
        self._dept_map = {name: did for did, name in depts}
        self._dept_combo["values"] = list(self._dept_map.keys())

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for doc in get_all_doctors():
            self.tree.insert("", "end", values=doc)

    def _add(self):
        v = {k: var.get().strip() for k, var in self._vars.items()}
        dept_name = self._dept_var.get()

        if not all([v["name"], v["email"], v["password"], dept_name]):
            messagebox.showwarning("Input Error", "Name, email, password, and department are required.")
            return

        dept_id = self._dept_map[dept_name]
        exp = int(v["experience"]) if v["experience"].isdigit() else 0

        success, msg = register_doctor(v["name"], v["email"], v["password"], dept_id, exp, v["qualification"])
        if success:
            messagebox.showinfo("Success", msg)
            for var in self._vars.values():
                var.set("")
            self._dept_var.set("")
            self._refresh()
        else:
            messagebox.showerror("Error", msg)

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a doctor to delete.")
            return
        doctor_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this doctor?"):
            if not delete_doctor(doctor_id):
                messagebox.showerror("Error", "Failed to delete doctor.")
            self._refresh()
