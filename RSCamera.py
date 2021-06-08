import pyrealsense2 as rs
import numpy as np
import cv2
import struct


class RSCamera:
    # Static property
    maximum_depth = 4.

    def __init__(self):
        """
        An intel realsense camera object for creating aligned depth and rgb images
        """
        self.pipe = rs.pipeline()
        self.config = rs.config()

        # Finding config data and creating the output streams for the camera
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start the pipeline to start streaming data
        self.profile = self.pipe.start(self.config)

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = self.profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        # Create an align object
        # rs.align allows us to perform alignment of depth frames to others frames
        # The "align_to" is the stream type to which we plan to align depth frames.
        align_to = rs.stream.color
        self.align = rs.align(align_to)

    def capture_images(self):
        """
        Captures a RGB image and a depth map from the camera

        :return: rgb image, depth map image
        """
        # Get coherent set of frames [depth and color]
        frames = self.pipe.wait_for_frames()
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not color_frame or not depth_frame:
            print("Could not capture frame(s)...")
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        return color_image, depth_image * self.depth_scale

    def close(self):
        self.pipe.stop()


def display_images(color_image, depth_image):
    """
    Displays a depth image and a RGB image beside each other
    in a window. The depth image is displayed through applying
    a color map to the depths.

    :param color_image: a RGB image in the cv2 standard
    (height, width, channels) where the channels are ordered RGB
    :param depth_image: a depth map that is similar to the color
    image (height, width), as given by RSCamera().capture_images()
    :return: the cv2 key-code that is pressed during the time
    the window was shown
    """
    # Switch color image channels
    color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
    # rescale depth image
    depth_image = depth_image
    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,
                                                           alpha=255/RSCamera.maximum_depth),
                                       cv2.COLORMAP_INFERNO)
    depth_colormap_dim = depth_colormap.shape
    color_colormap_dim = color_image.shape
    # print(np.max(depth_image), np.min(depth_image))
    # print(np.max(depth_colormap), np.min(depth_colormap))
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
    return cv2.waitKey(5)


def save_images(depth_image, color_image, path):
    """
    Saves the depth and the color image

    :param depth_image: depth image
    :param color_image: color image
    :param path: path to saved images
    :return: True
    """
    color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
    depth_bytes = struct.pack("d" * 480 * 640, *depth_image.flatten().tolist())
    with open(path + '.raw', 'wb') as file:
        file.write(depth_bytes)
    cv2.imwrite(path + '.png', color_image)
    return True


def read_depth(path):
    depth_bytes = open(path, "rb").read()
    depth = np.asarray(struct.unpack("d" * 480 * 640, depth_bytes))
    depth = np.reshape(depth, (480, 640))
    return depth
