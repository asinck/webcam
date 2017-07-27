#!/usr/bin/env python
#Adam Sinck

#This program allows a user to take a picture of their background and
#use that as a background that they can fade to. 

#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
    "import cv2 as cv"
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


from webcam import webcam        
from webcamGUI import GUI


class vampire:
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

        self.background = self.webcam.frame

        #add a couple buttons to toggle these
        self.initButton = Button(self.mainframe, text="Set Background",
                                command = lambda : self.setBackground(None))

        # self.transparencyLabel = Label(text="transparency")
        self.transparencySlider = Scale(self.mainframe, from_=0, to=100, orient=HORIZONTAL)
        
        self.initButton.pack(side=LEFT, fill=BOTH, expand=YES)
        self.transparencySlider.pack(side=LEFT, fill=BOTH, expand=YES)

        #put my stuff in the GUI
        self.GUI.packControls(self.mainframe)
        
        #start the stream
        self.mainframe.after(10, self.stream)

        #start the root mainloop
        self.GUI.run()


        
    #This sets the background that the user can fade to.
    def setBackground(self, event):
        self.webcam.takeFrame()
        self.background = self.webcam.frame

    #This is the "main" function. It does the streaming and processing.
    def stream(self):
        #take a frame
        self.webcam.takeFrame()
        frame = self.webcam.frame

        #decide how much each of the background and the frame to display, and show that
        transparency = self.transparencySlider.get()
        cv.addWeighted(self.background, (transparency/100.0), frame,
                       (100-transparency)/100.0, 0.0, frame)

        #show the frame
        self.GUI.updateImage(frame)

        #tell it to take another frame after five units of time
        self.mainframe.after(5, self.stream)


if __name__ == "__main__":
    vampire()
