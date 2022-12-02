import sqlite3 as db

conn = db.connect("database.db")

with open('schema.sql') as f:
    conn.executescript(f.read())

cur = conn.cursor()

cur.execute("INSERT INTO vocabulary (lesson, word) VALUES (?, ?)", 
            (1, 'ich'))
cur.execute("INSERT INTO dbMasters (email, pass) VALUES (?, ?)", ("mogawa@princeton.edu", "cloudyWalls"), ("jrankin@princeton.edu", "N!F7uH$1bEyO"), ("pmyers@luc.edu","theMebbo"))

#numCount = 1
#for line in f:
    #line = line.strip()
    #num = num2words(numCount)
    #num = num.capitalize()
    #cur.execute("CREATE TABLE lesson"+ num + "(word text)")
    #numCount += 1
    #lesson = open(line, "r")
    #for word in lesson:
        #word = word.strip()
        #cur.execute("INSERT INTO lesson"+ num + " VALUES ('" + word + "')")
conn.commit()
conn.close()