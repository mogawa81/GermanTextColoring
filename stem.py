from nltk.stem.snowball import GermanStemmer
from compound_split import char_split
import string
from HanTa import HanoverTagger as ht
import nltk

st = GermanStemmer()
token = "vergangenen"
#print(st.stem(token))

tagger_de = ht.HanoverTagger('morphmodel_ger.pgz')
#print("1",tagger_de.analyze('Deutschland'))
f = open("sample3.txt", 'r')
g = f.read()
f.close()
tokens = nltk.word_tokenize(g)
#print("2",tagger_de.tag_sent(tokens))
# print("3",tagger_de.analyze('vergangen'))
# print("3",tagger_de.analyze('vergangene'))

from nltk.corpus import stopwords
stopWords = set(stopwords.words('german'))
# print(stopWords)

# if they have 'to' in database, then it's a verb and can have a d at the end

#https://pypi.org/project/compound-split/ ~95% accuracy
test_str = "Touristenmassen, die zu normalen Zeiten dort unterwegs sind schreckten mich eher ab. Auch mit Corona im Herbst 2020 war hier ziemlich viel los, es hielt sich aber in Grenzen und es waren meist Studenten und Einheimische und keine Reisegruppen. So wohnten wir zwei Nächte im Parkhotel Atlantic hoch über dem Neckar und fußläufig konnten wir von hier aus über den Schlosspark und vorbei am Heidelberger Schloss die berühmte Altstadt erreichen. Heidelberg ist aber nicht nur ein Touristenziel, die Stadt ist auch bekannt für ihre renommierte Universität. Die 1386 gegründete Ruperto Carola ist die älteste Universität im heutigen Deutschland und eine der forschungsstärksten in Europa. Sie zieht Wissenschaftler und Besucher aus aller Welt an und wird von 2019 an als eine von zehn Exzellenzuniversitäten und einem Exzellenzverbund in Deutschland gefördert."
test_str = test_str.translate(str.maketrans('', '', string.punctuation))
x = test_str.split()
for word in x:
    array = (char_split.split_compound(word)[0][0:])
    if array[0] >= 0.6:
        print(array)
#print(char_split.split_compound('Autobahnraststätte')[0][1:])
#print(char_split.split_compound('reise')[0][0])

f = open("sample3.txt", 'r')
g = f.read()
f.close()
f = open("sample4.txt",'w')
for line in g.splitlines():
    if line == '':
        continue
    else:
        for word in line.split(" "):
            f.write(word+"\n")
f.close()

f = open("sample5.txt", 'r')
g = f.readlines()
f.close()
tokens = []
for line in g:
    tokens.append(line)
f = open("sample6.txt",'w')
tokens = [*set(tokens)]
for word in tokens:
    f.write(word)


