import random

def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    random.shuffle(nonce_nouns)
    random.shuffle(nonce_verbs)
    for i in range(10):
        #print (i, used_words)
        if engdict[engdictKeys[i]] == 'noun':
            # Here's one way to do it.
            nn=nonce_nouns.pop()
            # .pop() removes the first item in the list and puts it in nn.
            # Since it empties the list as we go, we don't need to worry about
            # the if/else.  You've already shuffled the list, so the item
            # popped should be random.  However, if you need to use nonce_nouns
            # again later, you'll find that it's empty!
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nn
        else:
            nv = nonce_verbs.pop()
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nv
    print newlanguage, engdictKeys
    return newlanguage, engdictKeys
    


nonce_nouns = ['melnog', 'bloffen', 'neegoul', 'vaneep', 'klamen', 'slegam']

nonce_verbs = ['dof', 'pouz','kass','zeeb']

################################################################
# 'point': 'verb '
# 'point': 'verb'
engdict = {'shoot': 'verb', 'police': 'noun', 'doctor': 'noun',
           'artist': 'noun', 'point': 'verb', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun', 'boxer':'noun'}

participantLang()
