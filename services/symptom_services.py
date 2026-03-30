# services/symptom_services.py
from database.symptom_dao import get_departments_by_symptom
from database.doctor_dao import get_doctors_by_department


def suggest_for_symptoms(symptom_text):
    keywords = symptom_text.lower().split()
    seen_departments = {}

    for kw in keywords:
        results = get_departments_by_symptom(kw)
        for dept_id, dept_name in results:
            if dept_id not in seen_departments:
                seen_departments[dept_id] = dept_name

    suggestions = []
    for dept_id, dept_name in seen_departments.items():
        doctors = get_doctors_by_department(dept_id)
        suggestions.append((dept_id, dept_name, doctors))

    return suggestions
