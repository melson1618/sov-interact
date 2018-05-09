import random
import pandas as pd
import pickle

sujet = 1

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
            nn=nonce_nouns.pop() # .pop() removes the first item in the list and puts it in nn.
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nn
        #elif engdict[engdictKeys[i]] == 'verb':
        else:
            nv = nonce_verbs.pop()
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nv
    return newlanguage, engdictKeys


def simplifyThatDictionary():
    '''Pull out just the nonce-English word pairs and create a new dictionary to be used in doTraining'''
    
    nldict, engKeys = participantLang() # Generate random nonce language for new participant, return a list of the english keys 
    nlkeys = list(nldict.keys()) # Make a list of the dictionary keys to iterate over in the next line
    nouns = [] # List for the nouns, needed to randomize incorrect noun in doNounTraining
    noncedict = {}
    for i in range(len(engKeys)):
        if engdict[engKeys[i]] == 'noun': # Make a list of the nouns for later on when the program needs a random noun
            nouns.append(engKeys[i])
    for i in range(len(nlkeys)):
        noncedict[nlkeys[i][0]] = nldict[nlkeys[i]] # Make a dictionary that has an english word as the key and the nonce word as the value
    
    pickle.dump(noncedict, open('../data/part_dict/{}-langDict.csv'.format(sujet), 'w+'))
    return noncedict, nouns # English:nonce

nonce_nouns = ['melnog', 'bloffen', 'neegoul', 'vaneep', 'klamen', 'slegam']

nonce_verbs = ['dof', 'pouz','kass','zeeb']


################################################################
# 'point': 'verb '
# 'point': 'verb'
engdict = {'shoot': 'verb', 'police': 'noun', 'doctor': 'noun',
           'artist': 'noun', 'point': 'verb', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun', 'boxer':'noun'}


simplifyThatDictionary()
