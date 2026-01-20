from db.connection import get_connection

def get_doctors_by_speciality(speciality: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, name, specialty FROM doctors WHERE specialty = %s", (speciality,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows