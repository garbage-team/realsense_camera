import math
import cv2
import pyrealsense2 as rs
from scipy.spatial import Delaunay
from math import pi
import numpy as np
from config import cfg

def main():
    # TODO Add a load from config function that sets parameters according to case
    calibrate = True
    pipe, align, d_scale = setup_camera_feeds()
    articles = 7

    if calibrate:
        print('Starting calibration, make sure the pallet is full with articles.')
        volume_empty = cfg['pallet_empty']
        volume_full = []
        # Get avg of 5 measurements
        for i in range(5):
            rgb, depth = capture_images(pipe, align, d_scale)
            volume = volume_from_depth(depth)
            volume_full.append(volume)
        volume_full_var = np.var(volume_full)
        error = np.mean(volume_full - np.mean(volume_full))
        volume_full = np.mean(volume_full)
        print('Calibration complete!')
        print("Full volume: ", volume_full)
        print('Variance: ', volume_full_var)
        print('error: ', error)
    else:
        print('Running default values.')
        volume_empty = cfg['pallet_empty']
        volume_full = cfg['pallet_full']
    volumes = [volume_empty, volume_full]

    while True:

        rgb, depth = capture_images(pipe, align, d_scale)
        volume = volume_from_depth(depth)
        show_result(rgb, volume, volumes, articles)


def setup_camera_feeds():
    """
    Starts the RealSense camera streams and aligns the rgb and depth image
    :return: the camera pipeline, aligned frames, and the scale of the depth image
    """
    print("Setting up camera pipeline..")
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

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)
    print("Camera setup complete.")
    return pipe, align, depth_scale


def capture_images(pipe, align, depth_scale):
    """
    Captures a RGB image and a depth map from the camera
    :param pipe: Camera pipeline
    :param align: Aligned frames
    :param depth_scale: Scale of the depth map
    :return: rgb image, depth map image
    """
    # Get coherent set of frames [depth and color]
    frames = pipe.wait_for_frames()
    aligned_frames = align.process(frames)
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not color_frame or not depth_frame:
        print("Could not capture frame(s). Retrying..")
        #capture_images(pipe, align)
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    print("Captured images.")
    return color_image, depth_image * depth_scale


def depth_to_xyz(depth, fov=(69.4, 42.5)):
    """
    Takes a depth image array and calculates the points in xyz-space for all pixels

    :param depth: a depth image array (float [h, w])
    :param fov: the field of view angles in horizontal and vertical respectively (float, float)
    :return: an array of points in xyz-space (float [p, 3])
    """
    x_size = depth.shape[1]
    y_size = depth.shape[0]

    x = np.asarray([i - (x_size // 2) for i in range(x_size)])  # [w,]
    x = np.tile(np.expand_dims(x, axis=0), (y_size, 1))         # [h, w]
    x = np.tan(fov[0] * pi / 360) / (x_size / 2) * np.multiply(x, depth)

    y = np.asarray([i - (y_size // 2) for i in range(y_size)])  # [h,]
    y = np.tile(np.expand_dims(y, axis=-1), (1, x_size))        # [h, w]
    y = np.tan(fov[1] * pi / 360) / (y_size / 2) * np.multiply(y, depth)

    z = depth

    x = np.expand_dims(x, -1)  # [h, w, 1]
    y = np.expand_dims(y, -1)  # [h, w, 1]
    z = np.expand_dims(z, -1)  # [h, w, 1]
    p = np.concatenate((x, y, z), axis=-1)   # [h, w, 3]
    p = np.reshape(p, (x_size * y_size, 3))  # [p, 3]

    return p


def shift_xyz_to_pallet(xyz, angle, z0=0.75):
    """

    :param xyz: xyz point cloud
    :param angle: angle to tilt the coordinate system with
    :param z0: distance to average top level of the pallet from depth map
    :return: shifted and tilted xyz point cloud
    """
    # TODO Add detection of the angle automatically using the height from two coordinates on the rim
    xyz[:, 2] = z0 - xyz[:, 2]
    t_x = np.asarray([[1., 0., 0.],
                      [0, math.cos(angle), math.sin(angle)],
                   [0, -math.sin(angle), math.cos(angle)]])
    xyz_shifted = np.dot(xyz, t_x)

    return xyz_shifted


def xyz_to_volume(xyz):
    """
    Calculates the volume of the points in xyz over the xy-plane.

    Negative z-coordinates result in negative volumes
    :param xyz: a list of coordinates in xyz-space that represent the point cloud (float [p, 3])
    :return: The total volume of the point cloud in xyz-space (float)
    """
    # Extract the triangles in the xy-plane
    triangles = Delaunay(xyz[:, 0:2])

    # Find all vertices of the constructed surface in xyz-space
    vertices = xyz[triangles.simplices]  # [e, points, xyz]
    x, y, z = vertices[:, :, 0], vertices[:, :, 1], vertices[:, :, 2]

    # Extract the mean height of all the triangular pillars
    heights = np.sum(z, axis=-1) / 3.  # [e,]
    # Extract the areas of all the triangles
    areas = np.abs(0.5 * (((x[:, 1] - x[:, 0]) * (y[:, 2] - y[:, 0])) -
                          ((x[:, 2] - x[:, 0]) * (y[:, 1] - y[:, 0]))))  # [e,]
    # Finding all volumes
    volumes = heights * areas  # [e,] = [e,] * [e,]
    volume = np.sum(volumes)   # [e,] -> [,]
    return volume


def volume_from_depth(depth, z_max=1.1, z_min=0.6, z0=0.75):
    xyz = depth_to_xyz(depth)
    # Remove points outside region of interest and shift coordinate system
    xyz = xyz[np.where(xyz[:, 2] < z_max)]
    xyz = xyz[np.where(xyz[:, 2] > z_min)]
    xyz = shift_xyz_to_pallet(xyz, angle=0.23554, z0=z0)
    volume = xyz_to_volume(xyz)
    return round(volume, 4)


def show_result(rgb, volume, volumes, articles):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fill_rate = 1 - (volume - volumes[1]) / (volumes[0] - volumes[1])
    fill_rate_prc = 100 * fill_rate
    fill_articles = round(fill_rate * articles)
    print("Fill rate percentage: ", str(round(fill_rate_prc, 2)), "%")
    text = str(fill_articles) + "/" + str(articles)

    if fill_rate < 0.3:
        # Red text if nearly empty
        text_color = (0, 0, 255)
    elif fill_rate < 0.6:
        # Yellow text if medium full
        text_color = (0, 255, 255)
    else:
        # Green text if mostly full
        text_color = (0, 255, 0)
    rgb = cv2.putText(rgb, text, (75, 75), font, 3, text_color, 2, cv2.LINE_AA)
    cv2.imshow('Pallet', rgb)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
