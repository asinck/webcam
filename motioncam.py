import cv2 as cv

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

if __name__ == "__main__":
    print("This is a library, not a runnable program.")
