import string
import psycopg2
import os
from HanTa import HanoverTagger as ht
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

def compileWords(num):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM vocabulary")
    size = cur.fetchone()
    if num == -1:
        num = str(size[0])
    wordBank = {}
    cur.execute("SELECT word FROM vocabulary WHERE lesson BETWEEN 1 and "+ num)
    vocabList = cur.fetchall()
    conn.commit()
    for row in vocabList:
        #unpack table name, which is a tuple, into a string
        str_word = row[0]
        str_word = str_word #.lower()
        wordBank[str_word] = None
        conn.commit()         
    conn.close()
    return wordBank

def formattedGray(word):
    code = "#A0A0A0" #Gray
    out = '''<FONT COLOR=''' + code + '''>''' + word + '''</FONT>'''
    return out

def formattedRed(word):
    code = "#FF5733" #Bright red
    out = '''<FONT COLOR=''' + code + '''>''' + word + '''</FONT>'''
    return out

def readability(wordBank, text):
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Text": ""} 
    formattedText = str(text)   # a really long string with color codes
    #---------------PRE-PROCESSING----------------------------------------------------------
    #1: count number of words
    split = text.split()         # split by spaces
    denominator = len(split)     # total number of words
    numerator = denominator
    #3: remove duplicates
    tokens = [*set(split)]
    #2: tokenize
    tokens = nltk.tokenize.word_tokenize(text)
    
    