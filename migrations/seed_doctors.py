"""
Seed script: adds 2 doctors per department.
Safe to re-run — skips emails that already exist.
Usage: python migrations/seed_doctors.py
"""

from database.db_connection import get_connection
from services.auth_services import register_doctor

# 2 doctors per department — names, qualifications, experience vary by specialty
DOCTOR_TEMPLATES = [
    {
        "suffix": "1",
        "name_prefix": "Dr. Anil",
        "qualification": "MBBS, MD",
        "experience": 8,
    },
    {
        "suffix": "2",
        "name_prefix": "Dr. Priya",
        "qualification": "MBBS, MS",
        "experience": 5,
    },
]


def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT department_id, department_name FROM department ORDER BY department_id;")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def dept_slug(name):
    """Lowercase, no spaces — used to build a unique email per department."""
    return name.lower().replace(" ", "").replace("/", "")


def seed():
    departments = get_all_departments()
    if not departments:
        print("No departments found. Add departments via the admin panel first.")
        return

    print(f"Found {len(departments)} departments.\n")

    for dept_id, dept_name in departments:
        slug = dept_slug(dept_name)
        for t in DOCTOR_TEMPLATES:
            name = f"{t['name_prefix']} ({dept_name})"
            email = f"doctor.{slug}.{t['suffix']}@hms.com"
            ok, msg = register_doctor(
                name=name,
                email=email,
                password="doctor123",
                department_id=dept_id,
                experience_years=t["experience"],
                qualification=t["qualification"],
            )
            status = "OK" if ok else f"SKIP ({msg})"
            print(f"  [{dept_name}] {email} — {status}")

    print("\nSeeding complete.")


if __name__ == "__main__":
    seed()
