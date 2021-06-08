from VolumeSensor import VolumeSensor
from config import read_config, save_config


def calibrate_sensor_empty():
    cfg = read_config()
    sensor = VolumeSensor(cfg)
    print("Measuring empty volume...", end=" ")
    empty_volume = sensor.calibrate_empty()
    print("Done.")
    print("Calibrating...")
    cfg["volume_empty"] = empty_volume
    sensor.set_empty_volume(empty_volume)

    print("Testing calibration:")
    pc = sensor.measure_depth()
    current_volume = pc.to_volume()
    print("Error in m^3: ", str(abs(empty_volume - current_volume)))
    print("Saving calibration to config...")
    save_config(cfg)
    print("Done.")
    print("Exiting")
    return True


if __name__ == "__main__":
    calibrate_sensor_empty()
