# gui/admin/manage_departments.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.department_dao import get_all_departments, create_department, delete_department


class ManageDepartments(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Manage Departments",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)
        tk.Label(form, text="Department Name:", bg="#ecf0f1").grid(row=0, column=0, padx=5)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5)
        tk.Button(form, text="Add", command=self._add,
                  bg="#27ae60", fg="white").grid(row=0, column=2, padx=5)

        cols = ("ID", "Name")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=200)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Button(self, text="Delete Selected", command=self._delete,
                  bg="#e74c3c", fg="white").pack(pady=5)

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for dept in get_all_departments():
            self.tree.insert("", "end", values=dept)

    def _add(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Enter a department name.")
            return
        if create_department(name):
            self.name_var.set("")
            self._refresh()
        else:
            messagebox.showerror("Error", "Failed to add department.")

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a department to delete.")
            return
        dept_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this department?"):
            delete_department(dept_id)
            self._refresh()
