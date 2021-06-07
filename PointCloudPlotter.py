from PointCloud import PointCloud
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d


def plot_point_cloud(point_cloud: PointCloud, figure=None):
    if not figure:
        figure = plt.figure()
    ax = plt.axes(projection="3d")
    pc = point_cloud.filter()
    ax.scatter3D(pc[:, 0],
                 pc[:, 1],
                 pc[:, 2],
                 c=pc[:, 2], cmap='hsv')
    ax.set_title("3D plot")
    plt.show(block=False)
    return figure
