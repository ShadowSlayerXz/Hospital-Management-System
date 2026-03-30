# gui/admin/dashboard.py
import tkinter as tk


class AdminDashboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=f"Admin Dashboard — {self.master.current_user['name']}",
                 fg="white", bg="#2c3e50", font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=15)
        tk.Button(header, text="Logout", command=self.master.logout,
                  bg="#e74c3c", fg="white", font=("Arial", 10)).pack(side="right", padx=20, pady=12)

        body = tk.Frame(self, bg="#ecf0f1")
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg="#34495e", width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg="#ecf0f1")
        self.content.pack(side="left", fill="both", expand=True)

        nav = [
            ("Manage Departments", self._show_departments),
            ("Manage Doctors", self._show_doctors),
            ("All Appointments", self._show_appointments),
            ("All Users", self._show_users),
        ]
        for label, cmd in nav:
            tk.Button(sidebar, text=label, command=cmd, width=22,
                      bg="#3d566e", fg="white", font=("Arial", 10),
                      relief="flat", pady=10).pack(fill="x", padx=5, pady=3)

        self._show_departments()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_departments(self):
        self._clear_content()
        from gui.admin.manage_departments import ManageDepartments
        ManageDepartments(self.content).pack(fill="both", expand=True)

    def _show_doctors(self):
        self._clear_content()
        from gui.admin.manage_doctors import ManageDoctors
        ManageDoctors(self.content).pack(fill="both", expand=True)

    def _show_appointments(self):
        self._clear_content()
        from gui.admin.all_appointments import AllAppointments
        AllAppointments(self.content).pack(fill="both", expand=True)

    def _show_users(self):
        self._clear_content()
        from gui.admin.all_users import AllUsers
        AllUsers(self.content).pack(fill="both", expand=True)
