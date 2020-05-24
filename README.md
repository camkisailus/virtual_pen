This is an OpenCV project that tracks a pen around the screen and draws lines. It reminds me of a smart board.

Run by `python3 virutal_pen.py` or `python3 virtual_pen.py -t [--tracker]` if you want to use CSRT tracker instead of HSV thresholding

**For HSV: Thresholding:**

Adjust the HSV sliders so that only your drawing device (pen) is seen in the mask

Press `s` to save the values and proceed to drawing

Drawing will start immediately... cover the pen if don't want to draw anything

`e` turns the pen to an eraser and vice versa

`c` clears your drawing canvas


**For CSRT Tracking:**

Once image appears press `s` to select your region of intrest. Use your mouse to click the top left and bottom right corners of your drawing device(pen)

If you are not happy with your box, press `c` to start over.

Then press space or enter and tracking begins immediately.

Press esc or `q` to close the program
