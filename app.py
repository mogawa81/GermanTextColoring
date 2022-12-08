from Occurrences import compileWords, lemmatize, extractProperNouns, readability
from analyze_out import write_to_template
#import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort, Blueprint
import string
import random
import psycopg2
import os
from init_db import check

# from flask_login import LoginManager, login_required, login_user
# import flask.ext.login as flask_login
# from flask.ext.login import LoginManager, UserMixin

#db = SQLAlchemy()

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'cloudyWalls'
check()

#secret_key = "cloudyWalls2023"

#db.init_app(app)
    
#login_manager = LoginManager()
#login_manager.login_view = 'login'
#login_manager.init_app(app)

#@login_manager.user_loader
#def load_user(user_id):
    #return User.get(user_id)

def get_db_connection():
    #conn = sqlite3.connect('database.db')
    #conn.row_factory = sqlite3.Row
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    return [conn, cur]

#check if table exists


def get_lesson(lesson):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    query = """SELECT word FROM vocabulary WHERE lesson = %s"""
    cur.execute(query, (lesson,))
    lesson_got = cur.fetchall()
    conn.close()
    if lesson_got is None:
        abort(404)
    return lesson_got

#LOGIN
@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/login/', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('pass')
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    #CHECK IF USERNAME EXISTS IN THE PASSWORD DATABASE
    #returns 1 if exists, 0 if not
    query = """SELECT EXISTS (SELECT 1 FROM dbMasters WHERE email=%s)"""
    cur.execute(query, (email,))
    email_get = cur.fetchone()
    conn.commit()
    #IF USERNAME EXISTS IN THE DATABASE, CHECK IF THE PASSWORD IS CORRECT
    if email_get[0]:
        query1 = """SELECT pass FROM dbMasters WHERE email=%s"""
        cur.execute(query1, (email,))
        pass_get = cur.fetchone()
        conn.commit()
        if str(pass_get[0]) == password:
            #user = email_get[0]
            #login_user(user)
            #global secret_key
            secret_key = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=8))
            cur.execute("""UPDATE dbMasters SET pass=%s WHERE email='s3cretkey'""", (secret_key,))
            conn.commit()
            conn.close()
            return redirect(url_for('edit', auth=secret_key))
        elif pass_get[0] != password:
            #conn.close()
            flash("Password incorrect, please check credentials and try again")
    elif not email_get[0]:
        #conn.close()
        flash("Username incorrect, please check credentials and try again")
    conn.close()
    return redirect(url_for('login'))

# homepage
@app.route('/', methods=['GET','POST'])
def index():
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute('SELECT DISTINCT lesson FROM vocabulary')
    vocabulary = cur.fetchall()
    conn.close()
    lesson_get = request.form.get('lesson-list')
    if request.method == 'POST':
        if lesson_get == 'None':
            print("no lesson selected")
            render_template('index.html', vocabulary=vocabulary)
        else:
            lesson_list = ''
            for word in get_lesson(lesson_get):
                lesson_list += word['word'] + "\n"
            #print(lesson_list)
            render_template('index.html', vocabulary=vocabulary)
    return render_template('index.html', vocabulary=vocabulary)

#EDIT DATABASE MENU
@app.route('/edit/<auth>', methods=('GET', 'POST'))
#@login_required
def edit(auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    if not auth == secret_key[0]:
        #print(auth)
        #print(secret_key)
        flash("Please log in to access the database")
        conn.close()
        return redirect(url_for('login'))
    cur.execute('SELECT DISTINCT lesson FROM vocabulary')
    vocabulary = cur.fetchall()
    conn.close()
    return render_template('edit.html', vocabulary=vocabulary, auth=auth)

#UPDATE A CHAPTER LIST
@app.route('/update/<auth>', methods=('GET', 'POST'))
#@login_required
def update(auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    conn.close()
    if not auth == secret_key[0]:
        #print(auth)
        #print(secret_key)
        flash("Please log in to access the database")
        return redirect(url_for('login'))
    #IF REDIRECTED FROM UPDATE2, KEEP THE LESSON_FROM VARIABLE
    lesson_get = request.form.get('lesson-list')
    #IF NO LESSON SELECTED, DO NOTHING
    if lesson_get == 'None':
        print("no lesson selected")
        return redirect(url_for('edit', auth=auth))
    #if request.method =='POST':
    lesson_str = ''
    for word in get_lesson(lesson_get):
        lesson_str += str(word[0]) + "\n"
    return render_template("update.html", lesson_str=lesson_str, lesson_get=lesson_get, auth=auth)

#UPDATE CHAPTER LIST STEP 2
@app.route('/update/<int:lesson_get>/<auth>', methods=('GET', 'POST'))
#@login_required
def update2(lesson_get, auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    if not auth == secret_key[0]:
        flash("Please log in to access the database")
        conn.close()
        return redirect(url_for('login'))
    if request.method == 'POST':
        text = request.form['word']
        if not text:
            flash('At least 1 word is required! To delete a chapter, go back to the \"Edit\" page')
            lesson_str = ''
            for word in get_lesson(lesson_get):
                lesson_str += str(word[0]) + "\n"
            conn.close()
            return render_template("update.html", lesson_str=lesson_str, lesson_get=lesson_get, auth=auth)
        else:
            #l = get_db_connection()
            #conn = l[0]
            #cur = l[1]
            words = text.split('\r')
            lesson_list = []
            for item in get_lesson(lesson_get):
                lesson_list.append(str(item[0]))
            for word in words:
                word = word.strip('\n')
                #ADD WORDS TO DATABASE
                if word not in lesson_list:
                    #print(word)
                    query = """INSERT INTO vocabulary (lesson, word) VALUES (%s, %s)"""
                    tuple1 = (lesson_get, word)
                    cur.execute(query, tuple1)
                    conn.commit()
                elif word in lesson_list:
                    lesson_list.remove(word)
            #DELETE WORDS IN DATABASE LEFT IN LESSON LIST
            for leftOver in lesson_list:
                print(leftOver)
                cur.execute('DELETE FROM vocabulary WHERE word = %s', (leftOver,))
                conn.commit()
            conn.close()
            flash("Chapter "+str(lesson_get)+" has been updated")
            return redirect(url_for('edit', auth=auth))

#DELETE A CHAPTER LIST
@app.route('/delete/<auth>', methods=('GET', 'POST'))
#@login_required
def delete(auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    if not auth == secret_key[0]:
        flash("Please log in to access the database")
        conn.close()
        return redirect(url_for('login'))
    delete_get = request.form.get('delete-list')
    #IF NO LESSON SELECTED, DO NOTHING
    if delete_get == 'None':
        print("no lesson selected")
        conn.close()
        return redirect(url_for('edit', auth=auth))
    else:
        #l = get_db_connection()
        #conn = l[0]
        #cur = l[1]
        cur.execute('DELETE FROM vocabulary WHERE lesson = %s', (delete_get))
        conn.commit()
        conn.close()
        flash("Chapter "+str(delete_get)+" deleted.")
        return redirect(url_for('edit', auth=auth))

#ADD NEW CHAPTER
@app.route('/add/<auth>', methods=('GET', 'POST'))
#@login_required
def add(auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    conn.close()
    if not auth == secret_key[0]:
        flash("Please log in to access the database")
        return redirect(url_for('login'))
    return render_template("add.html", auth=auth)

#ADD NEW CHAPTER STEP 2
@app.route('/adding/<auth>', methods=('GET', 'POST'))
#@login_required
def add2(auth):
    l = get_db_connection()
    conn = l[0]
    cur = l[1]
    cur.execute("""SELECT pass FROM dbMasters WHERE email='s3cretkey'""")
    secret_key = cur.fetchone()
    if not auth == secret_key[0]:
        flash("Please log in to access the database")
        conn.close()
        return redirect(url_for('login'))
    if request.method =='POST':
        lesson = request.form['lesson']
        text = request.form['word']
        if not lesson:
            flash("Chapter number required!")
        elif not text:
            flash("At least 1 word is required!")
        else:
            #l = get_db_connection()
            #conn = l[0]
            #cur = l[1]
            cur.execute('SELECT DISTINCT lesson FROM vocabulary')
            lessons = cur.fetchall()
            conn.commit()
            #lessons = lessons[0]
            for chapter in lessons:
                #print(chapter[0])
                if chapter[0] == int(lesson):
                    flash("Chapter already exists. To edit, go back to the \"Edit\" page using the Edit button below")
                    return render_template('add.html', auth=auth)
            words = text.split('\r')
            for word in words:
                word = word.strip('\n')
                query = """INSERT INTO vocabulary (lesson, word) VALUES (%s, %s)"""
                tuple1 = (lesson, word)
                cur.execute(query, tuple1)
                conn.commit()
            conn.close()
            flash("Chapter "+str(lesson)+" created successfully")
            return redirect(url_for('edit', auth = auth))
    conn.close()
    return render_template('add.html', auth=auth)


# ANALYZE TEXT
@app.route('/analyze/', methods=('GET', 'POST'))
def analyze():
    if request.method == 'POST':
        chapters = request.form["chapters"]
        text = request.form['text']
        if chapters == "":
            chapters = -1
        else:
            l = get_db_connection()
            conn = l[0]
            cur = l[1]
            cur.execute("SELECT DISTINCT lesson FROM vocabulary")
            size = cur.fetchall()
            count = 0
            for lesson in size:
                count += 1
            print(count)
            conn.commit()
            conn.close()
            #print(size)
            if int(chapters) > count:
                flash('The number of chapters requested exceeds chapters available.')
                return render_template('analyze.html')

        if not text:
            flash('At least 1 word is required!')
        else:
            print("compiling words...")
            wordBank = compileWords("database.db", chapters)
            print("calculating readability...")
            foundWords = readability(wordBank, text)
            print("writing to template...")
            write_to_template(foundWords, text)
            print("returning template...")
            return render_template('analyze_out.html')
            #return "Readability: "+str(foundWords["Readability"])+"%"
            
    return render_template('analyze.html')

if __name__ == '__main__':
    app.run(debug = True)
    
# HOW TO ACTIVATE VENV
#   test\Scripts\activate
#   If it says running scripts is disabled, type:
#       Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# DEACTIVATE VENV
#   type
#       deactivate