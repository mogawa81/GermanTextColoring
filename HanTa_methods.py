from HanTa import HanoverTagger as ht

def lemmatize(words):
    mails_lemma = []
    tagger = ht.HanoverTagger("morphmodel_ger.pgz")
    #for mail in line.split():
        #lemma = [lemma for (word,lemma,pos) in tagger.tag_sent(mail.split())]
        #mails_lemma.append(' '.join(lemma))
    mails_lemma = [lemma for (word, lemma, pos) in tagger.tag_sent(words)]
    return mails_lemma
        
def extractProperNouns(words):
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    tokens=[word for (word,x,pos) in tagger.tag_sent(words,taglevel= 1) if pos == 'NE']
    tokens = list(dict.fromkeys(tokens))
    return tokens