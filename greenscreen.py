#!/usr/bin/env python
#Adam Sinck

#This program provides greenscreen functionality to the user for any
#color.

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
        self.popMaskButton = Button(self.controlFrame, text="Remove last mask", command = lambda : self.popMask())
        
        self.noMaskButton.pack(side=LEFT, fill=BOTH, expand=YES)
        self.popMaskButton.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.background = cv.imread("forest.jpg")
        self.pictureframe = None


    def stream(self):
        #take a frame
        self.webcam.takeFrame()
        frame = self.webcam.frame

        #apply mask for each chosen color
        for color in self.mask:
            #make a HSV copy of the frame
            HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            
            #calculate the mask
            mask = cv.inRange(HSV, color[0], color[1])
            
            #mask the background
            background = cv.bitwise_and(self.background, self.background, mask=mask)
            #for a more blocky mask
            # mask = cv.GaussianBlur(mask, (3, 3), 0)

            #mask the frame
            mask = cv.bitwise_not(mask)
            frame = cv.bitwise_and(frame, frame, mask=mask)

            #combine the background and the frame
            frame = cv.bitwise_or(frame, background)

            #this is for edges. Possibly useful for forcing background
            #or foreground on the masking
            # edges = cv.Canny(frame, 100, 200)
            # frame = cv.bitwise_and(frame, frame, mask=edges)

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
        print('Clicked at {}, {}'.format(x, y))
        #hsv = cv.cvtColor(np.uint8([[[0, 200, 200]]]), cv.COLOR_BGR2HSV)
        hsv = cv.cvtColor(np.uint8([[self.webcam.frame[y][x]]]), cv.COLOR_BGR2HSV)
        print "bgr:", self.webcam.frame[y][x]
        print "hsv:", hsv
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
            self.mask.append([lower, upper])
            # print "Filtering colors in range", self.mask

    def popMask(self):
        if (len(self.mask) > 0):
            self.mask.pop()

    def picture(self, event):
        print "taking picture"
        cv.imwrite("%d.jpg" %self.imageNumber, self.pictureframe)
        self.imageNumber += 1
        

def main():
    root = Tk()
    root.title("Greenscreened Webcam")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()

if __name__ == "__main__":
    main()
