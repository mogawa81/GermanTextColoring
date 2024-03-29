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
    conn.commit()
    exists = cur.fetchone()
    if exists[0] == False:
        with open('schema.sql') as f:
            cur.execute(f.read())
        cur.execute("INSERT INTO vocabulary (lesson, word) VALUES (%s, %s)", 
                (1, 'ich'))
        conn.commit()

        cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("mogawa@princeton.edu", "cloudyWalls"))
        conn.commit()
        cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("jrankin@princeton.edu", ""))
        conn.commit()
        cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("pmyers@luc.edu","theMebbo"))
        conn.commit()
        cur.execute("INSERT INTO dbMasters (email, pass) VALUES (%s, %s)", ("s3cretkey", "nothing"))
        conn.commit()
    
    cur.execute("UPDATE dbMasters SET pass='nothing' WHERE email='s3cretkey'")

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