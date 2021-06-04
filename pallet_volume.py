import cv2
import pyrealsense2 as rs
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from config import cfg
from PointCloud import PointCloud


def main():
    # TODO Maybe move all functions and classes to another file
    volume_empty = cfg['pallet_empty']
    volume_full = cfg['pallet_full']
    gui = PalletGUI(volume_full, volume_empty)
    gui.window.mainloop()


def run_measurement(volume_full, volume_empty):

    rgb, depth = capture_images(pipe, align, d_scale)
    xyz = depth_to_xyz(depth)
    xyz = select_roi(xyz)
    volume = xyz_to_volume(xyz)
    fill_rate = 1 - (volume - volume_full) / (volume_empty - volume_full)
    return rgb, fill_rate


def calibrate():
    print('Starting calibration, make sure the pallet is full with articles.')
    volume_full = []
    # Get avg of 5 measurements
    for i in range(5):
        rgb, depth = capture_images(pipe, align, d_scale)
        pc = PointCloud(depth)
        pc.select_roi()
        volume = pc.to_volume()
        volume_full.append(volume)
    volume_full_var = np.var(volume_full)
    error = np.mean(volume_full - np.mean(volume_full))
    volume_full = np.mean(volume_full)
    print('Calibration complete!')
    print("Full volume: ", volume_full)
    print('Variance: ', volume_full_var)
    print('error: ', error)
    return volume_full


class PalletGUI:

    def __init__(self, volume_full, volume_empty):
        # Setup variables
        self.rgb = None
        self.current_image = None
        self.volume_full = volume_full
        self.volume_empty = volume_empty
        self.articles = 0
        self.fill_rate = 0
        self.fill_articles = round(self.fill_rate * self.articles)
        self.bg_color = 'green'
        self.msg_box = None
        self.msg_box_text = "This will set the current volume as the maximum level.\nContinue?"

        # Setup GUI window, buttons, and labels
        self.window = tk.Tk()
        self.window.wm_title("Pallet measuring")
        self.img_frame = tk.Frame(master=self.window)
        self.btn_frame = tk.Frame(master=self.window, relief=tk.RAISED)
        self.btn_frame.rowconfigure([0, 1], minsize=50)
        self.btn_frame.columnconfigure([0, 1, 2, 3], minsize=70)

        # Image panel
        self.panel = tk.Label(master=self.img_frame)
        self.panel.pack(padx=10, pady=10)
        # Article text
        self.article_lbl = tk.Label(self.btn_frame, text="Maximum number of artricles: " + str(self.articles))
        self.article_lbl.grid(row=0, column=0, columnspan=2)
        # Article add/remove buttons
        self.add_btn = tk.Button(self.btn_frame, text="+", command=self.add_article)
        self.add_btn.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.rem_btn = tk.Button(self.btn_frame, text="-", command=self.remove_article)
        self.rem_btn.grid(row=0, column=3, sticky="nsew", padx=10, pady=10)
        # Article fill rate text
        self.fill_article_lbl = tk.Label(self.btn_frame, text=self.articles, relief='solid')
        self.fill_article_lbl.config(font=("Courier", 44))
        self.fill_article_lbl.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Reset volume button
        self.reset_btn = tk.Button(self.btn_frame, text="Start measuring", command=self.set_max_volume)
        self.reset_btn.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Reset volume button
        self.reset_btn = tk.Button(self.btn_frame, text="Start measuring", command=self.set_max_volume)
        self.reset_btn.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.img_frame.pack()
        self.btn_frame.pack()
        self.update_display()

    def update_display(self):
        self.rgb, self.fill_rate = run_measurement(self.volume_full, self.volume_empty)
        self.update_fill_rate()
        self.current_image = Image.fromarray(self.rgb)
        self.img_tk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
        self.panel.img_tk = self.img_tk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=self.img_tk)  # show the image

    def update_fill_rate(self):
        if self.fill_rate < 0.25:
            self.bg_color = 'red'
        elif self.fill_rate < 0.6:
            self.bg_color = 'yellow'
        else:
            self.bg_color = 'green'
        self.fill_articles = round(self.fill_rate * self.articles)
        self.fill_article_lbl['text'] = str(self.fill_articles) + '/' + str(self.articles)
        self.fill_article_lbl['bg'] = self.bg_color

    def add_article(self):
        self.articles += 1
        self.update_fill_rate()

    def remove_article(self):
        self.articles = self.articles - 1 if self.articles > 0 else 0
        self.update_fill_rate()

    def set_max_volume(self):
        self.msg_box = messagebox.askquestion("Setting new maximum level", self.msg_box_text)
        if self.msg_box == 'yes':
            self.reset_btn['text'] = 'Set new maximum level'
            self.volume_full = calibrate()
            self.run()

    def run(self):
        # TODO Prb not needed
        print('running')
        self.update_display()
        self.window.after(1000, self.run)


if __name__ == '__main__':
    pipe, align, d_scale = setup_camera_feeds()
    main()
