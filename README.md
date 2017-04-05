# Python Webcam


### greenscreen.py
The greenscreen program is pretty intuitive. Run it, and install any libraries it tells you to. 

Click a color on the webcam stream to select it for screening.

Use the buttons to remove masks.



### webcam.py

The webcam program provides multiple motion detection features on a webcam.

The modes are as follows:
- Basic Webcam
- Basic Motion Detection
- Webcam with Motion Detection Overlay

These can be chosen with 1, 2, and 3.

The Motion detection has multiple options as follows:
- Motion Outline: this shows an outline of the areas of motion.
- Motion Ghost: this shows motion like a ghost.

also,
- Standard View: white output on a black background
- Inverse View: black output on a white background

These can be chosen with 4-7.

Note that you can't have an Inverse View in Overlay mode.

To run this program, you're going to need cv2 and Tkinter. If you don't have them, this program won't run. For cv2, on ubuntu, look for the opencv package

To close this program, hit escape.


