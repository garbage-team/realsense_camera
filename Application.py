from VolumeSensor import VolumeSensor
from PalletGUI import PalletGUI
from config import read_config, save_config
import numpy as np
from PointCloudPlotter import plot_point_cloud
from time import time


class Application:
    """
    An application for running the volume sensor together with its
    GUI, implements callback functions and calibration functions.

    Runs in one thread which means it will be unresponsive during
    a measurement, which usually takes a couple of seconds.

    To start the application with the GUI, run the following code:
        app = Application()

        app.main_loop()
    """
    def __init__(self):
        self.cfg = read_config()
        self.volume_sensor = VolumeSensor(
            np.asarray([0, 0, 0.75]),
            np.asarray([-0.16515, 0, 0]),
            np.asarray([[0.6, -0.6],
                        [0.6, -0.3],
                        [.5, -.5]]),
            self.cfg
        )
        # Callback function declaration
        self.gui = PalletGUI(self.add_btn_callback,
                             self.rem_btn_callback,
                             self.measure_btn_callback,
                             self.calibrate_btn_callback)
        self.plot_figure = None
        self.last_measurement = time()
        self.update_period = float(self.cfg["update_period"])

    def add_btn_callback(self):
        """
        Increases the number of maximum articles the volume sensor
        measures.

        :return: None
        """
        self.volume_sensor.max_articles += 1

    def rem_btn_callback(self):
        """
        Decreases the number of maximum articles the volume sensor
        measures.

        :return: None
        """
        self.volume_sensor.max_articles -= 1

    def measure_btn_callback(self):
        """
        Runs a measurements cycle and plots a 3D point cloud.

        Updates the state of the volume sensor with fill rate and
        number of articles

        :return: None
        """
        self.volume_sensor.measure_fill_rate()
        self.plot_figure = plot_point_cloud(self.volume_sensor.point_cloud,
                                            self.plot_figure)
        self.last_measurement = time()

    def calibrate_btn_callback(self):
        """
        Calibrates the sensor's full volume property through measuring
        the current volume

        :return: None
        """
        full_volume = self.volume_sensor.calibrate_full()
        self.cfg["volume_full"] = full_volume
        save_config(self.cfg)

    def update_gui(self):
        """
        Updates the GUI with the current properties of the volume sensor

        :return: None
        """
        self.gui.update_image(self.volume_sensor.rgb)
        fill_rate = self.volume_sensor.fill_rate * self.volume_sensor.max_articles
        self.gui.update_fill_rate(self.volume_sensor.fill_rate,
                                  round(fill_rate),
                                  self.volume_sensor.max_articles)
        self.gui.root.update()

    def main_loop(self):
        """
        Main loop of the application, runs updating functions and
        takes measurements periodically. The period is set in config
        file.

        Start the application through Application().main_loop()

        :return: Does not return
        """
        self.volume_sensor.measure_fill_rate()
        while True:
            self.update_gui()
            if time() - self.last_measurement > self.update_period:
                self.measure_btn_callback()


if __name__ == "__main__":
    app = Application()
    app.main_loop()
