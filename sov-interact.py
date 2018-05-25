# -*- coding: utf-8 -*-

import pandas as pd
from psychopy import core, gui, misc, data, visual, event, sound
import os, re, random
import pickle
import numpy as np


##########
#Dummy variables, change later

#sujet= 'S_001'

##########
# FUNCTIONS

def getPartOrder(sujet):
    partOrder = sujet[0:1]

    if partOrder == 'S':
        primOrder = 'SOV'
    else:
        primOrder = 'OSV'
    return primOrder

def instructions(x):
    'Display instructions on screen and wait for participant to press button'
    win.flip()
    visual.TextStim(win, text=x, color="black", wrapWidth=700).draw()
    win.flip()
    event.waitKeys()
    win.flip()
    return


def findStimImage():
    '''Gather the images for the single nouns and sentences into lists'''

    nounpics = [] # List of file names for images of nouns
    sentencepics = [] # List of file names for full Agent-Verb-Object sentences 
    for pic in images:
        if "_" in pic: # The nouns have 2 versions, presented R or L facing
            noun = pic.split("_")
            if len(noun) == 2:
                nounpics.append(pic)
            else:
                sentencepics.append(pic)
        else:
            nounpics.append(pic)
    return sentencepics, nounpics

def sortVerbImages():
    '''Sort the images based on the verb, this is used later in the cpImages function, which selects three additional images
    to be presented during the computer-director trials of the interaction phase. Image names are saved without file extensions.'''
    punchlst = []
    pointlst = []
    kicklst = []
    shootlst = []
    for p in sentencepics:
        sentlst = p.split('_')
        pagt = sentlst[0]
        pvrb = sentlst[1]
        ppat = sentlst[2]
        if pvrb == 'punch':
            punchlst.append(p)
        elif pvrb == 'point':
            pointlst.append(p)
        elif pvrb == 'kick':
            kicklst.append(p)
        else:
            shootlst.append(p)
    return punchlst, pointlst, kicklst, shootlst 

def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant, (English, function):nonce
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    random.shuffle(nonce_nouns)
    random.shuffle(nonce_verbs)
    for i in range(len(engdictKeys)):
        #print (i, used_words)
        if engdict[engdictKeys[i]] == 'noun':
            nn=nonce_nouns.pop() # .pop() removes the first item in the list and puts it in nn.
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nn
        else:
            nv = nonce_verbs.pop()
            newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nv
    return newlanguage, engdictKeys


def simplifyThatDictionary():
    '''Pull out just the nonce-English word pairs and create a new dictionary to be used in doTraining'''
    
    nldict, engKeys = participantLang() # Generate random nonce language for new participant, return a list of the english keys 
    nlkeys = list(nldict.keys()) # Make a list of the dictionary keys to iterate over in the line 75
    nouns = [] # List for the nouns, needed to randomize incorrect noun in doNounTraining
    noncedict = {}
    for i in range(len(engKeys)):
        if engdict[engKeys[i]] == 'noun': # Make a list of the nouns for later on when the program needs a random noun
            nouns.append(engKeys[i])
    for i in range(len(nlkeys)):
        noncedict[nlkeys[i][0]] = nldict[nlkeys[i]] # Make a dictionary that has an english word as the key and the nonce word as the value
    pickle.dump(noncedict, open('../data/partDict/{}-langDict.csv'.format(sujet), 'w+'))
    return noncedict, nouns # noncedict = {English:nonce}

def reverseDict():
    reverseNonce = {}
    nonceKeys = list(noncedict.keys())
    for i in range(len(nonceKeys)):
        reverseNonce[noncedict[nonceKeys[i]]] = nonceKeys[i]
    return reverseNonce

def playStim(x):
    # play sound and do not allow other processes to continue until sound finished
    x.play()
    core.wait(x.getDuration())
    return


def makeButton(buttonName, buttonText):
    # button names are A B C and D and have locations associated with them
    # make autodrawing button (will have to be turned off to not display)
    button = visual.Rect(
        win,
        width=buttonWidth,
        height=buttonHeight,
        fillColor=buttonColor,
        pos=buttonPositions[buttonName],
        autoDraw=True,
        lineWidth=1,
        lineColor='black'
    )
    button.draw()

    text = visual.TextStim(
        win,
        text=buttonText,
        color="black",
        pos=buttonPositions[buttonName],
    )
    # textstim does not have autodraw as attribute before creation
    text.setAutoDraw(True)
    text.draw()
    
    return button, text


def getClick(mouse, buttons, eng):

    # going to loop until click detected
    clicked = False
    
    while not clicked:
        # button is a tuple where 0 is shape obj and 1 is text obj
        for n, button in enumerate(buttons):
            # if mouse detected in shape (not clicked)
            if button[0].contains(mouse):
                # make button dark grey
                button[0].setFillColor(hoverColor)
                win.flip()
            else:
                # otherwise make button normal color
                button[0].setFillColor(buttonColor)
                win.flip()
            # if click detected in button
            if mouse.isPressedIn(button[0]):
                # then break the loop
                clicked = True
                # and get the response
                responseButton = n

    responseText = buttons[responseButton][1]
                
    win.flip()
    
    return responseButton, responseText.text


def initializeTrial(displayText, buttonNames, buttonTexts, pic, audioStim):

    # create mouse object (not active yet)
    mouse = event.Mouse(visible=False)
    
    win.flip()
    picObj = visual.ImageStim(
        win,
        image=pathToImages+pic+'.jpg',
        pos = (0, 20)
    )
    picObj.setAutoDraw(True)
    picObj.draw()
    win.flip()

    buttonsAssc = {}
    for n,i in enumerate(buttonNames):
        buttonsAssc[i] = buttonTexts[n]

    buttons = [makeButton(location, buttonsAssc[location]) for location in buttonsAssc.keys()]
    win.flip()
    
    if audioStim == ['none']:
        core.wait(0.0)
    else:
        core.wait(0.5)
    # make and play sound objects based on the nonce language of the participant'
    stims = makePhrase(audioStim)
    for stim in stims:
        playStim(stim)

    #core.wait(0.5)
    eng = visual.TextStim( #text that gets presented
        win,
        text=displayText,
        color='black',
        pos=(0,200),
        height=36
    )
    eng.setAutoDraw(True)
    eng.draw()
    win.flip()

    return mouse, buttons, eng, picObj


def makePhrase(words):
    # make list of sound objects based on words
    stimulus = [sound.Sound('../stimuli/audio/'+i+'.wav') for i in words]

    return stimulus

def doNounTrainingTrial(noun, wrongNoun, engNoun, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.150)
    
    # Get the correct nonce word and an incorrect one for the training
    nonceText = noun # Leaving this here until I have the audio stims
    target = noun # Correct word that matches image
    miss = wrongNoun # Random nonce word that does not match image, but is one of the nouns from the nonce language

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, eng, pic = initializeTrial(
        displayText=None,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = engNoun,
        audioStim = [target]
    )

    # wait 500 ms after sound
    core.wait(0.5)

    consBisText = "...click on the choice that matches what you heard..."
    consBis = visual.TextStim(
        win,
        text=consBisText,
        pos=(0,300),
        color="black",
        height=16,
        italic=True
    )
    consBis.setAutoDraw(True)
    win.flip()
    
    # update button text from dashes to actual content
    for n,button in enumerate(buttons):
        button[1].text = buttonTexts[n]
        
    # activate mouse
    mouse.setVisible(True)

    # recover response and response button
    responseButton, response = getClick(mouse, buttons, eng)

    # check to see that participant selected the correct nonce word
    if response == target:
        correct = 1
    else:
        correct = 0

    # if correct, then turn button green
    if correct == 1:
        buttons[responseButton][0].setFillColor('green') # no need to draw since AutoDraw active
    # else turn button red
    else:
        buttons[responseButton][0].setFillColor('red')

    win.flip()
    # wait 1000 ms before moving on to next trial    
    core.wait(1)
    
    # erase objects
    for button in buttons:
        button[0].setAutoDraw(False)
        button[1].setAutoDraw(False)
    #cons.setAutoDraw(False)
    eng.setAutoDraw(False) 
    consBis.setAutoDraw(False)
    pic.setAutoDraw(False)

    return response, correct, buttonTexts[0], buttonTexts[1]


def doNounTraining(sujet, repeat = 0):

    # ntrainingDf will be updated by the function, so must be global
    global ntrainingDf
    
    numberBlocks = 6
    trainingNouns = []
    for block in range(numberBlocks):
        blockNouns = list(np.copy(nouns)) # nouns is generated in simplifyThatDictionary, and is a list of Eng nouns 
        
        random.shuffle(blockNouns)
        trainingNouns.append(blockNouns)

    trainingNouns = trainingNouns[0] + trainingNouns[1] + trainingNouns[2]+trainingNouns[3]+trainingNouns[4]+trainingNouns[5]

    i = 0 # because we need to repeat incorrect trials, must have own counter
    while i < 24: # Iterate through entire noun list once
        engNoun = trainingNouns[i]
        nounWord = noncedict[engNoun]
        otherWord = random.choice(nouns)
        otherNonce = noncedict[otherWord] # Randomly choose a word from the nonce list to be the alternative button
        if otherNonce != nounWord: # Make sure the buttons aren't assigned the same word
    # do the trial and recover button content
            response, correct, buttonA, buttonB = doNounTrainingTrial(nounWord, otherNonce, engNoun, i)
        else:
            continue

    # if trial correct, move on, else repeat
        if correct == 1:
            i += 1
            
        else:
            continue

        dico = {
            'suj':sujet,
            'trial':i,
            'targetNoun':nounWord,
            'engNoun':engNoun,
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct,
            'iteration':repeat
        }
        trial = pd.DataFrame([dico])
        #print 'trial', trial
        ntrainingDf = ntrainingDf.append(trial)
        #print 'update', ntrainingDf
        #loop += 1
    return


def doNounTestTrial(noun, wrongNoun, engNoun, nTrial):

    # Get the correct nonce word and an incorrect one for the testing
    target = noun # Correct word that matches image
    miss = wrongNoun # Random nonce word that does not match image, but is one of the nouns from the nonce language

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)
    print target
    # create mouse and button objects, display instructions
    mouse, buttons, eng, pic = initializeTrial(
        displayText= None,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = engNoun,
        audioStim = ['none']
    )

    consBisText = "...click on the word that matches the image..."
    consBis = visual.TextStim(
        win,
        text=consBisText,
        pos=(0,300),
        color="black",
        height=16,
        italic=True
    )
    consBis.setAutoDraw(True)
    win.flip()
    
    # update button text from dashes to actual content
    for n,button in enumerate(buttons):
        button[1].text = buttonTexts[n]
        
    # activate mouse
    mouse.setVisible(True)

    # recover response and response button
    responseButton, response = getClick(mouse, buttons, eng)

    # count number of correct responses
    if response == target:
        correct = 1
    else:
        correct = 0

    # make response button blue after click
    buttons[responseButton][0].setFillColor('blue')

    win.flip()
    # wait 1000 ms before moving on to next trial    
    core.wait(1)
    
    # erase objects
    for button in buttons:
        button[0].setAutoDraw(False)
        button[1].setAutoDraw(False)
    eng.setAutoDraw(False) 
    consBis.setAutoDraw(False)
    pic.setAutoDraw(False)
    
    return response, correct, buttonTexts[0], buttonTexts[1]

def buttonWordsDif():
    otherWord = random.choice(nouns)
    otherNonce = noncedict[otherWord]
    return otherWord, otherNonce

def doNounTesting(sujet, repeat = 0):

    # ntestingDf will be updated by the function, so must be global
    global ntestingDf

    num_correct = 0
    numberBlocks = 3
    testNouns = []
    for block in range(numberBlocks):
        blockNouns = list(np.copy(nouns)) # nouns is generated in simplifyThatDictionary, and is a list of Eng nouns 
        
        random.shuffle(blockNouns)
        testNouns.append(blockNouns)

    testNouns = testNouns[0] + testNouns[1] + testNouns[2]# don't do this normally 
    for n,engNoun in enumerate(testNouns): # Show each noun once in each testing block
        nounWord = noncedict[engNoun]
        wordsDif = False
        while not wordsDif:
            otherWord, otherNonce = buttonWordsDif()
            if nounWord != otherNonce:
                wordsDif = True

        # do the trial and recover button content
        response, correct, buttonA, buttonB = doNounTestTrial(nounWord, otherNonce, engNoun, n)
        num_correct += correct
            
        dico = {
            'suj':sujet,
            'trial':n,
            'correct_noun':nounWord,
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct,
            'iteration': repeat
        }
        trial = pd.DataFrame([dico])
        ntestingDf = ntestingDf.append(trial)
    
    return

def typeTheNouns(suj, repeat=0):

    global ntypingDf

    num_correct = 0
    #corrent = 0
    numberBlocks = 3
    testNouns = []
    for block in range(numberBlocks):
        blockNouns = list(np.copy(nouns)) # nouns is generated in simplifyThatDictionary, and is a list of Eng nouns 
        
        random.shuffle(blockNouns)
        testNouns.append(blockNouns)

    testNouns = testNouns[0] + testNouns[1] + testNouns[2]# don't do this normally 
    for n,engNoun in enumerate(testNouns): # Show each noun once in each testing block
        nounWord = noncedict[engNoun]
        print nounWord
        imagePath = pathToImages+engNoun+'.jpg'
        response = typingTrial(win, imagePath)
        correctNoun = processResponses(response) 
        #print 'This is correctNoun: ', correctNoun
        if correctNoun[0] == nounWord:
            correct = 1
            num_correct += 1
        else:
            correct = 0
            num_correct += 0

        dico = {
            'suj':sujet,
            'trial':n,
            'correct_noun':nounWord,
            'response':response,
            'image':engNoun,
            'correct':correct,
            'total_correct':num_correct,
            'iteration':repeat 
        }
        trial = pd.DataFrame([dico])
        ntypingDf = ntypingDf.append(trial)

    
    checkLearning(num_correct, sujet, repeat) # Check to see if participant got at least 75% correct
    return

def checkLearning(numCorrect, suj, repeat):
    '''Check how many of the noun testing trials participant got correct, if it is less than 75% (9) repeat nounTraining, 
    unless they've already been through it twice'''

    if repeat == 1: # Check to see if they're already done it twice
        if numCorrect < 9:
            instructions(thanksfornothing)
        else:
            instructions(sentences)
            doSentTraining(primOrder)
            instructions(sentence_test)
            sentTesting(primOrder)
            instructions(interaction_phase)
            t = random.randint(1,5)
            core.wait(t)
            initializeInteract(primOrder)
            instructions(thankyou_complete)
    elif numCorrect < 9: # If they got less than 75% correct, repeat training
        instructions(tryagain)
        doNounTraining(suj, repeat = 1)
        instructions(teststatement)
        doNounTesting(suj, repeat = 1)
        instructions(type_nouns)
        typeTheNouns(suj, repeat=1)

    else:
        # If participant passes nountesting, initialize sentTraining and then testing, base testing on order assigned in ID
        instructions(sentences)
        doSentTraining(primOrder)
        instructions(sentence_test)
        sentTesting(primOrder)
        instructions(interaction_phase)
        t = random.randint(1,5)
        core.wait(t)
        initializeInteract(primOrder)
        instructions(last_test)
        sentTesting(primOrder, test = 'Post')
        instructions(thankyou_complete)
    return

def doSentTrainingTrial(agtWord, vrbWord, objWord, sentence, order, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.5)
    
    orderSOV = [agtWord, objWord, vrbWord]
    orderOSV = [objWord, agtWord, vrbWord]
    # Get the correct nonce sentence and the alternartive word order for trial
    if order == 'OSV':  # Stim for OSV word order
        target = ' '.join(orderOSV)
        miss = ' '.join(orderSOV)
        stimlst = orderOSV
    else:
        nonceText = ' '.join(orderSOV)
        target = ' '.join(orderSOV)
        miss = ' '.join(orderOSV)
        stimlst = orderSOV

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, eng, pic = initializeTrial(
        displayText=None,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = sentence,
        audioStim = stimlst
    )

    # wait 500 ms after sound
    core.wait(0.5)

    consBisText = "...click on the choice that matches what you heard..."
    consBis = visual.TextStim(
        win,
        text=consBisText,
        pos=(0,300),
        color="black",
        height=16,
        italic=True
    )
    consBis.setAutoDraw(True)
    win.flip()
    
    # update button text from dashes to actual content
    for n,button in enumerate(buttons):
        button[1].text = buttonTexts[n]
        
    # activate mouse
    mouse.setVisible(True)

    # recover response and response button
    responseButton, response = getClick(mouse, buttons, eng)

    # check to see that participant selected the correct word order
    if response == target:
        correct = 1
    else:
        correct = 0

    # if correct, then turn button green
    if correct == 1:
        buttons[responseButton][0].setFillColor('green') # no need to draw since AutoDraw active
    # else turn button red
    else:
        buttons[responseButton][0].setFillColor('red')

    win.flip()
    # wait 1000 ms before moving on to next trial    
    core.wait(1)
    
    # erase objects
    for button in buttons:
        button[0].setAutoDraw(False)
        button[1].setAutoDraw(False)
    #cons.setAutoDraw(False)
    eng.setAutoDraw(False) 
    consBis.setAutoDraw(False)
    pic.setAutoDraw(False)
    
    print order 
    return response, correct, buttonTexts[0], buttonTexts[1]

def sentTrials(i):

    random.shuffle(sentencepics)
    name = sentencepics[i]
    pic, file = name.split('.')
    sentencelist = pic.split('_')
    agent = sentencelist[0]         # English agent
    verb = sentencelist[1]
    patient = sentencelist[2]

    return pic, agent, verb, patient

def doSentTraining(primOrder): # Specify the dominant word order for the participant ('OSV' or 'SOV')
    
    global strainingDf

    # because we need to repeat incorrect trials, must have own counter
    i = 0
    if primOrder == 'OSV':
        orderlist = ['OSV']*42 + ['SOV']*18
    else:
        orderlist = ['OSV']*18 + ['SOV']*42
    random.shuffle(orderlist)

    while i < 60:
        pic, engAgt, engVerb, engPat = sentTrials(i)
        agent = noncedict[engAgt]
        verb = noncedict[engVerb]
        patient = noncedict[engPat]
        order = orderlist[i] #random.choice(orderlist)
        
        response, correct, buttonA, buttonB = doSentTrainingTrial(agent, verb, patient, pic, order, i)
        
        if correct == 1:
            i += 1
        else:
            continue
            
        dico = {
            'suj':sujet,
            'trial':i,
            'order':primOrder,
            'agent':engAgt,
            'verb':engVerb,
            'patient':engPat,
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        strainingDf = strainingDf.append(trial)
    return

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
    possibleWords = ['melnog', 'bloffen', 'vaneep', 'klamen']#list containing the correct lexicon. You can also pass it as an argument tot he function depending on how variable this list is. It is the same across, I would leave it here.
    correctedWords = [spellcheckWord(word,possibleWords) for word in input]
    #output = ' '.join(correctedWords)# turn back into a string
    #print correctedWords
    return correctedWords


def typingTrial(win,image_path,verb=None):
    text=""
    shifton=0 # allows caps and ?'s etc
    instructions = visual.TextStim(win, text=typing_instructions,
        color="Black",units='norm',pos=[0,0.75], wrapWidth = 1.5, height=0.05)
    #you do not need the above line if you do not have any text displayed along with the image
    imageStim=visual.ImageStim(win, image=image_path, units='norm',pos=[0,0],autoLog=True)
    verbStim = visual.TextStim(
        win, 
        text = verb, 
        color = "Black", 
        units = 'norm', 
        pos=[0.5, -0.75], 
        font='Monaco'
    )
    while event.getKeys(keyList=['return'])==[]:
        #text = ""
        letterlist=event.getKeys(keyList=['q','w','e','r','t','y','u','i','o','p','a','s','d','f',
            'g','h','j','k','l','z','x','c','v','b','n','m','lshift','rshift','period','space','apostrophe','comma','1','slash','backspace'])
        for l in letterlist:
            if shifton:
                if l == 'space':
                    text+=' '
                elif l == 'slash':
                    text+='?'
                elif l == '1':
                    text+='!'
                elif len(l) > 1:
                    pass
                elif l !='backspace':
                    text+=l.upper()
                shifton=0
            elif shifton == 0:
        #if key isn't backspace, add key pressed to the string
                if len(l) > 1:
                    if l == 'space':
                       text+=' '
                    elif l == 'period':
                       text+='.'
                    elif (l == 'lshift') | (l == 'rshift'):
                       shifton=1
                    elif l == 'comma':
                       text+=','
                    elif l == 'apostrophe':
                       text+='\''
                    elif l == 'backspace':
                       text=text[:-1]
                    elif l == 'slash':
                       text+='/'
                    else:
                       pass
                elif l == '1':
                    pass
                else: # it would have to be a letter at this point
                    text+=l
                #otherwise, take the last letter off the string
        #continually redraw text onscreen until return pressed
        response = visual.TextStim(
            win, 
            text=text+'|',
            color="black",
            units = 'norm', 
            pos = [-0.25,-0.75], 
            font='Monaco'
        )
        response.setAutoDraw(True)
            # text=text+'|' adds a pipe after the typed text to signal where typing will start/continue    
        instructions.setAutoDraw(True)
        imageStim.setAutoDraw(True)
        verbStim.setAutoDraw(True)
        win.flip()
        response.setAutoDraw(False)
        instructions.setAutoDraw(False)
        imageStim.setAutoDraw(False)
        verbStim.setAutoDraw(False)
    return text#this allows you to assigned the response to a variable outside the function (e.g., to store it)

def processResponses(responsestr):
    '''Takes in participant response (str), strips the non-alpha characters (leaves white space),
    passes it to spellcheck, which uses levenshtein distance to match back to closest words from
    participant target language, retruns the processed/corrected nouns from that function'''

    regex = re.compile('[^a-zA-Z ]')
    responses = regex.sub('', responsestr)

    correctedNouns = spellcheckWords(responses)

    return correctedNouns

def whichWords(correctNouns, agt, pat):
    '''Check what nouns the participant used, determine word order, and return all of that juicy data'''

    if len(correctNouns) < 2: # Incase participant only types one word or nothing
        worder = 'NA' 
        nAgt = 'NA'
        nPat = 'NA'
        respAgt = 'NA'
        respPat = 'NA'
    else:
        noun1 = correctNouns[0]
        noun2 = correctNouns[1]
        
        if agt == noun1 or pat == noun2:
            worder = 'SOV'
            nAgt = noun1 #save nonce response
            nPat = noun2
            respAgt = reverseNDict[noun1] #save the English equivalent of the participants response 
            respPat = reverseNDict[noun2]
        elif agt == noun2 or pat == noun1:
            worder = 'OSV'
            nAgt = noun2
            nPat = noun1
            respAgt = reverseNDict[noun2]
            respPat = reverseNDict[noun1]
        else:
            nAgt = noun1
            nPat = noun2
            worder = 'NA'
            respAgt = reverseNDict[noun1] #save the English equivalent of the participants response 
            respPat = reverseNDict[noun2]
       
    return respAgt, respPat, nAgt, nPat, worder

def sentTesting(primOrder,test = 'Pre'):
    
    global stestingDf
    
    random.shuffle(sentencepics)
    #i = 0
    for i in range(30):

        pic, engAgt, engVerb, engPat = sentTrials(i)
        agent = noncedict[engAgt]      # Target nonce agent
        verb = noncedict[engVerb]       # Nonce verb
        patient = noncedict[engPat]     # Target nonce patient
        print agent, patient
        imagePath = pathToImages+pic+'.jpg'
        responses = typingTrial(win, imagePath, verb) # Initialize typing trial
        correctNouns = processResponses(responses)          # Pass str from typing to be cleaned of non-alpha chars
        respAgt, respPat, nAgt, nPat, wordOrd = whichWords(correctNouns, agent, patient) 
        # Get word order used by participant and what words they used in the trial
        
        if wordOrd == primOrder:
            domOrder = 1
        else:
            domOrder = 0
        dico = {
            'suj':sujet,
            'trial':i,
            'image':pic,
            'agent':engAgt,    # Intended nonce agt  
            'patient':engPat,# Intended nonce pat
            'response':responses,
            'nonPartAgt':nAgt, # Agent used by participant (in case different from intended in stim)
            'nonPartPat':nPat, # Patient used by participant (in case different from intended in stim)
            'verb':engVerb,        
            'expNvrb':verb,# Nonce verb
            'engPartAgt': respAgt, # English agent used by part
            'engPartPat': respPat, # English pat used by part
            'expNAgt':agent, 
            'expNPat':patient, 
            'responseOrder':wordOrd, # Word order used by participant
            'dominantOrder':domOrder,
            'pre/post':test
        }
        trial = pd.DataFrame([dico])
        stestingDf = stestingDf.append(trial)
    
    return

##########
# Interaction phase

def participantPrompt(pic, engAgt, engVerb, engPat, primOrder, i, computerOrder):
# Run interaction phase where participant is the director
    
    global partPromptDf

    agent = noncedict[engAgt]      # Target nonce agent
    verb = noncedict[engVerb]       # Nonce verb
    patient = noncedict[engPat]     # Target nonce patient 
    imagePath = pathToImages+pic+'.jpg'
    print agent, patient 
    responses = typingTrial(win, imagePath, verb)
    correctNouns = processResponses(responses)          # Pass str from typing to be cleaned of non-alpha chars
    respAgt, respPat, nAgt, nPat, wordOrd = whichWords(correctNouns, agent, patient) 
    # Get word order used by participant and what words they used in the trial
    
    successCount, compGuess = computerResp(computerOrder, engAgt, engVerb, engPat, nAgt, nPat, wordOrd, pic)
    if wordOrd == primOrder:
        domOrder = 0
    else:
        domOrder = 1

    dico = {
        'suj':sujet,
        'trial':i,
        'image':pic,
        'agent':engAgt,    # Eng agt  
        'patient':engPat,# Eng pat
        'response':responses,
        'nonPartAgt':nAgt, # Agent used by participant (in case different from intended in stim)
        'nonPartPat':nPat, # Patient used by participant (in case different from intended in stim)
        'verb':engVerb,        
        'expNvrb':verb,# Nonce verb
        'engPartAgt': respAgt, # English agent used by part
        'engPartPat': respPat, # English pat used by part
        'expNAgt':agent, # Intended nonce agent
        'expNPat':patient, # Intended nonce patient
        'responseOrder':wordOrd, # Word order used by participant
        'dominantOrder':domOrder,
        'correct':successCount,
        'partner guess':compGuess
    }
    trial = pd.DataFrame([dico])
    partPromptDf = partPromptDf.append(trial)

    return

def feedbackDisplay(x, pic = None):
    '''Give participant feedback based on success or failure of computer to recognize the correct image'''
    win.flip()
    t = random.randint(1,5) # Wait between 1 and 5 seconds before continuing and showing the feedback
    core.wait(t)
    visual.TextStim(win, text=x, color="black", wrapWidth=700, pos = (0,200)).draw()
    #win.flip()
    if pic != None:
        picObj = visual.ImageStim(
            win,
            image=pathToImages+pic+'.jpg',
            pos = (0, 0)
        )
        picObj.setAutoDraw(True)
        picObj.draw()
        picObj.setAutoDraw(False)
    else:
        pass

    win.flip()
    event.waitKeys()
    
    win.flip()

def computerResp(computerOrder, engAgt, engVerb, engPat, nAgt, nPat, wordOrd, pic):
    '''Take participant input and check to see if the words match based on trial image, nonce language, 
    and strict minority word order'''

    success = 0
    if nAgt == noncedict[engAgt] and nPat == noncedict[engPat]: # Correct if words and order match
        if wordOrd == computerOrder:
            success += 1
            feedbackDisplay(comm_success)
        else:                                               # If words match, but order is incorrect
            success += 0
            pic = engPat+'_'+engVerb+'_'+engAgt
            feedbackDisplay(comm_failed, pic)
    else:
        success += 0
        if wordOrd == 'NA':
            if engVerb == 'punch':
                pic = random.choice(punchlst)
            elif engVerb == 'kick':
                pic = random.choice(kicklst)
            elif engVerb == 'shoot':
                pic = random.choice(shootlst)
            else:
                pic = random.choice(pointlst)
            feedbackDisplay(comm_failed,pic)
        elif wordOrd == computerOrder:
            compAgt = reverseNDict[nAgt]
            compPat = reverseNDict[nPat]
            pic = compAgt+'_'+engVerb+'_'+compPat
            feedbackDisplay(comm_failed, pic)
        else:
            compAgt = reverseNDict[nPat]
            compPat = reverseNDict[nAgt]
            pic = compAgt+'_'+engVerb+'_'+compPat
            feedbackDisplay(comm_failed, pic)
    return success, pic 

def theOtherOnes(trialpics, engAgt, engPat):
#Sort images based on verb, agt and pat, generate lists for random selection of alternate stims
    agtother = []
    patother = []

    for p in trialpics:
        p, ext = p.split('.')
        tempP = p.split('_')
        agt = tempP[0]
        pat = tempP[2]
        if agt == engPat and pat == engAgt:
            opposite = p
        elif agt == engAgt and pat != engPat:
            agtother.append(p)
        elif pat == engPat and agt != engAgt:
            patother.append(p)
    return agtother, patother, opposite


def cpImages(engAgt, engPat, engVerb, pic):

    if engVerb == 'punch':          # Select correct list of stims based on verb
        trialpics = punchlst
    elif engVerb == 'point':
        trialpics = pointlst
    elif engVerb == 'kick':
        trialpics = kicklst
    else:
        trialpics = shootlst
    agtother, patother, opposite = theOtherOnes(trialpics, engAgt, engPat)

    trialImages = []
    
    trialImages.append(pic)         # Correct image
    trialImages.append(opposite)    # Correct elements, agt and pat reversed
    alt1 = random.choice(agtother)  # Random pic that has same verb and agt, but diff pat
    trialImages.append(alt1)
    alt2 = random.choice(patother)  # Random pic that has same verb and pat, but diff agt
    trialImages.append(alt2)
    return trialImages              # List of 4 pics for trial


def computerPrompt(pic, engAgt, engVerb, engPat, primOrder, i):

    global compPromptDf

    agent = noncedict[engAgt]
    verb = noncedict[engVerb]
    patient = noncedict[engPat]
    # Check assigned dominant word order for participant and use the opposite to generate prompt
    if primOrder == 'OSV':                      
        promptSent = agent+' '+patient+' '+verb
    else:
        promptSent = patient+' '+agent+' '+verb
    trialStims = cpImages(engAgt, engPat, engVerb, pic) # Get 4 images for the trial
    print pic
    random.shuffle(trialStims) # List of images for the trial, shuffle to randomize location on the screen
    image1 = trialStims[0]
    image2 = trialStims[1]
    image3 = trialStims[2]
    image4 = trialStims[3]
    
    visStims = [image1, image2, image3, image4]
    print visStims
    mouse.setVisible(True)
    #core.wait(1.0)
    win.flip()
    core.wait(1)
    pic1 = visual.ImageStim(
            win,
            image = pathToImages+image1+'.jpg',
            pos = (-300, -150)
    )
    pic2 = visual.ImageStim(
            win,
            image = pathToImages+image2+'.jpg',
            pos = (-300, 150)
    )
    pic3 = visual.ImageStim(
            win,
            image = pathToImages+image3+'.jpg',
            pos = (300, 150)
    )
    pic4 = visual.ImageStim(
            win,
            image = pathToImages+image4+'.jpg',
            pos = (300, -150)
    )

    matcher_images = [pic1, pic2, pic3, pic4]

    for image in matcher_images:
        image.setAutoDraw(True)

    win.flip()
    eng = visual.TextStim( #text that gets presented
        win,
        text=promptSent,
        color='black',
        pos=(0,400),
        height=36
    )
    eng.setAutoDraw(True)
    win.flip()

    clicked = False

    while not clicked:
        for n, image in enumerate(matcher_images):
            if mouse.isPressedIn(image):

                clicked = True

                responseImage = n

    win.flip()

    eng.setAutoDraw(False)
    for image in matcher_images:
        image.setAutoDraw(False)
    win.flip()

    partGuess = visStims[responseImage]
    print partGuess, responseImage
    successCount = participantFeedback(partGuess, pic) # Check if participant response is correct

    dico = {
        'suj':sujet,
        'trial':i,
        'prompt':promptSent,
        'image':pic,
        'part guess':partGuess,
        'correct':successCount
    }
    trial = pd.DataFrame([dico])
    compPromptDf = compPromptDf.append(trial)

    return

def participantFeedback(partGuess, pic):

    success = 0
    if partGuess == pic:
        success += 1
        feedbackDisplay(right_choice)
    else:
        success += 0
        feedbackDisplay(wrong_choice, pic)
    return success 

def initializeInteract(primOrder):

    i = 0
    if primOrder == 'OSV':
        computerOrder = 'SOV'
    else:
        computerOrder = 'OSV'

    for i in range(48):
        pic, engAgt, engVerb, engPat = sentTrials(i)
        if i%2 == 0:
             # Run trial with participant as director
            participantPrompt(pic, engAgt, engVerb, engPat, primOrder, i, computerOrder)
        else:
            #Run trial with computer as director
            computerPrompt(pic, engAgt, engVerb, engPat, primOrder, i)
        i += 1
    return


####################
#START UP PARAMETERS
try:
    expInfo = misc.fromFile('../data/lastParams.pickle')
except:
    expInfo = {
        'ID':'O',
        'Subject number':'001',
        'Booth code':'0',
        'Gender':'X',
        'Age':0,
    }

sujet = '{}{}{}'.format(expInfo['ID'], expInfo['Booth code'], expInfo['Subject number'])

print type(sujet), sujet

genre = expInfo['Gender']
age = expInfo['Age']

datum = data.getDateStr(format="%Y-%m-%d %H:%M")

# dialogue box
dlg = gui.DlgFromDict(expInfo, title='Start parameters')
if dlg.OK:    
    misc.toFile('../data/lastParams.pickle', expInfo)
else:
    core.quit()

nonce_nouns = ['melnog', 'bloffen', 'vaneep', 'klamen']

nonce_verbs = ['dof', 'pouz','kass','zeeb']

engdict = {'shoot': 'verb', 'artist': 'noun', 'point': 'verb', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun','boxer':'noun'}


p = re.compile('.*\.jpg')
pathToImages = ('../stimuli/images/')


allFiles = os.listdir(pathToImages) # list all files in a certain directory

images = [] # create a list of images in the images folder (automatically!)
for f in allFiles:
    if p.match(f):
        images.append(f)

primOrder = getPartOrder(sujet)
sentencepics, nounpics = findStimImage()
noncedict, nouns = simplifyThatDictionary()
punchlst, pointlst, kicklst, shootlst = sortVerbImages()
reverseNDict = reverseDict()

win = visual.Window(
    [1200,1000],
    color="white",
    colorSpace="rgb",
    units="pix",
)

mouse = event.Mouse(visible=False)  # create mouse object that is invisible

buttonWidth = 280
buttonHeight = -80

buttonPositions = {
    'A': (buttonWidth/2*-1, buttonHeight/2*5),
    'B': (buttonWidth/2, buttonHeight/2*5),
    # 'C': (buttonWidth/2*-1, buttonHeight/2*-5),
    # 'D': (buttonWidth/2, buttonHeight/2*-5)
}

hoverColor = 'lightgrey' # "#C0C0C0"
buttonColor = "white"

nounTrainingFileName = '../data/nounTraining/{}.csv'.format(sujet)
ntrainingCols = [
    'suj',
    'trial',
    'targetNoun',
    'engNoun',
    'buttonA',
    'buttonB',
    'response',
    'correct',
    'iteration'
]
ntrainingDf = pd.DataFrame(columns=ntrainingCols)

sentTrainingFileName = '../data/sentTraining/{}.csv'.format(sujet)
strainingCols = [
    'suj',
    'trial',
    'order',
    'agent',
    'verb',
    'patient',
    'buttonA',
    'buttonB',
    'response',
    'correct'
]
strainingDf = pd.DataFrame(columns=strainingCols)


nounTestingFileName = '../data/nounTesting/{}.csv'.format(sujet)
nounTestingCols = [
    'suj',
    'trial',
    'correct_noun',
    'buttonA',
    'buttonB',
    'response',
    'correct',
    'iteration'
]
ntestingDf = pd.DataFrame(columns=nounTestingCols)

nounTypingFileName = '../data/nounTyping/{}.csv'.format(sujet)
nounTypingCols = [
    'suj',
    'trial',
    'correct_noun',
    'response',
    'image',
    'correct',
    'total_correct',
    'iteration' 
]
ntypingDf = pd.DataFrame(columns=nounTypingCols)

sentTestingFileName = '../data/sentTesting/{}.csv'.format(sujet)
stestingCols = [
    'suj',
    'trial',
    'image',
    'agent',
    'patient',
    'verb',
    'response',
    'nonPartAgt',
    'nonPartPat',
    'expNvrb',
    'engPartAgt',
    'engPartPat',
    'expNAgt',
    'expNPat',
    'responseOrder',
    'dominantOrder',
    'pre/post'
]
stestingDf = pd.DataFrame(columns=stestingCols)

partPromptFileName = '../data/partPrompt/{}.csv'.format(sujet)
partpromtCols = [
    'suj',
    'trial',
    'image',
    'agent',    # Eng agt  
    'patient',# Eng pat
    'response',
    'nonPartAgt', # Agent used by participant (in case different from intended in stim)
    'nonPartPat', # Patient used by participant (in case different from intended in stim)
    'verb',        
    'expNvrb',# Nonce verb
    'engPartAgt', # English agent used by part
    'engPartPat', # English pat used by part
    'expNAgt', # Intended nonce agent
    'expNPat', # Intended nonce patient
    'responseOrder', # Word order used by participant
    'dominantOrder',
    'correct',
    'partner guess'
]
partPromptDf = pd.DataFrame(columns=partpromtCols)

compPromptFileName = '../data/compPrompt/{}.csv'.format(sujet)
comptpromptCols = [
    'suj',
    'trial',
    'prompt',
    'image',
    'part guess',
    'correct'
]
compPromptDf = pd.DataFrame(columns=comptpromptCols)

############
# Instructions/dialogue

hello = u'''Hello, and welcome! You're about to learn part of a new language. There are four parts to the learning phase. 
First you'll learn the words of this language. 
Second is a very short test, just to see how much you've learned.
Third you'll see pictures with sentences in the new language describing them.
And fourth you'll have the opportunity to type in your own responses to describe scenes in the new language!

For some of these sections you will hear a native speaker say the word or sentence you're learning. In these sections, you're job is to match the word and image presented to the correct button on the bottom of the screen.
\n                      Let's get started!
                 Press the spacebar to continue
'''

between_nouns = u'''Well done! You've completed the first phase! Let's see what you remember. You will see a picture, and then respond by clicking on the button with the correct word.
\n
\n              Press the spacebar to continue'''

type_nouns = u'''Great! Now it's your turn to type the words!
\n
\n              Press the spacebar to continue'''

tryagain = u'''That was really good, but let's go over the words one more time.
\n
\n              Press the spacebar to continue'''

teststatement = u'''Nice job! Next you're going to see pictures of the words again and your job is to click on the button with the right word.
\n
\n              Press the spacebar to continue'''

sentences = u'''Now that you've learned the words, let's try some sentences. In this section you'll be shown a scene and our native speaker will describe it. You're job is to match what you see and the speaker's description to the phrases presented at the bottom of the screen.
\n
\n              Press the spacebar to continue'''

sentence_test = u'''For this part, you're task is to describe the scene using the nouns you've learned. The appropriate verb will be presented at the bottom of the screen under the image.
\n
\n              Press the spacebar to continue'''

thanksfornothing = u'''Thank you for participating, please let the experimenter know that you have finished'''

typing_instructions = u'''For the picture below, please type in the two words to describe the action taking place.
\n
\n              Press return/enter to continue'''

comm_success = u'''Well done! You're partner chose the correct scene!
\n
\n              Press the spacebar to continue'''

comm_failed = u'''Oops, not quite, your partner did not understand your description. This is what they thought you meant:
\n              Press the spacebar to continue'''

right_choice = u'''Good job! You chose the correct scene!
\n
\n           Press the spacebar to continue'''

wrong_choice = u'''Oh no! You did not understand your partner's description. This was the correct scene:
\n              Press the spacebar to continue'''

interaction_phase = u'''Congratulations on finishing the testing phase! For this next part you will be using the language you just learned to communicate with a partner. For half of the trials you will be shown a picture and asked to complete the description, which your partner will use to choose the correct scene. For the other half of the trials your task is to choose the correct scene based on your partner's description.
\nPlease wait while we match you with your partner.'''

last_test = u'''Just one more part to go! This last section is just a short test of your understanding, just like last time, for each scene, your task is to complete the sentence to describe the action.
\n
\n              Press the spacebar to continue'''

thankyou_complete = u'''Congratulations! You've reached the end of the experiment! Please let the researcher know that you have finished.'''

############
# RUN THE EXPERIMENT


#initializeInteract('OSV')

instructions(hello)

doNounTraining(sujet)
ntrainingDf.to_csv(nounTrainingFileName, index=None)

instructions(between_nouns)

doNounTesting(sujet)
ntestingDf.to_csv(nounTestingFileName, index=None)

instructions(type_nouns)
typeTheNouns(sujet)
ntypingDf.to_csv(nounTypingFileName, index=None)

# #doSentTraining('OSV')
strainingDf.to_csv(sentTrainingFileName, index=None)

# #sentTesting('OSV')
stestingDf.to_csv(sentTestingFileName, index=None)

partPromptDf.to_csv(partPromptFileName, index=None)

compPromptDf.to_csv(compPromptFileName, index=None)
core.quit()
