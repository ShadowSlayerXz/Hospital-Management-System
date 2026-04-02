# gui/login_frame.py
import tkinter as tk
from tkinter import ttk, messagebox

from services.auth_services import login_user, register_patient
from database.patient_dao import get_patient_by_user_id
from database.doctor_dao import get_doctor_by_user_id


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#ecf0f1")
        self._build_login()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _build_login(self):
        self._clear()
        tk.Label(self, text="Hospital Management System",
                 font=("Arial", 22, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=40)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack()

        tk.Label(form, text="Email:", bg="#ecf0f1", font=("Arial", 11)).grid(row=0, column=0, sticky="e", pady=8, padx=10)
        self.email_var = tk.StringVar()
        tk.Entry(form, textvariable=self.email_var, width=30, font=("Arial", 11)).grid(row=0, column=1)

        tk.Label(form, text="Password:", bg="#ecf0f1", font=("Arial", 11)).grid(row=1, column=0, sticky="e", pady=8, padx=10)
        self.pass_var = tk.StringVar()
        tk.Entry(form, textvariable=self.pass_var, show="*", width=30, font=("Arial", 11)).grid(row=1, column=1)

        tk.Button(self, text="Login", command=self._login,
                  bg="#2980b9", fg="white", font=("Arial", 12), width=15).pack(pady=15)
        tk.Button(self, text="New Patient? Register", command=self._build_register,
                  bg="#ecf0f1", font=("Arial", 10)).pack()

    def _login(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please enter email and password.")
            return

        user = login_user(email, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password.")
            return

        user_id, name, _, _, role = user[0], user[1], user[2], user[3], user[4]

        profile_id = None
        if role == "patient":
            patient = get_patient_by_user_id(user_id)
            profile_id = patient[0] if patient else None
        elif role == "doctor":
            doctor = get_doctor_by_user_id(user_id)
            profile_id = doctor[0] if doctor else None

        self.master.current_user = {
            "user_id": user_id,
            "name": name,
            "role": role,
            "profile_id": profile_id,
        }

        if role == "patient":
            from gui.patient.dashboard import PatientDashboard
            self.master.show_frame(PatientDashboard)
        elif role == "doctor":
            from gui.doctor.dashboard import DoctorDashboard
            self.master.show_frame(DoctorDashboard)
        elif role == "admin":
            from gui.admin.dashboard import AdminDashboard
            self.master.show_frame(AdminDashboard)
        else:
            messagebox.showerror("Login Error", "Unknown user role. Please contact admin.")

    def _build_register(self):
        self._clear()
        tk.Label(self, text="Patient Registration",
                 font=("Arial", 18, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=30)

        form = tk.Frame(self, bg="#ecf0f1")
        form.pack()

        fields = [
            ("Full Name:", "name"), ("Email:", "email"), ("Password:", "password"),
            ("Age:", "age"), ("Gender:", "gender"),
            ("Phone:", "phone"), ("Address:", "address"),
        ]
        self._reg_vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form, text=label, bg="#ecf0f1", font=("Arial", 11)).grid(
                row=i, column=0, sticky="e", pady=6, padx=10)
            var = tk.StringVar()
            if key == "gender":
                ttk.Combobox(form, textvariable=var, values=["male", "female", "other"],
                             width=28, font=("Arial", 11), state="readonly").grid(row=i, column=1)
            else:
                show = "*" if key == "password" else ""
                tk.Entry(form, textvariable=var, width=30, font=("Arial", 11), show=show).grid(row=i, column=1)
            self._reg_vars[key] = var

        tk.Button(self, text="Register", command=self._register,
                  bg="#27ae60", fg="white", font=("Arial", 12), width=15).pack(pady=15)
        tk.Button(self, text="Back to Login", command=self._build_login,
                  bg="#ecf0f1", font=("Arial", 10)).pack()

    def _register(self):
        v = {k: var.get().strip() for k, var in self._reg_vars.items()}

        if not all([v["name"], v["email"], v["password"], v["age"], v["gender"]]):
            messagebox.showwarning("Input Error", "Name, email, password, age, and gender are required.")
            return

        try:
            age = int(v["age"])
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return

        success, msg = register_patient(
            v["name"], v["email"], v["password"],
            age, v["gender"], v["phone"], v["address"]
        )

        if success:
            messagebox.showinfo("Success", msg)
            self._build_login()
        else:
            messagebox.showerror("Registration Failed", msg)
