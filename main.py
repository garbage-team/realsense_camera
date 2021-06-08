"""
Module for taking images with the realsense camera for
neural network training purposes
"""

import cv2
from time import sleep
import os
from RSCamera import RSCamera, display_images, save_images


PATH_DIR = "data/"


def main():
    cam = RSCamera()
    image_id = 0
    # create the data folder for saving images
    if not os.path.exists(PATH_DIR):
        print("Creating data directory...")
        os.mkdir(PATH_DIR)
    else:
        print("Data directory folder already exists. ")
        print("Searching for old files within the directory...")

        # Increment the path counter if old files exist
        while os.path.exists(PATH_DIR + str(image_id).zfill(6) + ".raw"):
            image_id += 1
        print("Files found: ", str(image_id))
        print("Next image ID in sequence: ", str(image_id).zfill(6))

    while image_id < 1000000:  # paths should not exceed this
        # Get coherent set of frames [depth and color]
        color_image, depth_image = cam.capture_images()
        key = display_images(color_image, depth_image)
        if key & 0xFF == ord('s'):  # save image
            print("Saving image...")
            image_path = PATH_DIR + str(image_id).zfill(6)
            print("path to image: ", image_path)
            save_images(depth_image, color_image, image_path)
            image_id += 1
            # sleep(seconds) for creating a nice feedback when taking an image
            # the image will freeze for a fraction of a second
            sleep(0.1)
            print("Done.")
        if key == 27:               # [esc] character (quit)
            print("Destroying windows, exiting application... ")
            cv2.destroyAllWindows()
            cam.close()
            break

    return None


if __name__ == '__main__':
    main()
