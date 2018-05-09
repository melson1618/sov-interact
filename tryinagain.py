import random

def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    used_words = []
    random.shuffle(nonce_nouns)
    random.shuffle(nonce_verbs)
    for i in range(10):
        print i, used_words
        if engdict[engdictKeys[i]] == 'noun':
            if nn in used_words:
                pass
            else:
                newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nn
                used_words.append(nn)
                #print used_words
        elif engdict[engdictKeys[i]] == 'verb':
            nv = random.choice(nonce_verbs)
            if nv in used_words:
                pass
            else:
                newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nv
                used_words.append(nv)
                #print used_words
            i+=1
        # Make a dictionary that has a tuple (Engword, function) as key and nonce word as value
    print 'This is the language: ', newlanguage, "These got used: ", used_words
    return newlanguage, engdictKeys

nonce_nouns = ['melnog', 'bloffen', 'neegoul', 'vaneep', 'klamen', 'slegam']

nonce_verbs = ['dof', 'pouz','kass','zeeb']

engdict = {'shoot': 'verb', 'police': 'noun', 'doctor': 'noun',
           'artist': 'noun', 'point': 'verb ', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun','boxer':'noun'}

participantLang()