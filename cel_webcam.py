#!/usr/bin/env python
#Adam Sinck

#This program puts Cel shading on the webcam screen

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


class webcam:
    def __init__(self):
        self.capture = cv.VideoCapture(1)
        self.frame = self.capture.read()[1]
        # self.height, self.width = self.t.shape[:2]

    def takeFrame(self):
        self.frame = self.capture.read()[1]
        

class GUI:
    def __init__(self, frame):
        """
        +----------------------+
        |                      |
        |                      |
        |       display        |
        |                      |
        |                      |
        +----------------------+
        |[ Toggle Cel Shading ]|
        +----------------------+
        """

        self.displayFrame = Frame(frame)
        self.controlFrame = Frame(frame)

        self.displayFrame.pack(side=TOP)
        self.controlFrame.pack(side=BOTTOM, fill=X, expand=YES)

        self.display = Label(self.displayFrame)
        self.display.after(10, self.stream)
        self.webcam = webcam()
        self.mask = []
        self.display.pack()

        self.normal = True

        self.celButton = Button(self.controlFrame, text="Toggle Cel Shading", command = lambda : self.toggleNormality(None))
        
        self.celButton.pack(side=LEFT, fill=BOTH, expand=YES)

        self.background = cv.imread("forest.jpg")
        self.pictureframe = None

    def toggleNormality(self, event):
        self.normal = not self.normal

    def stream(self):
        #take a frame
        self.webcam.takeFrame()
        frame = self.webcam.frame
        if (not self.normal):
            edges = cv.Canny(frame, 50, 200)
            
            cel = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            # frame = cv.bitwise_or(cel, np.array([[[31, 0, 0]]*640]*480))
            frame = cv.bitwise_or(cel, np.array([7, 31, 31]))
            # edges = cv.GaussianBlur(cv.bitwise_not(edges), (3, 3), 0)
            edges = cv.bitwise_not(edges)
            frame = cv.cvtColor(frame, cv.COLOR_HSV2BGR)
            frame = cv.bitwise_and(frame, frame, mask=edges)

            # frame = cv.bitwise_and(frame, np.array(edges))
            
        
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


def main():
    root = Tk()
    root.title("Cel Shading Webcam")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()

if __name__ == "__main__":
    main()
