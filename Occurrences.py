import spacy
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from HanTa import HanoverTagger as ht
import sqlite3 as db
import re

nlp = spacy.load('de_core_news_md')

def compileWords(database, num):
    conn = db.connect(database)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM vocabulary")
    size = cur.fetchone()
    if num == -1:
        num = str(size[0])
    wordBank = {"Readability":0, "Proper Nouns": []}
    cur.execute("SELECT word, lesson FROM vocabulary WHERE lesson BETWEEN 1 and "+ num)
    vocabList = cur.fetchall()
    conn.commit()
    for row in vocabList:
        #unpack table name, which is a tuple, into a string
        str_word = row[0]
        str_lesson = row[1]
        wordBank[str_word] = [str_lesson]
        conn.commit()         
    cur.close()
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
    words = nltk.word_tokenize(text)
    tokens=[word for (word,x,pos) in tagger.tag_sent(words,taglevel= 1) if pos == 'NE']
    return tokens

def formatted(word, lesson, colors):
    code = str(colors[lesson - 1]) # lesson 1 is color in element 0
    out = '''<FONT COLOR=''' + code + '''>''' + word + '''</FONT>'''
    return out
    

def readability(wordBank, text):
    out = {}
    out2 = {"Readability":0, "Proper Nouns":[], "Text": ""} 
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
            # if lemma is in the word bank, check if it is in the list for that lemma
            if lemma not in out:
                if lemma in wordBank:
                    # add the lesson number as the first element of the lemma in new dict
                    lesson = wordBank[lemma][0]
                    out[lemma] = [lesson]
                    # find the corresponding word in the text
                    word = words[wordsCount]
                    # add the word to the new dict under the lemma list
                    out[lemma].append(word)
                    # replace the vocab word in the text with html formatted color code
                    line = re.sub(r'\b'+word+r'\b', formatted(word, lesson, colors), line)
                    numerator += 1
            elif lemma in out:
                numerator += 1
                word = words[wordsCount]
                if word not in out[lemma]:
                    out[lemma].append(word)
                line = re.sub(r'\b'+word+r'\b', formatted(word, lesson, colors), line)
            wordsCount += 1
        formatted_text += " " + line
    #extract proper nouns
    nouns = extractProperNouns(text)
    #add number of proper nouns to readability score
    numerator += len(nouns)
    score = numerator/denominator * 100
    out2["Readability"] = score
    out2["Proper Nouns"] = nouns
    out2["Text"] = formatted_text
    return out2

# FOR TESTING
def output(foundWords):
    out = ""
    for lemma in foundWords:
        if lemma == "Readability":
            print("READABILITY:", foundWords[lemma], "%")
        elif lemma == "Proper Nouns":
            print("Proper Nouns:", foundWords[lemma])
        elif foundWords[lemma] != []:
            out += lemma + ": "
            for word in foundWords[lemma]:
                out += str(word) + ", "
            out += "\n"
    return out

#FOR TESTING
def test():
    print("in Occurences.py!")
    wordBank = compileWords("database.db", "1")
    print("compiled words!")
    f = open("sample1.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(output(foundWords))

#test()