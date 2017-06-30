#!/usr/bin/python
#Adam Sinck

#this will overlay the motion detector onto a color webcam

#this is a list of import commands. If the user doesn't have the
#necessary libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "from Tkinter import *",
    "import Tkinter as tk",
    "from PIL import Image, ImageTk",
    "import cv2 as cv",
    "import numpy as np",
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



#This is the class for the webcam. Right now, it doesn't do much, but
#in the future it might.
class webcam:
    def __init__(self):
        #initialize the webcam
        self.capture = cv.VideoCapture(0)
        #take a first frame
        self.frame0 = self.capture.read()[1]
        self.frame1 = self.capture.read()[1]
        self.frame2 = self.capture.read()[1]
        # self.height, self.width = self.t.shape[:2]

        #this tells how much motion to consider. 0 is strict, giving
        #only outlines. 2 is more blurry, giving a ghost
        #look. Anything above 2 is 2.
        self.motionLevel = 1
        
    #take a frame, and update the two previous frames
    def takeFrame(self):
        self.frame0 = self.frame1
        self.frame1 = self.frame2
        self.frame2 = self.capture.read()[1]

    #This returns the most current frame.
    def getFrame(self):
        return self.frame2

    #This sets how much motion to work with.
    def setMotionLevel(self, level):
        #force bounds
        if (level > 2):
            level = 2
        elif (level < 0):
            level = 0
            
        self.motionLevel = level
        

    #this will look at the difference between the last three frames
    def motioncap(self, invert=False):
        #convert frame1 to grayscale for the differences. This only
        #needs to be done here, because if no motion is being
        #processed then doing it for every frame would be a waste of
        #processing power.
        #I don't convert self.frame2 (the most recent frame) until the
        #function call, because that's still a frame that might be
        #used in its color form.
        #Check to make sure it's not RGB before we try to convert it.
        if (len(self.frame1.shape) == 3):
            self.frame1 = cv.cvtColor(self.frame1, cv.COLOR_RGB2GRAY)
        
        #take the difference of frames
        d1 = cv.absdiff(cv.cvtColor(self.frame2, cv.COLOR_RGB2GRAY), self.frame1)
        
        #combine the differences
        #"and" for an outline of movement, "or" for a ghost look. Not
        #doing either is in the middle. 
        frame = None
        if (self.motionLevel == 0):
            #Check to make sure it's not RGB before we try to convert it.
            if (len(self.frame0.shape) == 3):
                self.frame0 = cv.cvtColor(self.frame0, cv.COLOR_RGB2GRAY)
            d2 = cv.absdiff(self.frame1, self.frame0)
            frame = cv.bitwise_and(d1, d2)
        elif (self.motionLevel == 1):
            frame = d1
        else:
            #Check to make sure it's not RGB before we try to convert it.
            if (len(self.frame0.shape) == 3):
                self.frame0 = cv.cvtColor(self.frame0, cv.COLOR_RGB2GRAY)
            d2 = cv.absdiff(self.frame1, self.frame0)
            frame = cv.bitwise_or(d1, d2)
            
        #Black on white or white on black. Default: white on black.
        if (invert):
            return cv.bitwise_not(frame)
        else:
            return frame

class GUI:
    #This is the main GUI. It takes a frame as an argument, which it
    #will embed everything into. Not real useful here because of USB
    #webcam limitations, but so it is. 
    def __init__(self, frame):
        """
        +--------------------------+
        |                          |
        |                          |
        |          display         |
        |                          |
        |                          |
        +--------------------------+
        |[Color ]        [^ motion]|
        |[Motion]        [v motion]|
        |[ Both ]        [ invert ]|
        +--------------------------+
        """
        #Left options: change what's displayed.
        # ^ motion and v motion: change amount of motion capture output
        #invert: black on white or white on black motion display

        #Two frames: The frame for the stream, and the frame for the
        #control panels. 
        self.displayFrame = Frame(frame)
        self.controlFrame = Frame(frame)
        self.displayFrame.pack(side=TOP)
        self.controlFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        

        #The display is a label.
        self.display = Label(self.displayFrame)
        self.display.after(10, self.stream)
        self.display.pack()
        
        #This is for working with the frames taken from the webcam. It
        #gets displayed on self.display.
        self.pictureframe = None

        #init the webcam in its class
        self.webcam = webcam()

        #This is what does the Cel masking. The numbers are powers of
        #two minus 1, so that when the mask is bitwise or'd with a
        #frame, it will convert the last bits of the H, S, and V to 1's.
        self.mask = np.array([7, 31, 31])

        #some conditions and variables.
        self.color = True
        self.motion = False
        self.invert = False

        #add a couple buttons to toggle these

        self.colorButton = Button(self.controlFrame, text="Color",
                                  command = lambda : self.changeDisplay("color"))

        self.motionButton = Button(self.controlFrame, text="Motion",
                                   command = lambda : self.changeDisplay("motion"))
        self.bothButton = Button(self.controlFrame, text="Both",
                                 command = lambda : self.changeDisplay("both"))
        
        self.ghostDownButton = Button(self.controlFrame, text="Decrease Motion Ghosting",
                                      command = lambda : self.changeGhost(-1))
        self.ghostUpButton = Button(self.controlFrame, text="Increase Motion Ghosting",
                                    command = lambda : self.changeGhost(1))
        self.invertButton = Button(self.controlFrame, text="Invert Motion Frame",
                                   command = lambda : self.toggleInvert())


        for x in range(2):
            Grid.columnconfigure(self.controlFrame, x, weight=1)

        for y in range(3):
            Grid.rowconfigure(self.controlFrame, y, weight=1)
        
        self.colorButton.grid(     row=0, column=0, sticky=N+S+E+W )
        self.motionButton.grid(    row=1, column=0, sticky=N+S+E+W )
        self.bothButton.grid(      row=2, column=0, sticky=N+S+E+W )
        self.ghostDownButton.grid( row=0, column=1, sticky=N+S+E+W )
        self.ghostUpButton.grid(   row=1, column=1, sticky=N+S+E+W )
        self.invertButton.grid(    row=2, column=1, sticky=N+S+E+W )
        
        
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

                
        #convert the frame to something tk can use
        self.pictureframe = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        img = Image.fromarray(self.pictureframe)
        imgtk = ImageTk.PhotoImage(image=img)
        self.pictureframe = frame
        
        #put the image on the display
        self.display.imgtk = imgtk
        self.display.configure(image=imgtk)
        
        #tell it to take another frame after five units of time
        self.display.after(5, self.stream)


#start everything
def main():
    root = Tk()
    root.title("Motion Effects Webcam")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()


if __name__ == "__main__":
    main()

