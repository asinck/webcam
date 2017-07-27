#!/usr/bin/env python
#Adam Sinck

#This program should use the webcam to draw on the screen

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



from motioncam import webcam
            
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
        |[no mask][remove last]|
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
        self.display.bind('<Button-1>', self.getColor)
        self.display.bind('<Button-3>', self.picture)

        self.imageNumber = 0;

        self.noMaskButton = Button(self.controlFrame, text="No mask", command = lambda : self.setScreen(False, None))
        
        self.noMaskButton.pack(side=LEFT, fill=BOTH, expand=YES)

        # self.background = cv.imread("forest.jpg")
        self.pictureframe = None


    def stream(self):
        #take a frame
        self.webcam.takeFrame()
        frame = self.webcam.getFrame()


        #calculate the mask
        if (len(self.mask) > 0):
            #    The current status of the project: This allows the
            #user to click on a color in the stream and filter
            #everything out except for that color. This also does
            #motion tracking, and marks the region of most motion, but
            #it doesn't filter the motion tracking based on color.
            #    The next step would either be to filter motion based
            #on color or to outline a pingpong ball with a cv circle.
            
            #make a HSV copy of the frame
            HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

            #make a mask for masking out everything that's not the chosen color
            colormask = cv.inRange(HSV, self.mask[0], self.mask[1])
            #take a motion frame, and mask out regions of that that
            #aren't the right color, using the color mask. This makes
            #the webcam only consider motion of objects that are the
            #right color.
            motionmask = self.webcam.motioncap()
            motionmask = cv.bitwise_and(motionmask, motionmask, mask=colormask)

            #mask the frame to only show the correctly colored regions
            frame = cv.bitwise_and(frame, frame, mask=colormask)
            
            #Find out if there's a notable amount of motion, then find
            #out where the most motion is and put a dot there.
            still = int(cv.mean(motionmask)[0]*100) < 50
            if (not still):
                (minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(motionmask)
                cv.circle(frame, maxLoc, 4, (0, 255, 0), 5)


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

    def getColor(self, event):
        x, y = event.x, event.y
        # print('Clicked at {}, {}'.format(x, y))
        #hsv = cv.cvtColor(np.uint8([[[0, 200, 200]]]), cv.COLOR_BGR2HSV)
        hsv = cv.cvtColor(np.uint8([[self.webcam.getFrame()[y][x]]]), cv.COLOR_BGR2HSV)
        # print "bgr:", self.webcam.frame[y][x]
        # print "hsv:", hsv
        self.setScreen(True, hsv)
        

    #This sets the mask for the webcam. If mask == False, this tells
    #it to remove the mask, even though they're terribly comfortable.
    #Otherwise, it will set the mask to the given color.
    def setScreen(self, mask, hsv):
        if (not mask):
            self.mask = []
        else:
            h, s, v = hsv[0][0]
            # print h, s, v
            color = [[h-10, max(0, s-100), max(0, v-100)],
                     [h+10, min(255, s+100), min(255, v+100)]]
            lower = np.array(color[0])
            upper = np.array(color[1])
            self.mask = [lower, upper]


    def picture(self, event):
        print "taking picture"
        cv.imwrite("%d.jpg" %self.imageNumber, self.pictureframe)
        self.imageNumber += 1
        

def main():
    root = Tk()
    root.title("Color Tracker")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()

if __name__ == "__main__":
    main()
