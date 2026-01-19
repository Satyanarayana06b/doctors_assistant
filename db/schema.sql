CREATE TABLE doctors(
    doctor_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL
)

CREATE TABLE doctor_schedules(
    schedule_id SERIAL PRIMARY KEY,
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(doctor_id, schedule_date, start_time)
)

CREATE TABLE patients(
    patient_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT
)

CREATE TABLE appointments(
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(doctor_id, schedule_date, start_time)
)

CREATE INDEX idx_doctors_specialty ON doctors(specialty);
CREATE INDEX idx_schedules_doctor_date ON doctor_schedules(doctor_id, schedule_date);