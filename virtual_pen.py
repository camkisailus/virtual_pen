import cv2
import numpy as np
import time
import imutils
import argparse


def masking():
    # Required for trackbars
    def nothing(x):
        pass
    # Init webcam feed
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    cv2.namedWindow("Trackbars")

    cv2.createTrackbar("L-H", "Trackbars", 0, 179, nothing)
    cv2.createTrackbar("L-S", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("L-V", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("U-H", "Trackbars", 179, 179, nothing)
    cv2.createTrackbar("U-S", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("U-V", "Trackbars", 255, 255, nothing)

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        l_h = cv2.getTrackbarPos("L-H", "Trackbars")
        l_s = cv2.getTrackbarPos("L-S", "Trackbars")
        l_v = cv2.getTrackbarPos("L-V", "Trackbars")
        u_h = cv2.getTrackbarPos("U-H", "Trackbars")
        u_s = cv2.getTrackbarPos("U-S", "Trackbars")
        u_v = cv2.getTrackbarPos("U-V", "Trackbars")

        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, lower_range, upper_range)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        stacked = np.hstack((mask_3, frame, res))

        cv2.imshow('Trackbars', cv2.resize(stacked, None, fx=0.4, fy=0.4))

        key = cv2.waitKey(1)
        if key == 27:
            break

        if key == ord('s'):
            arr = [[l_h, l_s, l_v], [u_h, u_s, u_v]]

            print(arr)
            np.save('penval', arr)
            break
    cap.release()
    cv2.destroyAllWindows()

    load_from_disk = True
    if load_from_disk:
        penval = np.load('penval.npy')

    # Init webcam feed
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    kernel = np.ones((5, 5), np.uint8)

    noise_threshhold = 1000
    x1 = y1 = 0
    canvas = None
    eraser = False
    cv2.namedWindow("DrawingBoard", cv2.WINDOW_NORMAL)

    while(1):
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if canvas is None:
            canvas = np.zeros_like(frame)

        if penval is not None:
            lower_range = penval[0]
            upper_range = penval[1]

        else:
            lower_range = [100, 100, 100]
            upper_range = [150, 150, 150]

        mask = cv2.inRange(hsv, lower_range, upper_range)

        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        contours, heirarchy = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours and cv2.contourArea(
                max(contours, key=cv2.contourArea)) > noise_threshhold:
            c = max(contours, key=cv2.contourArea)

            x2, y2, w, h = cv2.boundingRect(c)

            if x1 != 0 and y1 != 0:
                if eraser:
                    canvas = cv2.circle(canvas, (x2, y2), 20, (0, 0, 0), -1)
                else:
                    canvas = cv2.line(
                        canvas, (x1, y1), (x2, y2), [
                            255, 0, 0], 5)
            x1, y1 = x2, y2

        else:
            x1, y1 = 0, 0

        frame = cv2.add(frame, canvas)

        cv2.imshow('DrawingBoard', frame)
        k = cv2.waitKey(1)

        if k == 27:
            break
        if k == ord('c'):
            canvas = None
        if k == ord('e'):
            eraser = not eraser

    cap.release()
    cv2.destroyAllWindows()


def tracking():
    # Init webcam feed
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    tracker = cv2.TrackerCSRT_create()
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    init_bb = None
    canvas = None
    eraser = False
    x1 = y1 = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if canvas is None:
            canvas = np.zeros_like(frame)

        if init_bb is not None:
            (ret, bbox) = tracker.update(frame)
            if ret:
                (x2, y2, _, _) = [int(val) for val in bbox]
                if x1 != 0 and y1 != 0:
                    if eraser:
                        canvas = cv2.circle(
                            canvas, (x2, y2), 20, (0, 0, 0), -1)
                    else:
                        canvas = cv2.line(
                            canvas, (x1, y1), (x2, y2), [
                                0, 255, 0], 5)
                x1, y1 = x2, y2
            else:
                x1, y1 = 0, 0

        frame = cv2.add(frame, canvas)
        cv2.imshow('Image', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            init_bb = cv2.selectROI(
                "Image", frame, fromCenter=False, showCrosshair=True)
            tracker.init(frame, init_bb)
        if key == ord('q') or key == 27:
            break
        if key == ord('e'):
            eraser = not eraser
        if key == ord('c'):
            canvas = None

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--tracker", action="store_true",
                    help="If you want to use tracking instead of masking")
    args = ap.parse_args()

    if args.tracker:
        tracking()
    else:
        masking()
