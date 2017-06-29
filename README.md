# Python Webcam

### What's this?

This is a small set of webcam stream processing programs I've written for fun and because they're cool. They primarily do motion and color processing effects. 

When you run a program, it will do a check for necessary libraries, and notify you if it needs any. Install those, and you should be good to go.



### greenscreen.py

This program filters out a chosen color from the webcam stream, filling all regions of that color with a background image (provided as `forest.jpg`, which I shamelessly stole from the internet). 

To select a color for filtering, click on it from the stream. If you click on a region that has been greenscreened out, it will choose the color behind the screen, on the actual stream. You can choose as many colors as you want.

To remove filters (in most recent order), click "Remove last mask". To remove all filters, click "No mask".

This is a frame I took from the program. On the left, you see the inside of a building. On the right, the wall of a stairwell was masked out. The door was masked a little bit because the color was too close to that of the wall.

![0](0.jpg)


##### TODO:

-   Allow a user to choose their own background image, and provide a warning if the dimensions are incorrect.



### cel_webcam.py

In short, this is a program that does Cel shading on the webcam. It can also do Canny edge detection on the stream, to provide outlines on everything. 

Cel shading is a graphics technique that makes everything look cartoony. Instead of having realistic lighting, shadows, textures, and so on, it uses a very limited set of colors. These colors come in pairs - a light "normal" version and a dark "shadowed" version. 

##### TODO:

-   Add ability to read from a config file. This will be useful for setting how much blur to put on the stream, among other things. 



### webcam.py

This is a program that I'm cleaning up that I wrote a long time ago. It's messy. Don't judge :)

This provides multiple motion detection features on a webcam.

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


