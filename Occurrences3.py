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

def unpunctuate(text):
    punctuation_list = string.punctuation
    punctuation_list = punctuation_list.replace("-",'')
    punctuation_list = punctuation_list.replace(".",'')
    punctuation_list = punctuation_list.replace("!",'')
    punctuation_list += "»«"
    return text.translate(str.maketrans('','',punctuation_list))

def stripAdj(token):
    adjEndings = ['es', 'en', 'em', 'er']
    #1: Check for adjective endings
    if ((token[-2:] in adjEndings) or (token[-1:] == 'e')):
    #2: if it is a verb, it will have a -d. Strip.
        if (len(token) > 3) and (token[-3] == 'd'):
            return token[:-3]
        elif (len(token) > 2) and (token[-2] == 'd'):
            return token[:-2]
    #3: if it is an adjective, strip the ending
    if (len(token) > 2) and (token[-2:] in adjEndings):
        return token[:-2]
    elif (len(token) > 1) and (token[-1:] == 'e'):
        return token[:-1]
    #4: otherwise, return the token as is
    else:
        return token

def cornerCase(token, wordBank, formattedText, numerator):
    # if the token is not in the wordBank in upper or lowercase, color red
    if (token not in wordBank) and (token.lower() not in wordBank):
            formattedText = re.sub(r'\b'+token+r'\b', formattedRed(token), formattedText)
            numerator -= 1
    return formattedText, numerator

def readability(wordBank, text):
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Text": ""} 
    formattedText = str(text)   # a really long string with color codes
    #---------------PRE-PROCESSING----------------------------------------------------------
    #1: count number of words
    denominator = len(text.split())     # total number of words
    numerator = denominator
    #2: remove punctuation except -, ., !
    tokens = unpunctuate(text)
    #3: remove duplicates
    tokens = [*set(tokens)]
    #4: tokenize
    tokens = nltk.tokenize.word_tokenize(text)
    #----------------ANALYSIS--------------------------------------------------------------------------
    prev = "."      # the first token is a corner case
    for token in tokens:
    #0: If it's punctuation, skip!
        if token == "." or token == "!":
            continue
    #1: Strip any adjective endings
        print(token)
        token = stripAdj(token)
    #2: If it's at the start of a sentence, treat it as a corner case
        if prev == "." or prev == "!":
            formattedText, numerator = cornerCase(token, wordBank, formattedText, numerator)
    #3: Otherwise, color it red if the token is not in the wordbank
        elif token not in wordBank:
            formattedText = re.sub(r'\b'+token+r'\b', formattedRed(token), formattedText)
            numerator -= 1
    #-----PREPARE THE DATA FOR THE HTML PAGE------------------------------------------------------
    formattedText = re.sub('\n', "<br>", formattedText)     # preserve line breaks in HTML code
    outDict['Readability'] = str("%s/%s = %s" % (numerator,denominator,(numerator/denominator*100)))
    outDict["Text"] = formattedText
    return outDict
                
#FOR TESTING
def test():
    wordBank = {"vergangen"}
    f = open("sample3.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(foundWords["Text"], foundWords["Readability"])

#test() 
    