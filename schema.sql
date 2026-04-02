CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    report_type VARCHAR(30) NOT NULL,
    report_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    original_text TEXT,
    summary_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blood_test_reports (
    id SERIAL PRIMARY KEY,
    report_id INTEGER UNIQUE REFERENCES reports(id) ON DELETE CASCADE,
    hemoglobin VARCHAR(50),
    wbc VARCHAR(50),
    rbc VARCHAR(50),
    platelet VARCHAR(50),
    glucose VARCHAR(50),
    creatinine VARCHAR(50),
    alt VARCHAR(50),
    ast VARCHAR(50),
    general_comment TEXT
);

CREATE TABLE IF NOT EXISTS epicrisis_reports (
    id SERIAL PRIMARY KEY,
    report_id INTEGER UNIQUE REFERENCES reports(id) ON DELETE CASCADE,
    diagnosis TEXT,
    treatment TEXT,
    discharge_summary TEXT,
    doctor_notes TEXT
);

CREATE TABLE IF NOT EXISTS ekg_reports (
    id SERIAL PRIMARY KEY,
    report_id INTEGER UNIQUE REFERENCES reports(id) ON DELETE CASCADE,
    heart_rate VARCHAR(50),
    rhythm VARCHAR(100),
    pr_interval VARCHAR(50),
    qrs_duration VARCHAR(50),
    qt_qtc VARCHAR(50),
    interpretation TEXT
);