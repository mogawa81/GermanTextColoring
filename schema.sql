DROP TABLE IF EXISTS vocabulary;

CREATE TABLE vocabulary (
    id SERIAL PRIMARY KEY,
    lesson INTEGER NOT NULL,
    word TEXT NOT NULL
);

DROP TABLE IF EXISTS dbMasters;

CREATE TABLE dbMasters (
    email TEXT NOT NULL,
    pass TEXT NOT NULL
);

INSERT INTO dbMasters (email, pass) VALUES ("mogawa@princeton.edu", "cloudyWalls")
INSERT INTO dbMasters (email, pass) VALUES ("s3cretkey", "")