# main.py
from migrations.init_db import initialize_database, seed_admin
from migrations.seed_doctors import seed as seed_doctors
from gui.app import App

if __name__ == "__main__":
    initialize_database()
    seed_admin()
    seed_doctors()

    app = App()
    app.mainloop()
