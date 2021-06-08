"""
For reading config files within the repository

Read the config file with read_config() and save it using
save_config()

In the config dictionary, the ["config_file_path"] value
needs to exist when saving, specifying where to save the
config file.
"""


def read_config(path="config.csv"):
    cfg = dict()
    with open(path, "r") as file:
        for line in file.readlines():
            line = line.strip()
            line = line.split(",")
            key = line[0]
            if key.startswith("var_"):  # float variables
                data = float(line[1])
            elif key.startswith("volume_"):
                data = float(line[1])
            elif key == "update_period":
                data = float(line[1])
            elif key.startswith("max_num_"):
                data = int(line[1])
            else:
                data = line[1]
            cfg[key] = data
    return cfg


def save_config(cfg_dict):
    with open(cfg_dict["config_file_path"], "w") as file:
        for key in cfg_dict.keys():
            line = str(key) + "," + str(cfg_dict[key]) + "\n"
            file.write(line)
