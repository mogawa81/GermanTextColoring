import nltk
nltk.download('punkt')
#import spacy
import string
from HanTa import HanoverTagger as ht
#import sqlite3 as db
import re
import psycopg2
import os

#nlp = spacy.load('de_core_news_sm')

def compileWords(num):
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
    words = nltk.tokenize.word_tokenize(line)
    #for mail in line.split():
        #lemma = [lemma for (word,lemma,pos) in tagger.tag_sent(mail.split())]
        #mails_lemma.append(' '.join(lemma))
    mails_lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(words)]
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
    #dict for non-vocab words in the text
    nonVocab = {}
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Proper Nouns":[], "Text": ""} 
    numerator = 0
    denominator = 0
    #f = text.splitlines()
    formattedText = str(text)
    #1: take out all punctuation
    unpunctuatedText = text.translate(str.maketrans('','',string.punctuation))
    #2: lemmatize
    lemmas = lemmatize(unpunctuatedText)
    print("Lemmas pass 1", lemmas)
    #3: Keep a count of the words in the original text
    unpunctuatedText = unpunctuatedText.split()
    wordsCount = 0
    #4: Lemma ForLoop
    for lemma in lemmas:
        denominator += 1
        lemma = lemma.lower()
        newLemma = ""
         # if lemma has not been previously seen and stored in foundLemmas
        if lemma not in foundLemmas:
            # if lemma is in the word bank, check if conjugation is in the list for that lemma
            if lemma in wordBank:
                numerator += 1
                # find the corresponding word in the text
                word = unpunctuatedText[wordsCount]
                # add the word to the new dict under the lemma list
                foundLemmas[lemma] = [word]
            # if it starts with the prefix ge- then remove it manually and check if it's a lemma
            elif lemma[:2] == 'ge':
                newLemma = lemmatize(lemma[2:])[0].lower()
            # if it ends with -tet suffix, remove and re-analyze
            elif lemma[-3:] == 'tet':
                newLemma = lemmatize(lemma[:-3])[0].lower()
            if newLemma != "":
                if newLemma not in foundLemmas:
                    if newLemma in wordBank:
                        numerator += 1
                        word = unpunctuatedText[wordsCount]
                        foundLemmas[newLemma] = [word]
                        print("Lemma stemmed: ", lemma, newLemma)
                    else:
                        # replace all occurrences of the non-vocab word in the text with html formatted color code
                        word = unpunctuatedText[wordsCount]
                        if word not in nonVocab and not word.isnumeric():
                            nonVocab[word] = None
                            formattedText = re.sub(r'\b'+word+r'\b', formatted(word), formattedText)
                elif newLemma in foundLemmas:
                    numerator += 1
                    print("Lemma stemmed: ", lemma, newLemma)
            elif lemma not in wordBank and newLemma == "":
                # replace all occurrences of the non-vocab word in the text with html formatted color code
                word = unpunctuatedText[wordsCount]
                if word not in nonVocab and not word.isnumeric():
                    nonVocab[word] = None
                    formattedText = re.sub(r'\b'+word+r'\b', formatted(word), formattedText)
        # if lemma seen before, add to found vocab score
        elif lemma in foundLemmas:
                numerator += 1
                # add non-lemmatized word to array in Dict under the lemma
                #word = words[wordsCount]
                #if word not in foundLemmas[lemma]:
                    #foundLemmas[lemma].append(word)
        wordsCount += 1
    #extract proper nouns
    nouns = extractProperNouns(text)
    score = numerator/denominator * 100
    print(numerator)
    print(denominator)
    outDict["Readability"] = score
    outDict["Proper Nouns"] = nouns
    formattedText = re.sub('\n', "<br>", formattedText)
    outDict["Text"] = formattedText
    return outDict

# FOR TESTING
def output(foundWords):
    print(foundWords["Proper Nouns"])
    print(foundWords["Text"])

#FOR TESTING
def test():
    print("in Occurences.py!")
    wordBank = {"arbeiten", "finden", "fragen", "gehen", "dürfen", "leisten", "warten"}
    print("compiled words!")
    f = open("sample3.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(foundWords["Text"])

test()