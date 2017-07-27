import cv2 as cv

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

if __name__ == "__main__":
    print("This is a library, not a runnable program.")
