#!/usr/bin/env python
#Adam Sinck

#This program puts Cel shading on the webcam screen

#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
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

from webcam import webcam        
from webcamGUI import GUI

class cel:
    def __init__(self):

        #init the webcam in its class
        self.webcam = webcam()

        #init the GUI, with a title
        self.GUI = GUI("Cel Shading Webcam")

        #get the frame that everything needs to pack into
        self.mainframe = self.GUI.getParentFrame()
        
        #This is what does the Cel masking. The numbers are (2^n)-1
        #(for arbitrarily chosen values) of n so that when the mask is
        #bitwise or'd with a frame, it will convert the last bits of
        #the H, S, and V to 1's. This has the effect of rounding up to
        #certain numbers.
        self.mask = np.array([7, 31, 31])

        #some conditions and variables.
        #if we're doing cel shading right now
        self.cel = False
        #if we put edges on stuff
        self.edges = False
        #how much to smooth stuff
        self.blurLevel = 5

        #add a couple buttons to toggle these
        self.celButton = Button(self.mainframe, text="Toggle Cel Shading",
                                command = lambda : self.toggleCel(None))

        self.edgesButton = Button(self.mainframe, text="Toggle Edges",
                                  command = lambda :self.toggleEdges(None),
                                  state="disabled")
        
        self.celButton.pack(side=LEFT, fill=BOTH, expand=YES)
        self.edgesButton.pack(side=LEFT, fill=BOTH, expand=YES)

        #put my stuff in the GUI
        self.GUI.packControls(self.mainframe)
        
        #start the stream
        self.mainframe.after(10, self.stream)

        #start the root mainloop
        self.GUI.run()

    #These are functions to toggle what the webcam's doing.
    
    #Enable/disable cel shading. Also, a user should only be able to
    #toggle edges while cel shading is active. 
    def toggleCel(self, event):
        self.cel = not self.cel
        if (not self.cel):
            self.edgesButton.config(state="disabled")
        else:
            self.edgesButton.config(state="normal")

    #Enable/disable edges
    def toggleEdges(self, event):
        self.edges = not self.edges


    #This is the "main" function. It does the streaming and processing.
    def stream(self):
        #take a frame
        self.webcam.takeFrame()
        frame = self.webcam.frame

        #if we're doing cel shading
        if (self.cel):
            #get a copy of the frame in HSV, and mask it. The idea
            #here is to round the HSV values to certain increments, so
            #that there's a limited set of colors, saturations, and
            #values (brightnesses). A future version of this will
            #probably do things a little differently. Right now color
            #is still a little too dependent on saturation and value. 
            cel = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            frame = cv.bitwise_or(cel, self.mask)
            frame = cv.cvtColor(frame, cv.COLOR_HSV2BGR)

            #cv.GaussianBlur(, (3, 3), 0)

            #Denoise. A gaussian blur isn't suitable for this, because
            #I'm going for blotches of color instead of just putting
            #the frame a little out of focus. 
            frame = cv.medianBlur(frame, self.blurLevel)

            #if we're doing edge detection, do it
            if (self.edges):
                #Find the edges. 100 and 100 are magic values that
                #worked nicely for me. 
                edges = cv.Canny(frame, 100, 100)
                edges = cv.bitwise_not(edges)
                
                #put the edges on the frame
                frame = cv.bitwise_and(frame, frame, mask=edges)

                #show the frame
        self.GUI.updateImage(frame)

        #tell it to take another frame after five units of time
        self.mainframe.after(5, self.stream)


#start everything
if __name__ == "__main__":
    cel()

