DROP TABLE IF EXISTS vocabulary;

CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson INTEGER NOT NULL,
    word TEXT NOT NULL
);

DROP TABLE IF EXISTS dbMasters;

CREATE TABLE dbMasters (
    email TEXT NOT NULL,
    pass TEXT NOT NULL
);