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

        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Color Histogram")
        self.ax.set_xlim([0, 256])

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

    def open_file(self):
        self.image_path = filedialog.askopenfilename(
            title="Select a File",
            initialdir=self.current_dir,
            filetypes=[("png Files", "*.png"), ("jpeg Files", "*.jpeg"), ("jpg Files", "*.jpg"), ("All Files", "*.*")]
        )

    def calculate_his(self, frame, L=256, channel=0):
        h, w = frame[:, :, 0].shape
        match channel:
            case 0:
                channel_color = "red"
            case 1:
                channel_color = "green"
            case 2:
                channel_color = "blue"

        hist = np.zeros(L, dtype=np.int32)
        for H in range(int(h)):
            for W in range(int(w)):
                r = frame[H, W, channel] 
                hist[r] += 1
        
        hist_plot = self.ax.plot(hist, color=channel_color)
        return hist_plot

    def update_frame(self):
        mode = self.select_mode.get()
        frame = None
        if mode == 'Camera':
            if self.cap == None :
                self.cap = cv2.VideoCapture(0)
            
            ret, frame = self.cap.read()
            if ret :
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
            # 1. Clear the old histogram lines from the axis
            self.ax.clear()

            # 2. Plot updated channel histograms
            self.calculate_his(frame=frame, channel=0)
            self.calculate_his(frame=frame, channel=1)
            self.calculate_his(frame=frame, channel=2)

            # 3. Restore axis settings after clearing
            self.ax.set_xlim([0, 256])
            self.ax.grid(True, linestyle="--", alpha=0.5)

            # 4. Redraw the Matplotlib canvas in Tkinter
            self.hist_canvas.draw()
        
        self.window.after(15, self.update_frame)

    def on_closing(self):
        """Clean up video resources on window close."""
        if self.cap :
            self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 1 PCV")
    root.mainloop()