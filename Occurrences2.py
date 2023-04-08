import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import string
import psycopg2
import os
from HanTa import HanoverTagger as ht
import re

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

def unpunctuate(text):
    punctuation_list = string.punctuation
    punctuation_list = punctuation_list.replace("-",'')
    punctuation_list += "»«"
    return text.translate(str.maketrans('','',punctuation_list))

def readability(wordBank, text):
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Text": ""} 
    formattedText = str(text)   # a really long string with color codes
    #---------------PRE-PROCESSING----------------------------------------------------------
    #1: count number of words
    denominator = len(text.split())     # total number of words
    numerator = denominator
    #2: tokenize
    tokens = nltk.tokenize.word_tokenize(text)
    #3: remove duplicates
    tokens = [*set(tokens)]
    #4: lemmatize
    tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
    tokens = tagger_de.tag_sent(tokens)
    print("Analysis: ", tokens)     # for debugging purposes
    #-----------------ANALYSIS--------------------------------------------------------------
    # tokens is a list of tuples.
    #   The first element in the tuple is the original word
    #   The second element in the tuple is the lemma
    #   THe third element in the tuple is its POS
    adjEndings = ['es', 'en', 'em', 'er']
    stopWords = set(stopwords.words('german'))
    for tup in tokens:
    #0: if it is in the vocabulary, do nothing. If not...
        if tup[1] not in wordBank:
    #1: if the word is a Proper Noun, color all occurrences of it gray
            if tup[2] == 'NE':
                temp = re.subn(r'\b'+tup[0]+r'\b', formattedGray(tup[0]), formattedText)
                formattedText = temp[0]
                numerator -= temp[1]
    #2: if the token is punctuation, continue
            elif tup[2] == '$.':
                continue
    #3: if the word is a stopword, continue
            elif tup[0] in stopWords or tup[1] in stopWords:
                continue
    #4: if the word has an adjective ending, check if it's a present/past participle
            elif tup[2] == 'ADJA' and ((tup[1][-2:] in adjEndings) or (tup[1][-1:] == 'e') or (tup[1][-1:] == 'd')):
                if tup[1][-1:] == 'd':
                    newLemma = tagger_de.analyze(tup[1][:-1])
                else:
                    newLemma = tagger_de.analyze(tup[1])
    #5: if the word is a particple with an adjective ending, but not a vocab word, color it red
                if newLemma[1] not in wordBank:
                    temp = re.subn(r'\b'+tup[0]+r'\b', formattedRed(tup[0]), formattedText)
                    formattedText = temp[0]
                    numerator -= temp[1]
    #6: otherwise, check if the lemma is in the core vocabulary. If not, color red
            else:
                temp = re.subn(r'\b'+tup[0]+r'\b', formattedRed(tup[0]), formattedText)
                formattedText = temp[0]
                numerator -= temp[1]
    #-----PREPARE THE DATA FOR THE HTML PAGE------------------------------------------------------
    formattedText = re.sub('\n', "<br>", formattedText)     # preserve line breaks in HTML code
    outDict['Readability'] = str("%s/%s = %s" % (numerator,denominator,(numerator/denominator*100)))
    outDict["Text"] = formattedText
    
    return outDict
    
#FOR TESTING
def test():
    print("in Occurences.py!")
    wordBank = {"meinen", "Name", "Abend", "gut"}
    print("compiled words!")
    f = open("sample3.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(foundWords["Text"], foundWords["Readability"])

#test()