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
        self.pictureframe = None


        #init the webcam in its class
        self.webcam = webcam()

        #This is what does the Cel masking. The numbers are powers of
        #two minus 1, so that when the mask is bitwise or'd with a
        #frame, it will convert the last bits of the H, S, and V to 1's.
        self.mask = np.array([7, 31, 31])

        #some conditions and variables.
        #if we're doing cel shading right now
        self.cel = False
        #if we put edges on stuff
        self.edges = False
        #how much to smooth stuff
        self.blurLevel = 5

        #add a couple buttons to toggle these
        self.celButton = Button(self.controlFrame, text="Toggle Cel Shading",
                                command = lambda : self.toggleCel(None))

        self.edgesButton = Button(self.controlFrame, text="Toggle Edges",
                                  command = lambda :self.toggleEdges(None),
                                  state="disabled")
        
        self.celButton.pack(side=LEFT, fill=BOTH, expand=YES)
        self.edgesButton.pack(side=LEFT, fill=BOTH, expand=YES)

        
        
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
    root.title("Cel Shading Webcam")
    mainFrame = Frame(root)
    mainFrame.pack()
    window = GUI(mainFrame)
    root.mainloop()


if __name__ == "__main__":
    main()
