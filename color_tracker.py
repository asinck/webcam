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
    def motioncap(self):
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
        return frame
            
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
