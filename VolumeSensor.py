import numpy as np
from RSCamera import RSCamera
from PointCloud import PointCloud


class VolumeSensor:
    def __init__(self, shift, rotation, borders, cfg: dict):
        self.volume_empty = float(cfg["volume_empty"])
        self.volume_full = float(cfg["volume_full"])
        self.depth_camera = RSCamera()
        self.rgb = None
        self.depth = None
        self.point_cloud = None
        self.fill_rate = None
        self.max_articles = int(cfg["max_num_articles"])
        self.shift = shift
        self.rotation = rotation
        self.borders = borders
        # self.measure_fill_rate()

    def measure_depth(self):
        self.rgb, self.depth = self.depth_camera.capture_images()
        self.point_cloud = PointCloud(self.depth).select_roi(self.shift,
                                                             self.rotation,
                                                             self.borders)
        return self.point_cloud

    def measure_fill_rate(self):
        self.measure_depth()
        volume = self.point_cloud.to_volume()
        self.fill_rate = 1 - (volume - self.volume_full) / (self.volume_empty - self.volume_full)
        return self.fill_rate

    def calibrate_full(self, num=5):
        volume_full = []
        for i in range(num):
            self.measure_depth()
            volume_full.append(self.point_cloud.to_volume())
        self.volume_full = np.mean(volume_full)
        return self.volume_full

    def calibrate_empty(self, num=5):
        volume_empty = []
        for i in range(num):
            self.measure_depth()
            volume_empty.append(self.point_cloud.to_volume())
        self.volume_empty = np.mean(volume_empty)
        return self.volume_empty

    def get_point_cloud(self):
        return self.point_cloud

    def get_rgb(self):
        return self.rgb

    def get_depth(self):
        return self.depth

    def set_empty_volume(self, volume_empty):
        self.volume_empty = volume_empty
        return self
