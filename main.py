import pyrealsense2 as rs
import numpy as np
import cv2
import struct
from time import sleep
import os


PATH_PREFIX = "data_1/"


def main():
    # creating a context for the camera
    pipe = rs.pipeline()
    config = rs.config()

    # Finding config data and creating the output streams for the camera
    pipeline_wrapper = rs.pipeline_wrapper(pipe)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start the pipeline to start streaming data
    profile = pipe.start(config)

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    print("Depth Scale is: ", depth_scale)

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)
    i = 0
    k = 0
    while os.path.exists(PATH_PREFIX + str(i).zfill(6) + ".raw"):
        i += 1
    try:
        while True:
            # Get coherent set of frames [depth and color]
            frames = pipe.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not color_frame or not depth_frame:
                continue
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_INFERNO)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                                                 interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            # Show images
            cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', images)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('s'):
                save_pair(depth_image, color_image, i)
                i = i + 1
                sleep(1)
            if key & 0xFF == ord('k'):
                k = 25
            if key == 27:
                cv2.destroyAllWindows()
                break
            if k > 0:
                save_pair(depth_image, color_image, i)
                i = i + 1
                k = k - 1
                sleep(0.5)

    finally:
        pipe.stop()
    return None


def show_depth():
    with open('hey.raw', 'rb') as file:
        depth_image = np.asarray(struct.unpack('H' * 640*480, file.read())).reshape((480, 640))
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', depth_colormap)
    cv2.waitKey(0)
    return None


def save_pair(depth_image, color_image, i):
    """
    Saves the depth and the color image

    :param depth_image: depth image
    :param color_image: color image
    :param i: ID of image
    :return: True
    """
    depth_bytes = struct.pack("H" * 480 * 640, *depth_image.flatten().tolist())
    path = PATH_PREFIX + str(i).zfill(6)
    with open(path + '.raw', 'wb') as file:
        file.write(depth_bytes)
    cv2.imwrite(path + '.png', color_image)
    print(path)
    return True


if __name__ == '__main__':
    main()
