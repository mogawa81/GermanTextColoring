import spacy
import nltk
nltk.download('punkt')
import string
#from nltk.corpus import stopwords
from nltk import tokenize
from HanTa import HanoverTagger as ht
#import sqlite3 as db
import re
import psycopg2
import os

try:
    nlp = spacy.load('de_core_news_md')
except: #if not present, download
    spacy.cli.download('de_core_news_md')
    nlp = spacy.load('de_core_news_md')

def compileWords(database, num):
    #conn = db.connect(database)
    #cur = conn.cursor()
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM vocabulary")
    size = cur.fetchone()
    if num == -1:
        num = str(size[0])
    wordBank = {"Readability":0, "Proper Nouns": []}
    cur.execute("SELECT word FROM vocabulary WHERE lesson BETWEEN 1 and "+ num)
    vocabList = cur.fetchall()
    conn.commit()
    for row in vocabList:
        #unpack table name, which is a tuple, into a string
        str_word = row[0]
        wordBank[str_word]
        conn.commit()         
    conn.close()
    return wordBank

def lemmatize(line):
    mails_lemma = []
    for mail in line.split():
        doc = nlp(mail)
        result = ' '.join([x.lemma_ for x in doc])
        mails_lemma.append(result)
    return mails_lemma
        
def extractProperNouns(text):
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    words = nltk.tokenize.word_tokenize(text)
    tokens=[word for (word,x,pos) in tagger.tag_sent(words,taglevel= 1) if pos == 'NE']
    return tokens

def formatted(word):
    code = "#FF5733" #Bright red
    out = '''<FONT COLOR=''' + code + '''>''' + word + '''</FONT>'''
    return out
    

def readability(wordBank, text):
    # dict for lemmas found in the text
    foundLemmas = {}
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Proper Nouns":[], "Text": ""} 
    numerator = 0
    denominator = 0
    f = text.splitlines()
    colors_file = open("colors.txt", 'r')
    colors = []
    for color in colors_file:
        colors.append(color.split()[0])
    formatted_text = ''''''
    for line in f:
        line_unpunctuated = line.translate(str.maketrans('','',string.punctuation))
        #lemmatize and see if they are in the vocab list
        lemmas = lemmatize(line_unpunctuated)
        #lemmas = lemmas.split()
        words = line_unpunctuated.split()
        wordsCount = 0
        for lemma in lemmas:
            denominator += 1
            # if lemma has not been previously seen and stored in foundLemmas
            if lemma not in foundLemmas:
                # if lemma is in the word bank, check if conjugation is in the list for that lemma
                if lemma in wordBank:
                    # DELETED: add the lesson number as the first element of the lemma in new dict
                    #lesson = wordBank[lemma][0]
                    #foundLemmas[lemma] = [lesson]
                    # find the corresponding word in the text
                    word = words[wordsCount]
                    # add the word to the new dict under the lemma list
                    foundLemmas[lemma].append(word)
                # if word is not a vocab word in the wordbank, color RED
                else:
                    # replace the non-vocab word in the text with html formatted color code
                    line = re.sub(r'\b'+word+r'\b', formatted(word), line)
                    numerator += 1
            elif lemma in foundLemmas:
                numerator += 1
                word = words[wordsCount]
                if word not in foundLemmas[lemma]:
                    foundLemmas[lemma].append(word)
                #DELETE:
                #line = re.sub(r'\b'+word+r'\b', formatted(word, lesson, colors), line)
            wordsCount += 1
        formatted_text += " " + line
    #extract proper nouns
    nouns = extractProperNouns(text)
    #add number of proper nouns to readability score
    #numerator += len(nouns)
    score = numerator/denominator * 100
    outDict["Readability"] = score
    outDict["Proper Nouns"] = nouns
    outDict["Text"] = formatted_text
    return outDict

# FOR TESTING
def output(foundWords):
    print(foundWords["Proper Nouns"])
    print(foundWords["Text"])

#FOR TESTING
def test():
    print("in Occurences.py!")
    wordBank = compileWords("database.db", "1")
    print("compiled words!")
    f = open("sample1.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    output(foundWords)

#test()