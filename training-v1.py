# -*- coding: utf-8 -*-

import pandas as pd
from psychopy import core, visual, event
import os, re, random

# don't put anything except imports in this block...try to keep your code as clean as possible

##########
# FUNCTIONS

'''
This block is where you'll define the functions you'll use in the experiment.
Try not to mix the actual experiment with the functions.  Keeping them
seperate makes it easier to keep track of things.
'''


def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    for i in range(len(nonce_words)):
        newlanguage[(engdictKeys[i],engdict[engdictKeys[i]])] = nonce_words[i] 
        # Make a dictionary that has a tuple (Engword, function) as key and nonce word as value
    return newlanguage


def findStimImage():
    '''Gather the images for the single nouns and sentences into lists'''

    nounpics = []
    sentencepics = []
    #engdictKeys = list(engdict.keys())
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

    # noncedict = {}
    
    nldict = participantLang() # Generate random nonce language for new participant
    nlkeys = list(nldict.keys()) # Make a list of the dictionary keys to iterate over in the next line

    for i in range(len(nlkeys)):
        noncedict[nlkeys[i][0]] = nldict[nlkeys[i]] # Make a dictionary that has an english word as the key and the nonce word as the value
    return noncedict


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

def doTrainingTrial(noun, wrongNoun, engNoun, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.5)
    
    # Get the correct nonce word and an incorrect one for the training
    engText = noun # Leaving this here until I have the audio stims
    target = noun # Correct word that matches image
    miss = wrongNoun # Random nonce word that does not match image, but is in the experimental language

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, cons, eng, noun = initializeTrial(
        displayText=engText,
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


def doTraining():

    # trainingDf will be updated by the function, so must be global
    #global trainingDf
    simplifyThatDictionary()
    sentencepics, nounpics = findStimImage()
    # because we need to repeat incorrect trials, must have own counter
    i = 0

    # until counter reaches 16 correct trials, loop

    ### ALEX: SHOW MARY HOW TO USE WHILE OR FOR NOT BOTH ###
    
    while i < 16: # 16
        # recover mod (the row includes category and number info)
        random.shuffle(nounpics)
        for pic in nounpics:
            name, file = pic.split('.')
            nounlist = name.split('_')
            engNoun = nounlist[0]
            nounWord = noncedict[engNoun]
            otherNonce = random.choice(nonce_words) # Randomly choose a word from the nonce list to be the alternative button
            if otherNonce != nounWord: # Make sure the buttons aren't assigned the same word
        # do the trial and recover button content
                response, correct, buttonA, buttonB = doTrainingTrial(nounWord, otherNonce, engNoun, i)
            else: 
                pass

        # if trial correct, move on, else repeat
            if correct == 1:
                i += 1
            else:
                continue

#        dico = {
#            'suj':sujet,
#            'trial':i,
#            'noun':nounWord,
#            'modifier':modifierWord,
#            'buttonA':buttonA,
#            'buttonB':buttonB,
#            'response':response,
#            'correct':correct
#        }
        #trial = pd.DataFrame([dico])
        #trainingDf = trainingDf.append(trial)
            
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

engdict = {'shoot': 'verb', 'ball': 'object', 'police': 'agent', 'doctor': 'agent',
           'artist': 'agent', 'point': 'verb ', 'punch': 'verb', 'cake': 'object', 'burglar': 'agent',
           'tophat': 'object', 'kick': 'verb', 'jug':'object'}

p = re.compile('.*\.jpg')
pathToImages = ('../stimuli/images/')

noncedict = {}


allFiles = os.listdir(pathToImages) # list all files in a certain directory

images = [] # create a list of images in the images folder (automatically!)
for f in allFiles:
    if p.match(f):
        images.append(f)


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

#trainingFileName = '../data/training/{}.csv'.format(sujet)
#trainingCols = [
#    'suj',
#    'trial',
#    'noun',
#    'modifier',
#    'buttonA',
#    'buttonB',
#    'response',
#    'correct'
#]
#trainingDf = pd.DataFrame(columns=trainingCols)

##########
# RUN THE EXPERIMENT

#simplifyThatDictionary()

doTraining()
core.quit()









