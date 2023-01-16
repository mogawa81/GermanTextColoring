import spacy
import nltk
nltk.download('punkt')
import string
from HanTa import HanoverTagger as ht
#import sqlite3 as db
import re
import psycopg2
import os

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
    wordBank = {}
    cur.execute("SELECT word FROM vocabulary WHERE lesson BETWEEN 1 and "+ num)
    vocabList = cur.fetchall()
    conn.commit()
    for row in vocabList:
        #unpack table name, which is a tuple, into a string
        str_word = row[0]
        str_word = str_word.lower()
        wordBank[str_word] = None
        conn.commit()         
    conn.close()
    return wordBank

def lemmatize(line):
    mails_lemma = []
    tagger = ht.HanoverTagger("morphmodel_ger.pgz")
    for mail in line.split():
        lemma = [lemma for (word,lemma,pos) in tagger.tag_sent(mail.split())]
        mails_lemma.append(' '.join(lemma))
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
    formatted_text = ''''''
    for line in f:
        line_unpunctuated = line.translate(str.maketrans('','',string.punctuation))
        #lemmatize and see if they are in the vocab list
        lemmas = lemmatize(line_unpunctuated)
        print(lemmas)
        words = line_unpunctuated.split()
        wordsCount = 0
        for lemma in lemmas:
            lemma = lemma.lower()
            denominator += 1
            # if lemma has not been previously seen and stored in foundLemmas
            if lemma not in foundLemmas:
                # if lemma is in the word bank, check if conjugation is in the list for that lemma
                if lemma in wordBank:
                    numerator += 1
                    # DELETED: add the lesson number as the first element of the lemma in new dict
                    #lesson = wordBank[lemma][0]
                    #foundLemmas[lemma] = [lesson]
                    #------------------------------------------------------------------------------
                    # find the corresponding word in the text
                    word = words[wordsCount]
                    # add the word to the new dict under the lemma list
                    foundLemmas[lemma] = [word]
                # if word is not a vocab word in the wordbank, color RED
                else:
                    # replace the non-vocab word in the text with html formatted color code
                    word = words[wordsCount]
                    # if a word is a number, don't color
                    if not word.isnumeric():
                        line = re.sub(r'\b'+word+r'\b', formatted(word), line)
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
    score = numerator/denominator * 100
    print(numerator)
    print(denominator)
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
    wordBank = {"arbeiten", "finden", "fragen", "gehen"}
    print("compiled words!")
    f = open("sample3.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(foundWords["Text"])

#test()