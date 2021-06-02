import tkinter as tk
from PIL import Image, ImageTk
import cv2


class PalletGUI:

    def __init__(self, rgb, fill_rate):
        # Setup variables
        self.rgb = rgb
        self.current_image = None
        self.articles = 0
        self.fill_rate = fill_rate
        self.fill_articles = round(self.fill_rate * self.articles)
        self.bg_color = 'green'

        # Setup GUI window, buttons, and labels
        self.window = tk.Tk()
        self.window.wm_title("Pallet measuring")
        self.img_frame = tk.Frame(master=self.window)
        self.btn_frame = tk.Frame(master=self.window, relief=tk.RAISED)
        self.btn_frame.rowconfigure([0, 1, 2], minsize=50)
        self.btn_frame.columnconfigure([0, 1, 2], minsize=70)

        # Image panel
        self.panel = tk.Label(master=self.img_frame)
        self.panel.pack(padx=10, pady=10)
        # Article text
        self.article_lbl = tk.Label(self.btn_frame, text="Number of articles / Total articles")
        self.article_lbl.grid(row=0, column=0, columnspan=3)
        # Article fill rate text
        self.fill_article_lbl = tk.Label(self.btn_frame, text=self.articles, relief='solid')
        self.fill_article_lbl.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        # Article add/remove buttons
        self.add_btn = tk.Button(self.btn_frame, text="+ total", command=self.add_article)
        self.add_btn.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
        self.rem_btn = tk.Button(self.btn_frame, text="- total", command=self.remove_article)
        self.rem_btn.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Reset volume button
        self.reset_btn = tk.Button(self.btn_frame, text="Set current volume as full", command=self.reset_max_volume)
        self.reset_btn.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.img_frame.pack()
        self.btn_frame.pack()
        self.update_display(self.rgb, self.fill_rate)

    def update_display(self, rgb, fill_rate):
        self.update_fill_rate(fill_rate)
        self.current_image = Image.fromarray(rgb)
        img_tk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
        self.panel.img_tk = img_tk  # anchor imgtk so it does not be deleted by garbage-collector
        self.panel.config(image=img_tk)  # show the image

    def update_fill_rate(self, fill_rate):
        if fill_rate < 0.25:
            self.bg_color = 'red'
        elif fill_rate < 0.6:
            self.bg_color = 'yellow'
        else:
            self.bg_color = 'green'
        self.fill_articles = round(fill_rate * self.articles)
        self.fill_article_lbl['text'] = str(self.fill_articles) + '/' + str(self.articles)
        self.fill_article_lbl['bg'] = self.bg_color

    def add_article(self):
        self.articles += 1
        self.update_fill_rate(self.fill_rate)

    def remove_article(self):
        self.articles = self.articles - 1 if self.articles > 0 else 0
        self.update_fill_rate(self.fill_rate)


    def reset_max_volume(self):
        print('Run re-calibration here')

# For testing
rgb_img = cv2.cvtColor(cv2.imread("data/000069.png"), cv2.COLOR_BGR2RGBA)
p = PalletGUI(rgb_img, 0.5)
p.window.mainloop() # use after instead

