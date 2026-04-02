# gui/admin/manage_symptoms.py
import tkinter as tk
from tkinter import ttk, messagebox
from database.symptom_dao import get_all_symptom_mappings, add_symptom_mapping, delete_symptom_mapping
from database.department_dao import get_all_departments


class ManageSymptoms(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        tk.Label(self, text="Manage Symptom Mappings",
                 font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack(pady=5)
        tk.Label(form, text="Keyword:", bg="#ecf0f1").grid(row=0, column=0, padx=5)
        self.keyword_var = tk.StringVar()
        tk.Entry(form, textvariable=self.keyword_var, width=20).grid(row=0, column=1, padx=5)
        tk.Label(form, text="Department:", bg="#ecf0f1").grid(row=0, column=2, padx=5)
        self._dept_var = tk.StringVar()
        self._dept_combo = ttk.Combobox(form, textvariable=self._dept_var,
                                         width=20, state="readonly")
        self._dept_combo.grid(row=0, column=3, padx=5)
        tk.Button(form, text="Add", command=self._add,
                  bg="#27ae60", fg="white").grid(row=0, column=4, padx=5)
        self._load_departments()

        cols = ("ID", "Keyword", "Department")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        widths = [60, 200, 200]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

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
        for mapping in get_all_symptom_mappings():
            self.tree.insert("", "end", values=mapping)

    def _add(self):
        keyword = self.keyword_var.get().strip().lower()
        dept_name = self._dept_var.get()
        if not keyword or not dept_name:
            messagebox.showwarning("Input Error", "Keyword and department are required.")
            return
        dept_id = self._dept_map[dept_name]
        if add_symptom_mapping(keyword, dept_id):
            self.keyword_var.set("")
            self._dept_var.set("")
            self._refresh()
        else:
            messagebox.showerror("Error", "Failed to add mapping. Keyword may already exist.")

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a mapping to delete.")
            return
        mapping_id = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this symptom mapping?"):
            if not delete_symptom_mapping(mapping_id):
                messagebox.showerror("Error", "Failed to delete mapping.")
            self._refresh()
