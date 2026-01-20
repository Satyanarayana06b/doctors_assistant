from db.connection import get_connection

def is_slot_available(doctor_id, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT is_available
        FROM doctor_schedules
        WHERE doctor_id = %s
          AND schedule_date = %s
          AND start_time = %s
    """, (doctor_id, date, time))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None and row[0] is True

def get_available_slots(doctor_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT schedule_date, start_time, end_time
        FROM doctor_schedules
        WHERE doctor_id = %s
          AND is_available = TRUE
        ORDER BY schedule_date, start_time
    """, (doctor_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows