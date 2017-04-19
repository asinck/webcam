# Python Webcam


### greenscreen.py
This program filters out a chosen color from the webcam stream, filling all regions of that color with a background image (provided as `forest.jpg`, which I shamelessly stole from the internet). 

When you run this program, it will do a check for necessary libraries, and notify you if it needs any. Install those, and you should be good to go.

To select a color for filtering, click on it from the stream. If you click on a region that has been greenscreened out, it will choose the color behind the screen, on the actual stream. You can choose as many colors as you want.

To remove filters (in most recent order), click "Remove last mask". To remove all filters, click "No mask".

This is a frame I took from the program. On the left, you see the inside of a building. On the right, the wall of a stairwell was masked out. The door was masked a little bit because the color was too close to that of the wall.

![0](0.jpg)

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


