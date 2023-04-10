import string
import psycopg2
import os
from HanTa import HanoverTagger as ht
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
#from compound_split import char_split

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

def stopword(token, formattedText, numerator):
    stopWords = set(stopwords.words('german'))
    if (token not in stopWords) and (token.lower() not in stopWords) and (stripAdj(token) not in stopWords) and (stripAdj(token).lower() not in stopWords):
                formattedText = re.sub(r'\b'+token+r'\b', formattedRed(token), formattedText)
                numerator = numerator - 1
    return formattedText, numerator

def specialChars(text):
    text = text.replace("(",'~')
    text = text.replace(")",'~')
    text = text.replace("<",'~')
    text = text.replace(">",'~')
    text = text.replace("•", "")
    text = text.replace("[",'~')
    text = text.replace("]",'~')
    text = text.replace("+","plus")
    return text

def readability(wordBank, text):
    text = str(specialChars(text))
    #dict returning readability, proper nouns, html formatted text
    outDict = {"Readability":0, "Text": ""} 
    formattedText = str(text)   # a really long string with color codes
    #---------------PRE-PROCESSING----------------------------------------------------------
    #1: count number of words
    denominator = len(text.split())     # total number of words
    numerator = denominator
    #2: remove punctuation except -, ., !
    tokens = unpunctuate(text)
    #3: tokenize
    tokens = nltk.tokenize.word_tokenize(text)
    print(tokens)   # for testing
    #4: lemmatize for Proper Noun identification
    tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
    tuples = tagger_de.tag_sent(tokens)
    tuplesCount = 0
    #----------------ANALYSIS--------------------------------------------------------------------------
    prev = "."      # the first token is a corner case
    for token in tokens:
    #0: If it's punctuation or a number, skip
        if token == "." or token == "!":
            pass
    #1: If it's a number, decrease the numerator and skip
        elif token.isnumeric():
            numerator = numerator - 1
            pass
    #2: If it's a compound word, see if both words are vocab words
        # array = (char_split.split_compound(token))
        # if (array[0][0] >= 0.6) and (array[0][1] in wordBank) and (array[0][2] in wordBank):
        #     continue
        # if (array[0][0] >= 0.6) and (array[0][1].lower() in wordBank) and (array[0][2] in wordBank):
        #     continue            
    #3: If it's at the start of a sentence, check if it's in the word bank in upper and lowercase in addition to its stripped forms
        elif prev == "." or prev == "!":
            if (stripAdj(token.lower()) not in wordBank) and (str(token.lower()) not in wordBank) and (token not in wordBank) and (token.lower() not in wordBank):
                formattedText, numerator = stopword(token, formattedText, numerator)
    #4: If it is not a special case, and the token or its stripped form is not in the wordbank, color red
        elif (token not in wordBank) and (stripAdj(token) not in wordBank):
    #5: If the non-vocabulary word is a Proper Noun, color it gray
            if tuples[tuplesCount][2] == 'NE':
                formattedText = re.sub(r'\b'+token+r'\b', formattedGray(token), formattedText)
    #6: If the non-vocabulary word is a stopword, leave it black. If not, color it red
            else:
                formattedText, numerator = stopword(token, formattedText, numerator)            
        prev = token
        tuplesCount += 1
    #-----PREPARE THE DATA FOR THE HTML PAGE------------------------------------------------------
    formattedText = re.sub('\n', "<br>", formattedText)     # preserve line breaks in HTML code
    score = 0
    if denominator != 0:
        score = numerator/denominator*100
    else:
        numerator = denominator
    outDict['Readability'] = str("%s/%s = %s" % (numerator,denominator,score))
    outDict["Text"] = formattedText
    return outDict
                
#FOR TESTING
def test():
    wordBank = {"vergangen", 'eigentlich'}
    f = open("sample3.txt", 'r')
    f = f.read()
    foundWords = readability(wordBank, f)
    print(foundWords["Text"], foundWords["Readability"])

#test() 
    