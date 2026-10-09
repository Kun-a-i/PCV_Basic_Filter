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

        self.filters = ['Mean',
                        'Sharpen',
                        'Gaussian',
                        'Laplacian 4',
                        'Laplacian 8',
                        'Sobel X',
                        'Sobel Y',
                        'Sobel',
                        'No Filter'
                        ]
        self.select_filter = ttk.Combobox(self.ui, values=self.filters, state='readonly')
        self.select_filter.set('No Filter')
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

        #Kernels
        self.sharp_kernel = np.array(
                            [[ 0, -1,  0],
                            [-1,  5, -1],
                            [ 0, -1,  0]], np.float64
                            )
        self.mean_kernel = (1.0/25.0)*np.array(
                            [[1, 1, 1, 1, 1],
                            [ 1, 1, 1, 1, 1],
                            [ 1, 1, 1, 1, 1],
                            [ 1, 1, 1, 1, 1],
                            [ 1, 1, 1, 1, 1]], np.float64
                            )
        self.gaussian_kernel = (1.0/16)*np.array(
                            [[1, 2, 1],
                            [ 2, 4, 2],
                            [ 1, 2, 1]], np.float64
                            )
        self.lap4_kernel = np.array(
                            [[0, 1, 0],
                            [ 1, -4, 1],
                            [ 0, 1, 0]], np.float64
                            )
        self.lap8_kernel = np.array(
                            [[1, 1, 1],
                            [ 1, -8, 1],
                            [ 1, 1, 1]], np.float64
                            )
        self.sobelx = np.array(
                            [[-1, 0, 1],
                            [ -2, 0, 2],
                            [ -1, 0, 1]], np.float64
                            )
        self.sobely = np.array(
                            [[-1, 2, -1],
                            [ 0, 0, 0],
                            [ -1, 2, -1]], np.float64
                            )

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
            case 'Mean':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.mean_kernel)
            case 'Sharpen':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.sharp_kernel)
            case 'Gaussian':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.gaussian_kernel)
            case 'Laplacian 4':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.lap4_kernel)
            case 'Laplacian 8':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.lap8_kernel)
            case 'Sobel X':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.sobelx)
            case 'Sobel Y':
                return cv2.filter2D(src=frame, ddepth=-1, kernel=self.sobely)
            case 'Sobel':
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                frame = cv2.filter2D(src=frame, ddepth=-1, kernel=self.sobelx)
                frame = cv2.filter2D(src=frame, ddepth=-1, kernel=self.sobely)
                return frame
            case _:
                return frame

    def open_file(self):
        self.image_path = filedialog.askopenfilename(
            title="Select a File",
            initialdir=self.current_dir,
            filetypes=[("png Files", "*.png"), ("jpeg Files", "*.jpeg"), ("jpg Files", "*.jpg"), ("All Files", "*.*")]
        )

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
      
        if frame is not None :
            #Apply Filter
            filtered_frame = self.apply_filter(frame=frame)
            filtered_view = Image.fromarray(filtered_frame)
            self.img_tk = ImageTk.PhotoImage(image=filtered_view)
            self.canvas.create_image(720,0, image=self.img_tk, anchor=tk.NW)

        
        self.window.after(15, self.update_frame)

    def on_closing(self):
        """Clean up video resources on window close."""
        if self.cap :
            self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 3 PCV")
    root.mainloop()