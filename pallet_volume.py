import tkinter as tk
from PIL import Image, ImageTk


class PalletGUI:
    def __init__(self,
                 add_btn_callback,
                 rem_btn_callback,
                 measure_btn_callback,
                 calibrate_btn_callback):
        # Setup variables
        self.current_image = None
        self.low_threshold = 0.25
        self.high_threshold = 0.6

        # Setup GUI window, buttons, and labels
        self.root = tk.Tk()
        self.root.wm_title("Volume sensor")
        self.img_frame = tk.Frame(master=self.root)
        self.btn_frame = tk.Frame(master=self.root, relief=tk.RAISED)
        self.btn_frame.rowconfigure([0, 1], minsize=50)
        self.btn_frame.columnconfigure([0, 1, 2, 3, 4, 5], minsize=70)

        # Image panel
        self.img_lbl = tk.Label(master=self.img_frame)
        self.img_lbl.pack(padx=10, pady=10)
        # Article text
        self.article_lbl = tk.Label(self.btn_frame, text="Maximum number of articles: " + "-")
        self.article_lbl.grid(row=0, column=0, columnspan=2)
        # Article add/remove buttons
        self.add_btn = tk.Button(self.btn_frame, text="+", command=add_btn_callback)
        self.add_btn.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.rem_btn = tk.Button(self.btn_frame, text="-", command=rem_btn_callback)
        self.rem_btn.grid(row=0, column=3, sticky="nsew", padx=10, pady=10)
        # Article fill rate text
        self.fill_article_lbl = tk.Label(self.btn_frame, text="-", relief='solid')
        self.fill_article_lbl.config(font=("Courier", 44))
        self.fill_article_lbl.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Reset volume button
        self.measure_btn = tk.Button(self.btn_frame, text="Take Measurement", command=measure_btn_callback)
        self.measure_btn.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.calibrate_btn = tk.Button(self.btn_frame, text="Calibrate Full", command=calibrate_btn_callback)
        self.calibrate_btn.grid(row=1, column=4, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.img_frame.pack()
        self.btn_frame.pack()

    def update_image(self, rgb):
        self.current_image = Image.fromarray(rgb)
        # anchor img_tk so it does not be deleted by garbage-collector
        self.img_lbl.img_tk = ImageTk.PhotoImage(image=self.current_image)
        self.img_lbl.config(image=self.img_lbl.img_tk)  # show the image

    def update_fill_rate(self, fill_rate, num_articles, max_articles):
        if fill_rate < self.low_threshold:
            color = 'red'
        elif fill_rate < self.high_threshold:
            color = 'yellow'
        else:
            color = 'green'
        text = str(num_articles) + '/' + str(max_articles)
        self.fill_article_lbl["text"] = text
        self.fill_article_lbl["bg"] = color
