"""
Module for taking images with the realsense camera for neural network training purposes
"""

import cv2
from time import sleep
import os
from RSCamera import RSCamera, display_images, save_images


PATH_PREFIX = "data/"


def main():
    cam = RSCamera()
    i = 0
    if not os.path.exists(PATH_PREFIX):
        os.mkdir(PATH_PREFIX)
    while os.path.exists(PATH_PREFIX + str(i).zfill(6) + ".raw"):
        i += 1
    while True:
        # Get coherent set of frames [depth and color]
        color_image, depth_image = cam.capture_images()
        key = display_images(cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR), depth_image)
        if key & 0xFF == ord('s'):
            path = PATH_PREFIX + str(i).zfill(6)
            save_images(depth_image, color_image, path)
            i = i + 1
            sleep(0.1)
        if key == 27:
            cv2.destroyAllWindows()
            break
    return None


if __name__ == '__main__':
    main()
