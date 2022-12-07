import sqlite3 as db
import mysql.connector
import psycopg2
import os

#conn = db.connect("database.db")

DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

#conn = mysql.connector.connect(host='localhost',
                             #database='database',
                             #user='root')
#cur = conn.cursor(prepared=True)

with open('schema.sql') as f:
    conn.executescript(f.read())

#cur = conn.cursor()

cur.execute("INSERT INTO vocabulary (lesson, word) VALUES (%s, %s)", 
            (1, 'ich'))
cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("mogawa@princeton.edu", "cloudyWalls"), ("jrankin@princeton.edu", "N!F7uH$1bEyO"), ("pmyers@luc.edu","theMebbo"))

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