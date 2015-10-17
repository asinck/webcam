#!/usr/bin/python

#this will overlay the motion detector onto a color webcam

#this is a list of import commands. If the user doesn't have Tkinter
#or other libraries installed, it will fail gracefully instead of
#crashing.
imports = [
    "import cv2 as cv",
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


#this will look at the difference between frames
def diffImg(t0, t1, t2):
    global inverseMotion, ghost
    d1 = cv.absdiff(t2, t1)
    d2 = cv.absdiff(t1, t0)
    #"and" for an outline of movement, "or" for a ghost look
    frame = None
    if ghost:
        frame = cv.bitwise_or(d1, d2)
    else:
        frame = cv.bitwise_and(d1, d2)
    #inverseMotion is whether or not the frame is black on white or
    #white on black
    if inverseMotion:
        return cv.bitwise_not(frame)
    return frame


#connect to the webcam
webcam = cv.VideoCapture(0)

# Read three images first:
t_minus = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
t = cv.cvtColor(webcam.read()[1], cv.COLOR_RGB2GRAY)
colorFrame = webcam.read()[1]
t_plus = cv.cvtColor(colorFrame, cv.COLOR_RGB2GRAY)

#window reference and title
window = "Webcam"
#make a window
cv.namedWindow(window, cv.CV_WINDOW_AUTOSIZE)


#some display settings
colorImage = True
motionImage = False
inverseMotion = False
ghost = True
displayFrame = None

#keep taking frames
while True:
    if motionImage:
        #take a frame and its inverse
        frame = diffImg(t_minus, t, t_plus)
        #convert frame to something I can use for masks
        mask = cv.cvtColor(cv.cvtColor(frame, cv.COLOR_GRAY2RGB), cv.COLOR_BGR2GRAY)
        ret, mask = cv.threshold(mask, 10, 255, cv.THRESH_BINARY)
        mask_inv = cv.bitwise_not(mask)
        
        maskedColorFrame = cv.bitwise_and(colorFrame, colorFrame, mask = mask_inv)
        maskedFrame = cv.bitwise_and(frame, frame, mask = mask)
        maskedFrame = cv.cvtColor(maskedFrame, cv.COLOR_GRAY2RGB)
        mixedFrame = cv.add(maskedColorFrame, maskedFrame)
    
    #show the relevant frame: color with motion overlay, color only, or motion only
    if colorImage and motionImage:
        displayFrame = mixedFrame
    elif colorImage:
        displayFrame = colorFrame
    else:
        displayFrame = frame
    cv.imshow(window, displayFrame)

    # Read next image
    t_minus = t
    t = t_plus
    colorFrame = webcam.read()[1]
    t_plus = cv.cvtColor(colorFrame, cv.COLOR_RGB2GRAY)
    
    #if the user presses a key, sometimes it means something
    key = cv.waitKey(10)
    #sometimes the key code is randomly off, possibly because of byte overflow
    if key > 1000000:
        key = key - 1048576 # 1048576 = 0b100000000000000000000
        
    if key == 32:
        #current epoch time * 1000, so that there won't be filename
        #conflicts unless the user is taking pictures REALLY fast
        currentTime = str(int(time.time()*1000)) + ".png"
        cv.imwrite(currentTime, displayFrame)
    #1-3 key codes for display modes
    elif key == 49:
        colorImage = True
        motionImage = False
    elif key == 50:
        colorImage = False
        motionImage = True
    elif key == 51:
        colorImage = True
        motionImage = True
    #4-7 key codes for motion display type
    elif key == 52:
        ghost = False
    elif key == 53:
        ghost = True
    elif key == 54:
        inverseMotion = False
    #todo: allow the user to have a white motion overlay
    elif key == 55:
        inverseMotion = True
        colorImage = False
        motionImage = True
    elif key == 27: #this is the code for Esc
        cv.destroyWindow(window)
        break
