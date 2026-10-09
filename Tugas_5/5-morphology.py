from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import cv2
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import math

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
        selected_mode = self.select_mode.get()
        self.filters = ['Erosi',
                        'Dilasi',
                        'Opening',
                        'Closing',
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
        self.selected_filter = self.select_filter.get()
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

        self.kernel_frame = tk.Frame(self.ui)
        self.set_kernel = tk.Entry(self.kernel_frame, textvariable=tk.IntVar)
        self.set_kernel.insert(1, '5')
        
        label = tk.Label(self.kernel_frame, text="Kernel Size:")
        label.pack(anchor=tk.N)
        self.set_kernel.pack(
            padx=20, pady=20, anchor=tk.N
        )
        self.kernel_frame.pack()
        # Rectangular Kernel
        self.rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

        # Elliptical Kernel
        self.ellipse_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

        # Cross-shaped Kernel
        self.cross_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))


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
            filetypes=[("png Files", "*.png"), ("jpeg Files", "*.JPEG"), ("jpg Files", "*.JPG"), ("All Files", "*.*")]
        )

    def click_filter(self, event=None):
        self.selected_filter = self.select_filter.get()

    def update_kernel(self):
        input_val = self.set_kernel.get().strip()

        if input_val in ("", "."):
            size = 1
        else:
            try:
                size = int(float(input_val))
            except ValueError:
                size = 1

        if size < 1:
            size = 1
        
        kernel_size = (size, size)

        self.rect_kernel    = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        self.ellipse_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
        self.cross_kernel   = cv2.getStructuringElement(cv2.MORPH_CROSS, kernel_size)

    def apply_filter(self, frame):
        match self.selected_filter:
            case 'Dilasi':
                return self.dilasi(frame)
            case 'Erosi':
                return self.erosi(frame)
            case 'Opening':
                return self.opening(frame)
            case 'Closing':
                return self.closing(frame)
            case _:
                displays = [(frame, "Original")]
                self.put_names(displays)
                self.frames = [frame]
                return
    def dilasi(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        dilasi_rect     = cv2.dilate(thresh, self.rect_kernel, iterations=1)
        dilasi_cross    = cv2.dilate(thresh, self.cross_kernel, iterations=1)
        dilasi_elipse   = cv2.dilate(thresh, self.ellipse_kernel, iterations=1)

        displays = [
            (frame, "Original"),
            (thresh, "Thresholding"),
            (dilasi_rect, "Dilasi Kotak"),
            (dilasi_cross, "Dilasi Salib"),
            (dilasi_elipse, "Dilasi Slips")
        ]

        self.put_names(displays)

        self.frames = [frame, thresh, dilasi_rect, dilasi_cross, dilasi_elipse]
        
    def erosi(self, frame):
        gray_frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, thresh   = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        erosi_rect  = cv2.erode(thresh, self.rect_kernel, iterations=1)
        erosi_cross = cv2.erode(thresh, self.cross_kernel, iterations=1)
        erosi_elipse= cv2.erode(thresh, self.ellipse_kernel, iterations=1)

        displays = [
            (frame, "Original"),
            (thresh, "Thresholding"),
            (erosi_rect, "Erosi Kotak"),
            (erosi_cross, "Erosi Salib"),
            (erosi_elipse, "Erosi Elips")
        ]
        self.put_names(displays=displays)

        self.frames = [frame, thresh,  erosi_rect, erosi_cross, erosi_elipse]

    def opening(self, frame):
        gray_frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, thresh   = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
        erosi_rect  = cv2.erode(thresh, self.rect_kernel, iterations=1)
        erosi_cross = cv2.erode(thresh, self.cross_kernel, iterations=1)
        erosi_elipse= cv2.erode(thresh, self.ellipse_kernel, iterations=1)

        opening_rect    = cv2.dilate(erosi_rect, self.rect_kernel, iterations=1)
        opening_cross   = cv2.dilate(erosi_cross, self.cross_kernel, iterations=1)
        opening_elipse  = cv2.dilate(erosi_elipse, self.ellipse_kernel, iterations=1)

        displays = [
            (frame, "Original"),
            (thresh, "Thresholding"),
            (opening_rect,  "Opening Kotak"),
            (opening_cross, "Opening Salib"),
            (opening_elipse,"Opening Elips")
        ]
        self.put_names(displays=displays)

        self.frames = [frame, thresh, opening_rect, opening_cross, opening_elipse]

    def closing(self, frame):
        gray_frame  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, thresh   = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)

        dilasi_rect    = cv2.dilate(thresh, self.rect_kernel, iterations=1)
        dilasi_cross   = cv2.dilate(thresh, self.cross_kernel, iterations=1)
        dilasi_elipse  = cv2.dilate(thresh, self.ellipse_kernel, iterations=1)

        closing_rect  = cv2.erode(dilasi_rect, self.rect_kernel, iterations=1)
        closing_cross = cv2.erode(dilasi_cross, self.cross_kernel, iterations=1)
        closing_elipse= cv2.erode(dilasi_elipse, self.ellipse_kernel, iterations=1)

        displays = [
            (frame, "Original"),
            (thresh, "Thresholding"),
            (closing_rect,  "Closing Kotak"),
            (closing_cross, "Closing Salib"),
            (closing_elipse,"Closing Elips")
        ]
        self.put_names(displays=displays)

        self.frames = [frame, thresh, closing_rect, closing_cross, closing_elipse]


    def put_names(self, displays):
        for img, text in displays:
            cv2.putText(
                        img=img,
                        text=text,
                        org=(30, 50),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(255, 0, 0),
                        thickness=2,
                        lineType=cv2.LINE_AA,
                        )

    def update_frame(self):
        self.update_kernel()
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
                self.img_tk_prev=[]
                self.apply_filter(frame)
                for i in range(len(self.frames)):
                    self.preview = Image.fromarray(self.frames[i])
                    self.img_tk_prev.append(
                        ImageTk.PhotoImage(image=self.preview)
                    )
                    self.canvas.create_image(640*(i%2), 480*(int(i/2)), image=self.img_tk_prev[i], anchor=tk.NW)

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
                self.img_tk_prev=[]
                self.apply_filter(frame)
                for i in range(len(self.frames)):
                    self.preview = Image.fromarray(self.frames[i])
                    self.img_tk_prev.append(
                        ImageTk.PhotoImage(image=self.preview)
                    )
                    self.canvas.create_image(640*(i%2), 480*(int(i/2)), image=self.img_tk_prev[i], anchor=tk.NW)

        i = len(self.frames)
        self.canvas.config(width=640*(min(i,2)), height=480*(min(i,math.ceil(i/2))))

        self.window.after(15, self.update_frame)

    def on_closing(self):
            """Clean up video resources on window close."""
            if self.cap :
                self.cap.release()
            self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 5 PCV")
    root.mainloop()