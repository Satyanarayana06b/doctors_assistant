from db.connection import get_connection

def book_appointment(doctor_id, patient_name, phone, date, time):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN")

        # Insert patient
        cur.execute(
            "INSERT INTO patients (name, phone) VALUES (%s, %s) RETURNING patient_id",
            (patient_name, phone)
        )
        patient_id = cur.fetchone()[0]

        # Insert appointment
        cur.execute("""
            INSERT INTO appointments (doctor_id, patient_id, schedule_date, start_time)
            VALUES (%s, %s, %s, %s)
        """, (doctor_id, patient_id, date, time))

        # Update availability
        cur.execute("""
            UPDATE doctor_schedules
            SET is_available = FALSE
            WHERE doctor_id = %s AND schedule_date = %s AND start_time = %s
        """, (doctor_id, date, time))

        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cur.close()
        conn.close()
