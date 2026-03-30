# gui/doctor/dashboard.py
import tkinter as tk


class DoctorDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#1a5276", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Doctor Dashboard — Dr. {self.master.current_user['name']}",
                 fg="white", bg="#1a5276", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#1f618d", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("My Appointments", self._show_appointments),
            ("Write Medical Record", self._show_write_record),
            ("Patient History", self._show_patient_history),
            ("My Reviews", self._show_reviews),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=22,
                      bg="#2471a3", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_appointments()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_appointments(self):
        self._clear_content()
        from gui.doctor.appointments import DoctorAppointments
        DoctorAppointments(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_write_record(self):
        self._clear_content()
        from gui.doctor.write_record import WriteRecord
        WriteRecord(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)

    def _show_patient_history(self):
        self._clear_content()
        from gui.doctor.patient_history import PatientHistory
        PatientHistory(self.content).pack(fill="both", expand=True)

    def _show_reviews(self):
        self._clear_content()
        from gui.doctor.my_reviews import MyReviews
        MyReviews(self.content, self.master.current_user["profile_id"]).pack(fill="both", expand=True)
