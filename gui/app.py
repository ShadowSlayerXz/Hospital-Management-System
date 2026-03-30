# gui/app.py
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.current_user = None
        self._current_frame = None

        from gui.login_frame import LoginFrame
        self.show_frame(LoginFrame)

    def show_frame(self, frame_class, **kwargs):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame_class(self, **kwargs)
        self._current_frame.pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        from gui.login_frame import LoginFrame
        self.show_frame(LoginFrame)
