import sqlite3 as db
#import mysql.connector
import psycopg2
import os

#conn = db.connect("database.db")
def check():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    #conn = mysql.connector.connect(host='localhost',
                             #database='database',
                             #user='root')
    #cur = conn.cursor(prepared=True)
    query = """select exists(select * from information_schema.tables where table_name=%s)"""
    cur.execute(query, ('vocabulary',))
    exists = cur.fetchone()
    if exists[0] == False:
        with open('schema.sql') as f:
            cur.execute(f.read())
        cur.execute("INSERT INTO vocabulary (lesson, word) VALUES (%s, %s)", 
                (1, 'ich'))

    #cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS dbMasters")
    conn.commit()
    cur.execute("CREATE TABLE dbMastersCREATE TABLE dbMasters (email TEXT NOT NULL, pass TEXT NOT NULL)")
    conn.commit()
    cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("mogawa@princeton.edu", "cloudyWalls"))
    cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("jrankin@princeton.edu", "N!F7uH$1bEyO"))
    cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("pmyers@luc.edu","theMebbo"))
    cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%S, %S)", ("s3cretkey, nothing"))

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