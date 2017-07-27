#!/usr/bin/python
#Adam Sinck

#this will overlay the motion detector onto a color webcam

#this is a list of import commands. If the user doesn't have the
#necessary libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
    "import cv2 as cv",
    "import time"
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
#if there were any errors in the imports, tell the users what packages
#didn't import, and exit.
if len(failedPackages) > 0:
    print "Some packages could not be imported:"
    print failedPackages
    exit()

from motioncam import webcam
from webcamGUI import GUI

class motioneffects:
    #This is the main GUI. It takes a frame as an argument, which it
    #will embed everything into. Not real useful here because of USB
    #webcam limitations, but so it is. 
    def __init__(self):
        #init the webcam in its class
        self.webcam = webcam()

        #init the GUI, with a title
        self.GUI = GUI("Vampire Webcam")

        #get the frame that everything needs to pack into
        self.mainframe = self.GUI.getParentFrame()

        """
        +--------------------------+
        |[Color ]        [^ motion]|
        |[Motion]        [v motion]|
        |[ Both ]        [ invert ]|
        +--------------------------+
        """
        #Left options: change what's displayed.
        # ^ motion and v motion: change amount of motion capture output
        #invert: black on white or white on black motion display


        #some conditions and variables.
        self.color = True
        self.motion = False
        self.invert = False

        #add a couple buttons to toggle these

        self.colorButton = Button(self.mainframe, text="Color",
                                  command = lambda : self.changeDisplay("color"))

        self.motionButton = Button(self.mainframe, text="Motion",
                                   command = lambda : self.changeDisplay("motion"))
        self.bothButton = Button(self.mainframe, text="Both",
                                 command = lambda : self.changeDisplay("both"))
        
        self.ghostDownButton = Button(self.mainframe, text="Decrease Motion Ghosting",
                                      command = lambda : self.changeGhost(-1))
        self.ghostUpButton = Button(self.mainframe, text="Increase Motion Ghosting",
                                    command = lambda : self.changeGhost(1))
        self.invertButton = Button(self.mainframe, text="Invert Motion Frame",
                                   command = lambda : self.toggleInvert())


        for x in range(2):
            Grid.columnconfigure(self.mainframe, x, weight=1)

        for y in range(3):
            Grid.rowconfigure(self.mainframe, y, weight=1)
        
        self.colorButton.grid(     row=0, column=0, sticky=N+S+E+W )
        self.motionButton.grid(    row=1, column=0, sticky=N+S+E+W )
        self.bothButton.grid(      row=2, column=0, sticky=N+S+E+W )
        self.ghostDownButton.grid( row=0, column=1, sticky=N+S+E+W )
        self.ghostUpButton.grid(   row=1, column=1, sticky=N+S+E+W )
        self.invertButton.grid(    row=2, column=1, sticky=N+S+E+W )
        
        #put my stuff in the GUI
        self.GUI.packControls(self.mainframe)
        
        #start the stream
        self.mainframe.after(10, self.stream)

        #start the root mainloop
        self.GUI.run()

        
    #These are functions to toggle what the webcam's doing.
    
    def changeDisplay(self, option):
        if (option == "color"):
            self.color = True
            self.motion = False
            
        elif (option == "motion"):
            self.color = False
            self.motion = True

        else:
            self.color = True
            self.motion = True
            

    #This is for the amount of ghost to see
    def changeGhost(self, amount):
        self.webcam.setMotionLevel(self.webcam.motionLevel + amount)
        
        if (self.webcam.motionLevel == 2):
            self.ghostUpButton.config(state="disabled")
            self.ghostDownButton.config(state="normal")
        elif (self.webcam.motionLevel == 1):
            self.ghostUpButton.config(state="normal")
            self.ghostDownButton.config(state="normal")
        else:
            self.ghostUpButton.config(state="normal")
            self.ghostDownButton.config(state="disabled")


    #toggle if inversion is happening on motion frames
    def toggleInvert(self):
        self.invert = not self.invert

    #This is the "main" function. It does the streaming and processing.
    def stream(self):
        #take a new frame from the webcam
        self.webcam.takeFrame()
        frame = None
        
        if (self.color and not self.motion):
            frame = self.webcam.getFrame()

        #if we're only doing motion, then we're only doing motion
        elif (self.motion and not self.color):
            frame = self.webcam.motioncap(self.invert)
            frame = cv.cvtColor(frame, cv.COLOR_GRAY2BGR)
                
        #this is the fun one
        else: #both color and motion
            #take a frame and its inverse
            frame = self.webcam.getFrame()
            mask = self.webcam.motioncap(self.invert)
            
            if (not self.invert):
                _, mask = cv.threshold(mask, 10, 255, cv.THRESH_BINARY)
                
                mask = cv.bitwise_not(mask)
                frame = cv.bitwise_and(frame, frame, mask=mask)
                
            else:
                mask = cv.bitwise_not(mask)
                _, mask = cv.threshold(mask, 10, 255, cv.THRESH_BINARY)
                
                frame = cv.bitwise_and(frame, frame, mask=mask)

        #show the frame
        self.GUI.updateImage(frame)        
        
        #tell it to take another frame after five units of time
        self.mainframe.after(5, self.stream)


#start everything
if __name__ == "__main__":
    motioneffects()


