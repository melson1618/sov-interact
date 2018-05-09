# -*- coding: utf-8 -*-

import pandas as pd
from psychopy import core, visual, event
import os, re, random


##########
#Dummy variables, change later

sujet=1

##########
# FUNCTIONS


def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    for i in range(len(nonce_words)):
        newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nonce_words[i] 
        # Make a dictionary that has a tuple (Engword, function) as key and nonce word as value
    return newlanguage, engdictKeys


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


def simplifyThatDictionary():
    '''Pull out just the nonce-English word pairs and create a new dictionary to be used in doTraining'''
    
    nldict, engKeys = participantLang() # Generate random nonce language for new participant, return a list of the english keys 
    nlkeys = list(nldict.keys()) # Make a list of the dictionary keys to iterate over in the next line
    nouns = [] # List for the nouns, needed to randomize incorrect noun in doNounTraining
    noncedict = {}
    for i in range(len(engKeys)):
        if engdict[engKeys[i]] in ['agent','object']: # Make a list of the nouns for later on when the program needs a random noun
            nouns.append(engKeys[i])
    for i in range(len(nlkeys)):
        noncedict[nlkeys[i][0]] = nldict[nlkeys[i]] # Make a dictionary that has an english word as the key and the nonce word as the value
    return noncedict, nouns # English:nonce


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


def getClick(mouse, buttons, cons, eng):

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


def initializeTrial(displayText, buttonNames, buttonTexts, pic):

    # create mouse object (not active yet)
    mouse = event.Mouse(visible=False)
    
    win.flip()
   
    # draw text stimulus and consigne
    cons = visual.TextStim(
        win,
        text="Phrase to be translated:",
        color="black",
        pos=(0,260),
        height=16
    )
    cons.setAutoDraw(True)
    cons.draw()
    
    eng = visual.TextStim(
        win,
        text=displayText,
        color='black',
        pos=(0,200),
        height=36
    )
    eng.setAutoDraw(True)
    eng.draw()
    
    picObj = visual.ImageStim(
        win,
        image=pathToImages+pic+'.jpg'
    )
    picObj.setAutoDraw(True)
    picObj.draw()
    
    # create button objects (they will keep drawing themselves until turned off)
    buttonsAssc = {}
    for n,i in enumerate(buttonNames):
        buttonsAssc[i] = buttonTexts[n]

    buttons = [makeButton(location, buttonsAssc[location]) for location in buttonsAssc.keys()]
        
        
    win.flip()
    
    return mouse, buttons, cons, eng, picObj

def doNounTestTrial(noun, wrongNoun, engNoun, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.5)
    
    # Get the correct nonce word and an incorrect one for the training
    nonceText = noun # Leaving this here until I have the audio stims
    target = noun # Correct word that matches image
    miss = wrongNoun # Random nonce word that does not match image, but is one of the nouns from the nonce language

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, cons, eng, noun = initializeTrial(
        displayText= None,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = engNoun
    )

    # make and play sound objects based on the English'     # Will be using this later once I have generated the audio
#    stims = makePhrase([noun, modifier])
#    for stim in stims:
#        playStim(stim)

    # wait 500 ms after sound
    core.wait(0.5)

    consBisText = "...click on the choice that matches what you heard... ({}/16)".format(nTrial+1)
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
    responseButton, response = getClick(mouse, buttons, cons, eng)

    # check to see that participant selected the postnominal variant
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
    cons.setAutoDraw(False)
    eng.setAutoDraw(False) 
    consBis.setAutoDraw(False)

    
    return response, correct, buttonTexts[0], buttonTexts[1]


def doNounTesting():

    # trainingDf will be updated by the function, so must be global
    global ntestingDf
    # because we need to repeat incorrect trials, must have own counter
    random.shuffle(nounpics)
    i = 0
    while i < 5:
        pic = nounpics[i]
        name, file = pic.split('.')
        nounlist = name.split('_') # 
        engNoun = nounlist[0]
        nounWord = noncedict[engNoun]
        otherWord = random.choice(nouns)
        otherNonce = noncedict[otherWord] # Randomly choose a word from the nonce list to be the alternative button
        if otherNonce != nounWord: # Make sure the buttons aren't assigned the same word
            #print "Look, I made it!"
    # do the trial and recover button content
            response, correct, buttonA, buttonB = doNounTestTrial(nounWord, otherNonce, engNoun, i)
        else: 
            pass
        i += 1
    # if trial correct, move on, else repeat
#        if correct == 1:
#            i += 1
#            print i
#        else:
#            continue
                
    
        dico = {
            'suj':sujet,
            'trial':i,
            'correct_noun':nounWord,
            #'modifier':modifierWord,
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        ntestingDf = ntestingDf.append(trial)
            
    return

def doSentTrainingTrial(agtWord, objWord, vrbWord, sentence, order, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.5)
    
    orderSOV = agtWord+' '+objWord+' '+vrbWord
    orderOSV = objWord+' '+agtWord+' '+vrbWord
    # Get the correct nonce sentence and an incorrect one for the training
    if order == 'OSV':  # Correct word order for participant
        nonceText = orderOSV
        target = orderOSV
        miss = orderSOV
    else:
        nonceText = orderSOV
        target = orderSOV
        miss = orderOSV
    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, cons, eng, noun = initializeTrial(
        displayText=None,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = sentence
    )

    # make and play sound objects based on the English'     # Will be using this later once I have generated the audio
#    stims = makePhrase([noun, modifier])
#    for stim in stims:
#        playStim(stim)

    # wait 500 ms after sound
    core.wait(0.5)

    consBisText = "...click on the choice that matches what you heard... ({}/30)".format(nTrial+1)
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
    responseButton, response = getClick(mouse, buttons, cons, eng)

    # check to see that participant selected the postnominal variant
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
    cons.setAutoDraw(False)
    eng.setAutoDraw(False) 
    consBis.setAutoDraw(False)

    print order 
    return response, correct, buttonTexts[0], buttonTexts[1]


def doSentTraining(primOrder): # Specify the dominant word order for the participant ('OSV' or 'SOV')
    
    global stestingDf
    # because we need to repeat incorrect trials, must have own counter
    i = 0
    if primOrder == 'OSV':
        orderlist = ['OSV']*7 + ['SOV']*3
    else:
        orderlist = ['OSV']*3 + ['SOV']*7
    random.shuffle(orderlist)
    # until counter reaches 30 correct trials, loop

    random.shuffle(sentencepics)

    while i < 5:
        pic = sentencepics[i]
        name, file = pic.split('.')
        sentencelist = name.split('_')
        agent = noncedict[sentencelist[0]]
        verb = noncedict[sentencelist[1]]
        object = noncedict[sentencelist[2]]
        order = orderlist[i] #random.choice(orderlist)
        
        response, correct, buttonA, buttonB = doSentTrainingTrial(agent, verb, object, name, order, i)
        i+= 1
#        if correct == 1:
#            i += 1
#        else:
#            continue
            
        dico = {
            'suj':sujet,
            'trial':i,
            'order':primOrder,
            'trialorder':order,
            'agent':sentencelist[0],
            'verb':sentencelist[1],
            'object':sentencelist[2],
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        stestingDf = stestingDf.append(trial)
    return

##########
# START UP PARAMETERS

'''
These are the parameters that are static and used throughout the experiment.

Things like button sizes and whatnot can be defined in this block and then referenced
throughout the experiment.  You'll also know where they live for when you want to change
them.
'''

nonce_words = ['spargin', 'preg', 'dof', 'geedar', 'narg', 'zib',
               'kass', 'bloffen', 'slegam', 'nergid', 'wanip', 'drim']

engdict = {'shoot': 'verb', 'police': 'noun', 'doctor': 'noun',
           'artist': 'agent', 'point': 'verb ', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun','boxer':'noun'}

newnonceDict = {'ball':'sphero','police':'copi','doctor':'heelper','artist':'pinta',
                'cake':'isee','burglar':'theefo','tophat':'hedan','jug':'sloshin'}


p = re.compile('.*\.jpg')
pathToImages = ('../stimuli/images/')



allFiles = os.listdir(pathToImages) # list all files in a certain directory

images = [] # create a list of images in the images folder (automatically!)
for f in allFiles:
    if p.match(f):
        images.append(f)

sentencepics, nounpics = findStimImage()
noncedict, nouns = simplifyThatDictionary()

win = visual.Window(
    [800,800],
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
    'C': (buttonWidth/2*-1, buttonHeight/2*-1),
    'D': (buttonWidth/2, buttonHeight/2*-1)
}

hoverColor = 'lightgrey' # "#C0C0C0"
buttonColor = "white"

nounTestingFileName = '../data/nounTesting/{}.csv'.format(sujet)
nounTestingCols = [
    'suj',
    'trial',
    'correct_noun',
    #'modifier',
    'buttonA',
    'buttonB',
    'response',
    'correct'
]
ntestingDf = pd.DataFrame(columns=nounTestingCols)

verbTestingFileName = '../data/sentTesting/{}.csv'.format(sujet)
stestingCols = [
    'suj',
    'trial',
    'order',
    'agent',
    'verb',
    'obj',
    'buttonA',
    'buttonB',
    'response',
    'correct'
]
stestingDf = pd.DataFrame(columns=stestingCols)

############
# RUN THE EXPERIMENT


doNounTesting()
ntestingDf.to_csv(nounTestingFileName, index=None)

#doSentTesting('OSV')
#stestingDf.to_csv(verbTestingFileName, index=None)
core.quit()