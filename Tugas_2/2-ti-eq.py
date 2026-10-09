from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk

class App :
    def __init__(self, window, window_title):
        #set up main window and camera view
        self.window = window
        self.window_title = window_title
        self.cap = cv2.VideoCapture(0)
        self.canvas = tk.Canvas(window, width=1380, height=480, bg="black")
        self.canvas.pack()
        self.window.title(window_title)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        #set UI
        self.ui = tk.Frame(self.window)
        self.modes = ['Camera', 'Image from file']
        self.select_mode = ttk.Combobox(self.ui, values=self.modes, state='readonly')
        self.select_mode.set('Camera')
        self.select_mode.pack(
            padx=1,
            pady=10
        )
        self.select_mode.bind(
            "<<ComboboxSelected>>",
            self.click_mode
        )

        self.filters = ['Gamma', 'Negatif', 'Lut Stretch', 'Logaritmik']
        self.select_filter = ttk.Combobox(self.ui, values=self.filters, state='readonly')
        self.select_filter.set('Gamma')
        self.select_filter.pack(
            padx=1,
            pady=10
        )
        self.select_filter.bind(
            "<<ComboboxSelected>>",
            self.click_filter
        )
        
        self.r = np.arange(256, dtype=float)

        #UI for Gamma
        self.gamma_frame = tk.Frame(self.ui)
        self.set_gamma = tk.Entry(self.gamma_frame, textvariable=tk.DoubleVar)
        self.set_gamma.insert(0, '1.0')
        self.set_gamma.pack(
            padx=20, pady=20
        )
        self.click_filter()
        
        #UI for selecting image file
        self.button_frame = tk.Frame(self.ui)
        self.select_image_button = tk.Button(
            self.button_frame, 
            text='Open Image', 
            command=self.open_file, 
            activebackground="blue", 
            activeforeground="white"
        )
        self.select_image_button.pack(
            padx=20, pady=20
        )
        self.image_path = None
        self.current_dir = os.getcwd()

        #Histogram for preview Image
        self.fig = Figure(figsize=(5, 3), dpi=100)
        gs = self.fig.add_gridspec(1, 2, wspace=0.2)

        self.ax = self.fig.add_subplot(gs[0, 0])
        self.ax.set_title("Preview Histogram")
        self.ax.set_xlim([0, 256])

        self.filtered_ax = self.fig.add_subplot(gs[0, 1])
        self.filtered_ax.set_title("Filtered Histogram")
        self.filtered_ax.set_xlim([0, 256])

        self.hist_canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas_widget = self.hist_canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=False, anchor=tk.S)

        self.ui.pack()
        self.update_frame()


    def click_mode(self, event =None):
        selected_mode = self.select_mode.get()
        if selected_mode == 'Image from file':
            self.button_frame.pack()
            if self.image_path == None :
                self.open_file()
        elif selected_mode == 'Camera':
            self.button_frame.forget()

    def click_filter(self, event=None):
        self.selected_filter = self.select_filter.get()
        if self.selected_filter == 'Gamma':
            self.gamma_frame.pack()
        else:
            self.gamma_frame.forget()
            
    def apply_filter(self, frame):
        match self.selected_filter:
            case 'Gamma':
                gamma = self.set_gamma.get()
                if gamma == '':
                    gamma = 0.0
                elif gamma == '.':
                    gamma = 0.0
                return self.filter_gamma(frame=frame, gamma=gamma)
            case 'Negatif':
                return self.filter_negatif(frame=frame)
            case 'Logaritmik':
                return self.filter_log(frame=frame)
            case 'Lut Stretch':
                return self.filter_stretch(frame=frame)


    def open_file(self):
        self.image_path = filedialog.askopenfilename(
            title="Select a File",
            initialdir=self.current_dir,
            filetypes=[("png Files", "*.png"), ("jpeg Files", "*.jpeg"), ("jpg Files", "*.jpg"), ("All Files", "*.*")]
        )

    def calculate_his(self, frame, L=256, channel=0, ax=None):
        h, w = frame[:, :, 0].shape
        match channel:
            case 0:
                channel_color = "red"
            case 1:
                channel_color = "green"
            case 2:
                channel_color = "blue"
        size = h*w/16
        hist = np.zeros(L, dtype=np.int32)
        for H in range(int(h/4)):
            for W in range(int(w/4)):
                r = frame[H, W, channel] 
                hist[r] += 1

        hist = np.array(hist)
        hist = hist/size
        
        hist_plot = ax.plot(hist, color=channel_color)
        return hist_plot

    def rapikan(self, lut):
        return np.clip(
            np.floor(lut + 0.5), 
            0, 
            255
        ).astype(np.uint8)
    
    def filter_negatif(self, frame):
        lut_negatif = (255 - self.r)
        return cv2.LUT(frame, self.rapikan(lut_negatif))

    def filter_log(self, frame):
        c = 255.0/np.log(256.0)
        lut_log = c*np.log(1.0 + self.r)
        return cv2.LUT(frame, self.rapikan(lut_log))
    
    def filter_gamma(self, frame, gamma):
        gamma = float(gamma)
        lut_gamma = 255.0 * (self.r / 255.0) ** gamma
        return cv2.LUT(frame, self.rapikan(lut_gamma))

    def filter_stretch(self, frame, r1=80, s1=20, r2=175, s2=240):
        out = np.empty(256, dtype=np.float64)
        bagian1 = self.r < r1
        bagian2 = (self.r >= r1) & (self.r < r2)
        bagian3 = self.r >= r2
        out[bagian1] = (s1 / r1) * self.r[bagian1]
        out[bagian2] = (s2 - s1) / (r2 - r1) * (self.r[bagian2] - r1) + s1
        out[bagian3] = (255 - s2) / (255 - r2) * (self.r[bagian3] - r2) + s2
        return cv2.LUT(frame, self.rapikan(out))

    def update_frame(self):
        mode = self.select_mode.get()
        frame = None
        if mode == 'Camera':
            if self.cap == None :
                self.cap = cv2.VideoCapture(0)
            
            ret, frame = self.cap.read()
            if ret :
                frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv_frame = frame

                #render preview
                self.preview = Image.fromarray(frame)
                self.img_tk_prev = ImageTk.PhotoImage(image=self.preview)
                self.canvas.create_image(0,0, image=self.img_tk_prev, anchor=tk.NW)

        elif mode == 'Image from file' :
            if self.cap :
                self.cap.release() 
                self.cap = None
            
            if self.image_path :
                frame = cv2.imread(self.image_path)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_AREA)
                cv_frame = frame

                #render preview
                self.preview = Image.fromarray(frame)
                self.img_tk_prev = ImageTk.PhotoImage(image=self.preview)
                self.canvas.create_image(0,0, image=self.img_tk_prev, anchor=tk.NW)
        self.ax.clear()
        
        if frame is not None :
            #Apply Filter
            filtered_frame = self.apply_filter(frame=frame)
            filtered_view = Image.fromarray(filtered_frame)
            self.img_tk = ImageTk.PhotoImage(image=filtered_view)
            self.canvas.create_image(720,0, image=self.img_tk, anchor=tk.NW)

            #Calculate and show Histogram
            self.ax.clear()
            self.calculate_his(frame=frame, channel=0, ax=self.ax)
            self.calculate_his(frame=frame, channel=1, ax=self.ax)
            self.calculate_his(frame=frame, channel=2, ax=self.ax)
            self.ax.set_title("Preview Histogram")
            self.ax.set_xlim([0, 256])

            self.filtered_ax.clear()
            self.calculate_his(frame=filtered_frame, channel=0, ax=self.filtered_ax)
            self.calculate_his(frame=filtered_frame, channel=1, ax=self.filtered_ax)
            self.calculate_his(frame=filtered_frame, channel=2, ax=self.filtered_ax)
            self.filtered_ax.set_title("Filtered Histogram")
            self.filtered_ax.set_xlim([0, 256])
            
            self.filtered_ax.grid(True, linestyle="--", alpha=0.5)
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.hist_canvas.draw()
        
        self.window.after(15, self.update_frame)

    def on_closing(self):
        """Clean up video resources on window close."""
        if self.cap :
            self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 2 PCV")
    root.mainloop()