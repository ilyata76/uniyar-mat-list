CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    middle_name TEXT,
    surname TEXT NOT NULL,
    university TEXT NOT NULL,
    faculty TEXT NOT NULL,
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    seniority TEXT NOT NULL
);