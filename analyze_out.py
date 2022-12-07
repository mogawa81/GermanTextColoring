#import os
#from bs4 import BeautifulSoup
from pathlib import Path

#FOR TESTING
def printFoundWords(html_template, foundWords, encode_with):
    #Print Found Words
    html_template += '''<p id="foundWords">'''.encode(encode_with)
    html_template += '''Found Words:\n<br>'''.encode(encode_with)
    for lemma in foundWords:
        if lemma != "Readability":
            html_template += lemma.encode(encode_with)
            html_template += ": ".encode(encode_with)
            for word in foundWords[lemma]:
                word = str(word)
                html_template +=  word.encode(encode_with)#str(word)
                html_template += ", ".encode(encode_with)
                #print(str(word))
            html_template += "\n<br>".encode(encode_with)
    return html_template
        
    

def write_to_template(foundWords, text):
    #cur_path = os.path.dirname(__file__)
    #rel_path = "flask_app/templates/analyze_out.html"
    #new_path = os.path.relpath(rel_path, cur_path)
    #path = "C:/Users/ogawa/OneDrive - Princeton University/IW/ArticleFinder/flask_app/templates/analyze_out.html"
    path = Path(('templates/analyze_out.html'))
    #f_read = open(path, 'r')
    f = open(path, 'wb')
    encode_with = "UTF-8"
    #contents = f_read.read()
    #soup = BeautifulSoup(contents, 'html.parser')
    
    html_template = '''{% extends 'base.html' %}\n{% block content %}\n<h1>
    {% block title %} Analyzed text {% endblock %}\n</h1>\n<p id="readability">'''.encode(encode_with)
    
    #Print readability
    html_template += '''Readability: '''.encode(encode_with)
    html_template += str(foundWords["Readability"]).encode(encode_with)
    html_template += '''%</p>\n<br>\n'''.encode(encode_with)
    
    #Print proper nouns
    html_template += '''<p id="properNouns">'''.encode(encode_with)
    html_template += '''Proper Nouns: '''.encode(encode_with)
    html_template += str(foundWords["Proper Nouns"]).encode(encode_with)
    html_template += '''</p>\n<br>\n'''.encode(encode_with)
    
    #html_template = printFoundWords(html_template, foundWords, encode_with)
    html_template += '''<p id="text">'''.encode(encode_with) 
    html_template += str(foundWords["Text"]).encode(encode_with)
    html_template += '''</p>\n<br>'''.encode(encode_with)
            
    html_template += '''\n</p>\n<br>\n{% endblock %}'''.encode(encode_with)
    
    # replace the code into the file
    #p_tag = soup.find("p", {"id": "readability"}).string
    #p_tag = p_tag.string
    #p_tag.replace_with(readability_template)
    #p2_tag = soup.find("p", {"id": "foundWords"})
    #p2_tag = p2_tag.string
    #p2_tag.replace_with(html_template)
    #with open(path, "wb") as f:
        #f.write(soup.prettify("utf-8"))
    
    f.write(html_template)
    
    # close the file
    f.close()


#dic = {"Readability": 12, "Proper Nouns": ["Anna"], "ich": ["Ich", "ich"]}
#text = "success"
#write_to_template(dic, text)

#print(Path('templates/analyze_out.html').exists())