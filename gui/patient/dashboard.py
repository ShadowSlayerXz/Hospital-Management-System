# gui/patient/dashboard.py
import tkinter as tk


class PatientDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#117a65", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Patient Dashboard — {self.master.current_user['name']}",
                 fg="white", bg="#117a65", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#148f77", width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("Browse Departments", self._show_browse),
            ("Symptom Search", self._show_symptom),
            ("My Appointments", self._show_appointments),
            ("My Medical Records", self._show_records),
            ("My Bills", self._show_bills),
            ("Review Doctor", self._show_review),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=24,
                      bg="#17a589", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_browse()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_browse(self):
        self._clear_content()
        from gui.patient.browse_departments import BrowseDepartments
        BrowseDepartments(self.content, self.master).pack(fill="both", expand=True)

    def _show_symptom(self):
        self._clear_content()
        from gui.patient.symptom_search import SymptomSearch
        SymptomSearch(self.content, self.master).pack(fill="both", expand=True)

    def _show_appointments(self):
        self._clear_content()
        from gui.patient.my_appointments import MyAppointments
        MyAppointments(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_records(self):
        self._clear_content()
        from gui.patient.my_records import MyRecords
        MyRecords(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_bills(self):
        self._clear_content()
        from gui.patient.my_bills import MyBills
        MyBills(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_review(self):
        self._clear_content()
        from gui.patient.review_doctor import ReviewDoctor
        ReviewDoctor(self.content, self.master.current_user).pack(fill="both", expand=True)
