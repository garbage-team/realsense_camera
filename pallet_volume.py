import math
import cv2
import pyrealsense2 as rs
from scipy.spatial import Delaunay
from math import pi
import numpy as np

def main():

    pipe, align, d_scale = setup_camera_feeds()
    volume_empty = []  # -0.1067519020328733
    volume_full = 0  # -0.03130304659043235
    # Run 10 measurements on empty to calibrate
    for i in range(10):
        # TODO Place the volume extracting inside its own function
        rgb, depth, images = capture_images(pipe, align, d_scale)
        xyz = depth_to_xyz(depth)
        # Remove points outside region of interest and shift coordinate system
        xyz = xyz[np.where(xyz[:, 2] < 1.1)]
        xyz = xyz[np.where(xyz[:, 2] > 0.6)]
        xyz = shift_xyz_to_pallet(xyz, angle=0.23554, z0=0.75)

        volume = xyz_to_volume(xyz)
        volume_empty.append(volume)
    volume_empty_avg = np.mean(volume_empty)
    volume_empty_mae = np.mean(abs(volume_empty - volume_empty_avg))
    print("Avg empty volume: ", volume_empty_avg)
    print("Avg error %: ", round(-volume_empty_mae/volume_empty_avg, 2))

    while True:

        rgb, depth, images = capture_images(pipe, align, d_scale)
        xyz = depth_to_xyz(depth)
        xyz = xyz[np.where(xyz[:, 2] < 1.1)]
        xyz = xyz[np.where(xyz[:, 2] > 0.6)]
        xyz = shift_xyz_to_pallet(xyz, angle=0.23554, z0=0.75)

        volume = xyz_to_volume(xyz)
        fill_rate = 1 - (volume-volume_full)/(volume_empty_avg-volume_full)
        fill_rate_prc = 100 * fill_rate
        print("Fill rate percentage: ", str(round(fill_rate_prc, 2)), "%")

        cv2.imshow('Pallet', rgb)
        cv2.waitKey(0)


def setup_camera_feeds():
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
    print('Capturing images..')
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

    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    depth_colormap_dim = depth_colormap.shape
    color_colormap_dim = color_image.shape

    # If depth and color resolutions are different, resize color image to match depth image for display
    if depth_colormap_dim != color_colormap_dim:
        resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                                         interpolation=cv2.INTER_AREA)
        images = np.hstack((resized_color_image, depth_colormap))
    else:
        images = np.hstack((color_image, depth_colormap))

    print("Images captured.")
    return color_image, depth_image * depth_scale, images


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

    return xyz_to_volume(xyz)

if __name__ == '__main__':
    main()
