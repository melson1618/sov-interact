# -*- coding: utf-8 -*-

import pandas as pd
from psychopy import core, visual, event, sound
import os, re, random
import pickle
import numpy as np


##########
#Dummy variables, change later

sujet= 'OSV001'

##########
# FUNCTIONS

def instructions(x):
    'Display instructions on screen and wait for participant to press button'
    win.flip()
    visual.TextStim(win, text=x, color="black", wrapWidth=800).draw()
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


def participantLang():
    '''Create language for participant from list of nonce words and English words/grammatical roles, probably need to save
    this to a file somewhere, but honestly not even close to there yet'''

    newlanguage = {}  # Dictionary for language for participant, (English, function):nonce
    engdictKeys = list(engdict.keys())
    random.shuffle(engdictKeys) # Randomize language for each participant
    random.shuffle(nonce_nouns)
    random.shuffle(nonce_verbs)
    for i in range(10):
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
    nlkeys = list(nldict.keys()) # Make a list of the dictionary keys to iterate over in the line 65
    nouns = [] # List for the nouns, needed to randomize incorrect noun in doNounTraining
    noncedict = {}
    for i in range(len(engKeys)):
        if engdict[engKeys[i]] == 'noun': # Make a list of the nouns for later on when the program needs a random noun
            nouns.append(engKeys[i])
    for i in range(len(nlkeys)):
        noncedict[nlkeys[i][0]] = nldict[nlkeys[i]] # Make a dictionary that has an english word as the key and the nonce word as the value
    pickle.dump(noncedict, open('../data/part_dict/{}-langDict.csv'.format(sujet), 'w+'))
    return noncedict, nouns # noncedict = {English:nonce}


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
        image=pathToImages+pic+'.jpg'
    )
    picObj.setAutoDraw(True)
    picObj.draw()
    win.flip()

    core.wait(0.5)
    # make and play sound objects based on the nonce language of the participant'
    stims = makePhrase(audioStim)
    for stim in stims:
        playStim(stim)

    core.wait(0.5)
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

    # create button objects (they will keep drawing themselves until turned off)
    buttonsAssc = {}
    for n,i in enumerate(buttonNames):
        buttonsAssc[i] = buttonTexts[n]

    buttons = [makeButton(location, buttonsAssc[location]) for location in buttonsAssc.keys()]
        
        
    win.flip()
    
#    return mouse, buttons, cons, eng, picObj
    return mouse, buttons, eng, picObj


def makePhrase(words):
    # make list of sound objects based on words
    stimulus = [sound.Sound('../stimuli/audio/'+i+'.wav') for i in words]

    return stimulus

def typing_trial(win,image_path,instructions):
	text=""
	shifton=0 # allows caps and ?'s etc
	instructions = visual.TextStim(win, text=instructions,color="DimGray",units='norm',pos=[0,0.75], wrapWidth = 1.5)
	#you do not need the above line if you do not have any text displayed along with the image
	image_stim=visual.ImageStim(win, image=image_path, units='norm',pos=[0,0],autoLog=True)
	while event.getKeys(keyList=['return'])==[]:
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
		response = visual.TextStim(win, text=text+'|',color="black",units = 'norm', pos = [0,-0.75] )
		# text=text+'|' adds a pipe after the typed text to signal where typing will start/continue    
		response.draw()
		instructions.draw()
		image_stim.draw()
		win.flip()
	return text #this allows you to assigned the response to a variable outside the function (e.g., to store it)


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


def doNounTraining(sujet, repeat=0):

    # ntrainingDf will be updated by the function, so must be global
    global ntrainingDf
    
    loop = 0
    while loop < 1: # Iterate through the nouns 5 times, randomizing the order of the nouns within each iteration
        random.shuffle(nouns) # Randomize order for presentation of nouns in training
        i = 0 # because we need to repeat incorrect trials, must have own counter
        while i < 6: # Iterate through entire noun list once
            engNoun = nouns[i]
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
                print i
            else:
                continue

            dico = {
                'suj':sujet,
                'trial':i,
                'correct_noun':nounWord,
                'buttonA':buttonA,
                'buttonB':buttonB,
                'response':response,
                'correct':correct,
                'iteration':repeat
            }
            trial = pd.DataFrame([dico])
            ntrainingDf = ntrainingDf.append(trial)
        loop += 1 # Update loop count after each successful completion of all 6 nouns in a training block
    return


def doNounTestTrial(noun, wrongNoun, engNoun, nTrial):

    # wait 500 ms at beginning of trial
    core.wait(0.5)
    
    # Get the correct nonce word and an incorrect one for the testing
    target = noun # Correct word that matches image
    miss = wrongNoun # Random nonce word that does not match image, but is one of the nouns from the nonce language

    buttonTexts = [target, miss]
    # mix up button texts
    random.shuffle(buttonTexts)

    # create mouse and button objects, display instructions
    mouse, buttons, eng, pic = initializeTrial(
        displayText= target,
        buttonNames=['A', 'B'],
        buttonTexts=['-----'] * len(buttonTexts),
        pic = engNoun,
        audioStim = ['none']
    )

    # wait 500 ms after sound
    core.wait(0.5)

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


def doNounTesting(sujet):

    # ntestingDf will be updated by the function, so must be global
    global ntestingDf
    loop = 0
    num_correct = 0

    numberBlocks = 2
    testNouns = []
    for block in range(numberBlocks):
        blockNouns = list(np.copy(nouns))
        random.shuffle(blockNouns)
        testNouns.append(blockNouns)

    testNouns = testNouns[0] + testNouns[1] # don't do this normally
    
    for n,nounWord in enumerate(testNouns): # Show each noun once in each testing block
        engNoun = noncedict[nounWord]
        otherWord = random.choice(nouns)
        otherNonce = noncedict[otherWord] # Randomly choose a word from the nonce list to be the alternative button
        if otherNonce != nounWord: # Make sure the buttons aren't assigned the same word
    # do the trial and recover button content
            response, correct, buttonA, buttonB = doNounTestTrial(nounWord, otherNonce, engNoun, n)
            num_correct += correct
            print num_correct
        else: 
            continue

        dico = {
            'suj':sujet,
            'trial':n,
            'correct_noun':nounWord,
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        ntestingDf = ntestingDf.append(trial)
    print num_correct
    checkLearning(num_correct, sujet) # Check to see if participant got at least 75% correct
    return

def checkLearning(numCorrect, suj):
    '''Check how many of the noun testing trials participant got correct, if it is less than 75% (9) repeat nounTraining, 
    unless they've already been through it twice'''

    if '-2' in suj: # Check to see if they're already done it twice
        if numCorrect < 9:
            instructions(thanksfornothing)
        else:
            pass
    elif numCorrect < 9: # If they got less than 75% correct, repeat training
        instructions(tryagain)
        suj = suj+'-2'
        doNounTraining(suj, repeat=1)
        instructions(teststatement)
        doNounTesting(suj)
    else:
        pass
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
    mouse, buttons, eng, noun = initializeTrial(
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

    print order 
    return response, correct, buttonTexts[0], buttonTexts[1]


def doSentTraining(primOrder): # Specify the dominant word order for the participant ('OSV' or 'SOV')
    
    global strainingDf

    # because we need to repeat incorrect trials, must have own counter
    i = 0
    if primOrder == 'OSV':
        orderlist = ['OSV']*7 + ['SOV']*3
    else:
        orderlist = ['OSV']*3 + ['SOV']*7
    random.shuffle(orderlist)

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
        
        if correct == 1:
            i += 1
        else:
            continue
            
        dico = {
            'suj':sujet,
            'trial':i,
            'order':primOrder,
            'agent':sentencelist[0],
            'verb':sentencelist[1],
            'object':sentencelist[2],
            'buttonA':buttonA,
            'buttonB':buttonB,
            'response':response,
            'correct':correct
        }
        trial = pd.DataFrame([dico])
        strainingDf = strainingDf.append(trial)
    return

def processResponses(textResponse):
    response = textResponse.strip()
    
def sentTesting():
    
    global stestingDf
    
    random.shuffle(sentencepics)
    i = 0
    while i < 5:
        pic = sentencepics[i]
        name, file = pic.split('.')
        sentencelist = name.split('_')
        agent = noncedict[sentencelist[0]]
        verb = noncedict[sentencelist[1]]
        object = noncedict[sentencelist[2]]
        imagePath = pathToImages+pic+'.jpg'
        text = typing_trial(win, imagePath, instruction)
        
        dico = {
            'suj':sujet,
            'trial':i,
            'image':pic,
            'agent':sentencelist[0],
            'verb':sentencelist[1],
            'patient':sentencelist[2],
            'response':text,
        }
        trial = pd.DataFrame([dico])
        stestingDf = stestingDf.append(trial)
    return

##########
# START UP PARAMETERS


nonce_nouns = ['melnog', 'bloffen', 'neegoul', 'vaneep', 'klamen', 'slegam']

nonce_verbs = ['dof', 'pouz','kass','zeeb']

engdict = {'shoot': 'verb', 'police': 'noun', 'doctor': 'noun',
           'artist': 'noun', 'point': 'verb', 'punch': 'verb', 'burglar': 'noun',
           'kick': 'verb', 'clown':'noun','boxer':'noun'}


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

nounTrainingFileName = '../data/nounTraining/{}.csv'.format(sujet)
ntrainingCols = [
    'suj',
    'trial',
    'correct_noun',
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
    'obj',
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
    'correct'
]
ntestingDf = pd.DataFrame(columns=nounTestingCols)

sentTestingFileName = '../data/sentTesting/{}.csv'.format(sujet)
stestingCols = [
    'suj',
    'trial',
    'image',
    'agent',
    'verb',
    'obj',
    'response',
]
stestingDf = pd.DataFrame(columns=stestingCols)
############
# Instructions/dialogue

hello = u'''Hello, and welcome! I need to add more to this bit about what to actually do'''

between_nouns = u'''Well done! You've completed the first phase! Let's see what you remember'''

tryagain = u'''That was really good, but let's go over the words one more time'''

teststatement = u'''Something encouraging about finishing nouns again'''

sentences = u'''Now that you've learned the words, let's try some sentences'''

sentence_test = u'''Type a sentence to describe the image'''

thanksfornothing = u'''Thank you for participating, please let the experimenter know that you have finished'''
############
# RUN THE EXPERIMENT

instructions(hello)

# doNounTraining(sujet)
# ntrainingDf.to_csv(nounTrainingFileName, index=None)

instructions(between_nouns)

doNounTesting(sujet)
ntestingDf.to_csv(nounTestingFileName, index = None)

instructions(sentences)

doSentTraining('OSV')
strainingDf.to_csv(sentTrainingFileName, index=None)

#instructions(sentence_test)


core.quit()
