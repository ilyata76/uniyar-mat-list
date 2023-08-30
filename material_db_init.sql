CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL,
    year TEXT NOT NULL,
    department TEXT NOT NULL,
    file BLOB NOT NULL,
    author_email TEXT NOT NULL,

    FOREIGN KEY(author_email) REFERENCES users(email)
);