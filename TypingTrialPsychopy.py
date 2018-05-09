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
