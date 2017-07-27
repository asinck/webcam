#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
    "from PIL import Image, ImageTk",
    "import cv2 as cv",
    "import numpy as np"
]

#failedPackages will keep a record of the names of the packages that
#failed to import, so that the program can go through the entire list
#of packages that it wants to import. This will allow the program to
#give the user a complete list of packages that they need to install,
#instead of only telling the user one at a time.
failedPackages = ''
for i in imports:
    try:
        exec(i)
    except ImportError as error:
        failedPackages += str(error) + '\n'
#if there were any errors in the imports, tell the user what packages
#didn't import, and exit.
if len(failedPackages) > 0:
    print "Some packages could not be imported:"
    print failedPackages
    exit()


class GUI:
    #This is the main GUI. It takes a frame as an argument, which it
    #will embed everything into. Not real useful here because of USB
    #webcam limitations, but so it is. 
    def __init__(self, title):
        """
        +--------------------------+
        |                          |
        |                          |
        |          display         |
        |                          |
        |                          |
        +--------------------------+
        |---class defined content--|
        +--------------------------+
        """
        self.root = Tk()
        self.root.title(title)
        self.mainFrame = Frame(self.root)
        self.mainFrame.pack()

        
        #Two frames: The frame for the stream, and the frame for the
        #control panels. 
        self.displayFrame = Frame(self.mainFrame)
        self.controlFrame = Frame(self.mainFrame)
        self.displayFrame.pack(side=TOP)
        self.controlFrame.pack(side=BOTTOM, fill=X, expand=YES)
        self.controlPanel = None

        #The display is a label.
        self.display = Label(self.displayFrame)
        self.display.pack()
        
        #This is for working with the frames taken from the webcam. It
        #gets displayed on self.display.
        self.pictureframe = None
        

    #This function gets the frame that a class importing this GUI can pack into
    def getParentFrame(self):
        return self.controlFrame

    #This packs whatever the calling class provides.
    def packControls(self, frame):
        self.controlPanel = frame
        self.controlPanel.pack(fill=BOTH, expand=YES)

    #this takes a frame and displays it
    def updateImage(self, frame):        
        #convert the frame to something tk can use
        self.pictureframe = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(self.pictureframe)
        imgtk = ImageTk.PhotoImage(image=img)
        self.pictureframe = frame
        
        #put the image on the display
        self.display.imgtk = imgtk
        self.display.configure(image=imgtk)
        

    #this sets the window title
    def updateTitle(self, title):
        root.title(title)

    #this starts the mainloop
    def run(self):
        self.root.mainloop()
