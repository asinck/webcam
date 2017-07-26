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


#This is the class for the webcam. Right now, it doesn't do much, but
#in the future it might.
class webcam:
    def __init__(self):
        self.config = None
        self.variables = {'webcam':'0'}
        try:
            #open the config file
            self.config = open("config.conf", 'r')
            #go through each line
            for line in self.config:
                myline = line.strip()
                #check that it's not a comment, and that it contains
                #an equal sign
                if (len(myline) > 0 and myline[0] != '#' and '=' in myline):
                    #grab the variables, removing any comments
                    myline = myline.split("#")[0].strip()
                    myline = myline.split("=")
                    self.variables[myline[0].strip()] = ' '.join(myline[1:]).strip()
            self.config.close()

        #if there's no config file, close
        except:
            self.config = open("config.conf", 'w+')
            self.config.write("webcam=0")
            self.config.close()

        #initialize the webcam
        self.capture = None
        try:
            self.capture = cv.VideoCapture(int(self.variables["webcam"]))
            # self.capture = cv.VideoCapture(int(variables["webcam"]))
        except:
            print "Unable to open webcam specified in config. Opening"
            print "default webcam instead."
            self.capture = cv.VideoCapture(0)

        #take a first frame
        self.frame = self.capture.read()[1]
        # self.height, self.width = self.t.shape[:2]

    def takeFrame(self):
        #take a frame
        self.frame = self.capture.read()[1]
        

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
        |[Toggle Cel][Toggle Edges]|
        +--------------------------+
        """

        #Two frames: The frame for the stream, and the frame for the
        #control panels. 
        self.displayFrame = Frame(frame)
        self.controlFrame = Frame(frame)
        self.displayFrame.pack(side=TOP)
        self.controlFrame.pack(side=BOTTOM, fill=X, expand=YES)


        #The display is a label.
        self.display = Label(self.displayFrame)
        self.display.after(10, self.stream)
        self.display.pack()
        
        #This is for working with the frames taken from the webcam. It
        #gets displayed on self.display.
        self.background = None
        self.pictureframe = None

        #init the webcam in its class
        self.webcam = webcam()
        self.webcam.takeFrame()
        self.background = self.webcam.frame

        #add a couple buttons to toggle these
        self.initButton = Button(self.controlFrame, text="Set Background",
                                command = lambda : self.setBackground(None))

        # self.transparencyLabel = Label(text="transparency")
        self.transparencySlider = Scale(self.controlFrame, from_=0, to=100, orient=HORIZONTAL)
        
        self.initButton.pack(side=LEFT, fill=BOTH, expand=YES)
        self.transparencySlider.pack(side=LEFT, fill=BOTH, expand=YES)

        
        
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
        cv.addWeighted(self.background, (transparency/100.0), frame, (100-transparency)/100.0, 0.0, frame)

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
    root.title("Vampire Webcam")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()


if __name__ == "__main__":
    main()
