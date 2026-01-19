INSERT INTO doctors (name, specialty) VALUES
('Dr X', 'Orthopedics'),
('Dr Y', 'Orthopedics'),
('Dr A', 'Dermatology');

-- Dr X tomorrow
INSERT INTO doctor_schedules (doctor_id, schedule_date, start_time, end_time)
VALUES
(1, CURRENT_DATE + INTERVAL '1 day', '10:00', '10:30'),
(1, CURRENT_DATE + INTERVAL '1 day', '11:00', '11:30');

-- Dr Y today
INSERT INTO doctor_schedules (doctor_id, schedule_date, start_time, end_time)
VALUES
(2, CURRENT_DATE, '11:00', '11:30');
