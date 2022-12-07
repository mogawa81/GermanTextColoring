import psycopg2
import os
DATABASE_URL = os.environ.get('DATABASE_URL')
con = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = con.cursor()

cur.execute('SELECT * FROM vocabulary')
cur.close()