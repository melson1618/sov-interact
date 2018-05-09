'''function spellcheckWords() to correct a word to the closest correct vocabulary item 
plus required functions.'''

#######################################################################################

#import packages
import random
import numpy as np

#function to shuffle the elements in a list
def shuffle(l):
    return random.sample(l,len(l))

#calculates the levenshtein edit distance between two sequences or strings, seq1 and seq2.  
def levenshtein(seq1, seq2):
    oneago = None
    thisrow = range(1, len(seq2) + 1) + [0]
    for x in xrange(len(seq1)):
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in xrange(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[len(seq2) - 1]

#Calculates the Demerau-levenshtein distance between two sequences or strings, s1 and s2
#Difference with levenshtein: it allows transpositon as a edit operation on top of deletion, insertion and substitution.
def dl(s1, s2):
	d = {}
	lenstr1 = len(s1)
	lenstr2 = len(s2)
	for i in xrange(-1,lenstr1+1):
	    d[(i,-1)] = i+1
	for j in xrange(-1,lenstr2+1):
	    d[(-1,j)] = j+1
	for i in xrange(lenstr1):
	    for j in xrange(lenstr2):
	        if s1[i] == s2[j]:
	            cost = 0
	        else:
	            cost = 1
	        d[(i,j)] = min(
	                       d[(i-1,j)] + 1, # deletion
	                       d[(i,j-1)] + 1, # insertion
	                       d[(i-1,j-1)] + cost, # substitution
	                      )
	        if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
	            d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition
	return d[lenstr1-1,lenstr2-1]

#finds the closest correct word to the potentially incorrect word
# modify this function to included any weighted selection you might want to incorporate
def spellcheckWord(word,possibleWords):
    possibleWords = shuffle(possibleWords) #shuffles so that the match is randomly selected among the closest
    d = np.inf # set to arbitrarily large number
    bestMatch = None
    for possibleWord in possibleWords:
        d_new = dl(word,possibleWord);# compute dl edit distance. To compute levenshtein substitute dl(0 for levenshtein())
        # if closer than previous try, store replacement word in position i of output list
        if d_new < d :
            bestMatch = possibleWord
            d = d_new
    return bestMatch

# Checks for 
def spellcheckWords(str):
    str = str.lower() # check to make sure things are lower case
    input = str.split(); # split into array of words - not specifying a seperator means that multipe whitespace is treated as one, empty whitespace is ignored
    possibleWords = ['nezno','nefri','kogla','kospu','mokte','jelpa']#list containing the correct lexicon. You can also pass it as an argument tot he function depending on how variable this list is. It is the same across, I would leave it here.
    correctedWords = [spellcheckWord(word,possibleWords) for word in input]
    output = ' '.join(correctedWords)# turn back into a string
    return output

'''Test'''
word='kaglu'
corrected_word=spellcheckWords(word)
print corrected_word
