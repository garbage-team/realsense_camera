import pyrealsense2 as rs
import numpy as np
import cv2


class RSCamera:
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

    def __del__(self):
        self.close()
