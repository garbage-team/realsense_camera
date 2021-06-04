import numpy as np
from math import pi
from scipy.spatial import Delaunay


class PointCloud:
    def __init__(self, depth, fov=(69.4, 42.5)):
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
        self.xyz = p

    def transform(self, rotation_matrix=np.eye(3), shift_matrix=np.asarray([0, 0, 0])):
        """
        Shift and transform point cloud according to equation:
        points = xyz @ rotation_matrix + shift_matrix

        :param rotation_matrix:
        :param shift_matrix:
        :return: shifted and tilted xyz point cloud
        """
        self.xyz = (self.xyz @ rotation_matrix) + shift_matrix
        return self

    def rotate(self, angles=np.asarray([0, 0, 0])):
        """
        Rotates all points in xyz around each axis in order according to angles

        :param angles: angles in radians of each axis' rotation
        :return: rotated xyz points
        """
        x_rotation = np.asarray([[1, 0, 0],
                                 [0, np.cos(angles[0]), -np.sin(angles[0])],
                                 [0, np.sin(angles[0]),  np.cos(angles[0])]])
        y_rotation = np.asarray([[np.cos(angles[1]), 0, -np.sin(angles[1])],
                                 [0, 1, 0],
                                 [np.sin(angles[1]), 0,  np.cos(angles[1])]])
        z_rotation = np.asarray([[np.cos(angles[2]), -np.sin(angles[2]), 0],
                                 [np.sin(angles[2]),  np.cos(angles[2]), 0],
                                 [0, 0, 1]])
        rotation = x_rotation @ y_rotation @ z_rotation
        self.transform(rotation_matrix=rotation)
        return self

    def crop(self, borders=np.asarray([1, -1]), axis=0):
        """
        Returns points in xyz where the values along the axis is within the values given
        in borders

        :param borders: two values within which all values should lie
        :param axis: which axis of points to be considered
        :return: a subset of points in xyz that fulfills the condition
        """
        self.xyz = self.xyz[np.where(self.xyz[:, axis] < np.max(borders))]
        self.xyz = self.xyz[np.where(self.xyz[:, axis] > np.min(borders))]
        return self

    def to_volume(self):
        """
        Calculates the volume of the points in xyz over the xy-plane.

        Negative z-coordinates result in negative volumes
        :return: The total volume of the point cloud in xyz-space (float)
        """
        # Extract the triangles in the xy-plane
        triangles = Delaunay(self.xyz[:, 0:2])

        # Find all vertices of the constructed surface in xyz-space
        vertices = self.xyz[triangles.simplices]  # [e, points, xyz]
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

    def select_roi(self,
                   shift=np.asarray([0, 0, -0.75]),
                   rotation=np.asarray([0.23554, 0, 0]),
                   borders=np.asarray([[np.inf, -np.inf], [np.inf, -np.inf], [1.1, 0.6]])):
        """
        Transforms and crops point cloud according to
        region of interest set

        :param shift: the linear movement after rotation
        :param rotation: the rotation in each axis in radians
        :param borders: the borders for each axis after shift and rotation
        :return: points within region of interest
        """
        self.rotate(angles=np.asarray(rotation))
        self.transform(shift_matrix=np.asarray(shift))
        for i in range(len(borders)):
            self.crop(borders[i], axis=i)
        return self
