#Python Program to search string in text using Tkinter

from tkinter import *

#to create a window
root = Tk()

#root window is the parent window
fram = Frame(root)

#adding label to search box
Label(fram,text='Text to find:').pack(side=LEFT) 

#adding of single line text box
edit = Entry(fram) 

#positioning of text box
edit.pack(side=LEFT, fill=BOTH, expand=1) 

#setting focus
edit.focus_set() 

#adding of search button
butt = Button(fram, text='Find') 
butt.pack(side=RIGHT) 
fram.pack(side=TOP)

#text box in root window
text = Text(root) 

#text input area at index 1 in text window
text.insert('1.0','''Type your text here''') 
text.pack(side=BOTTOM)


#function to search string in text
def find():
	
	#remove tag 'found' from index 1 to END
	text.tag_remove('found', '1.0', END) 
	
	#returns to widget currently in focus
	s = edit.get() 
	if s:
		idx = '1.0'
		while 1:
			#searches for desired string from index 1
			idx = text.search(s, idx, nocase=1, 
							stopindex=END) 
			if not idx: break
			
			#last index sum of current index and
			#length of text
			lastidx = '%s+%dc' % (idx, len(s)) 
			
			#overwrite 'Found' at idx
			text.tag_add('found', idx, lastidx) 
			idx = lastidx
		#mark located string as red
		text.tag_config('found', foreground='orange') 
	edit.focus_set()
butt.config(command=find)

#mainloop function calls the endless loop of the window,
#so the window will wait for any 
#user interaction till we close it
root.mainloop() 

