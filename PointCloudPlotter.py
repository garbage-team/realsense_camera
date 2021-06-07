from PointCloud import PointCloud
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import cv2


def plot_point_cloud(point_cloud: PointCloud, figure=None):
    if not figure:
        figure = plt.figure()
        plt.ion()
    ax = plt.axes(projection="3d")
    pc = point_cloud.filter()
    ax.scatter3D(pc[:, 0],
                 pc[:, 1],
                 pc[:, 2],
                 c=pc[:, 2], cmap='hsv')
    ax.set_title("3D plot")
    plt.show()
    plt.draw()
    plt.pause(0.001)
    return figure


def get_pc_image(pc: PointCloud):
    ax = plt.axes(projection="3d")
    pc = pc.filter()
    ax.scatter3D(pc[:, 0],
                 pc[:, 1],
                 pc[:, 2],
                 c=pc[:, 2], cmap='hsv')
    ax.set_title("3D plot")
    plt.savefig("plot.png")
    rgb = cv2.cvtColor(cv2.imread("plot.png"), cv2.COLOR_BGR2RGB)
    return rgb
