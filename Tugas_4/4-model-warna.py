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

        self.filters = ['RGB',
                        'HSI',
                        'HSV',
                        'CMYK'
                        ]
        self.select_filter = ttk.Combobox(self.ui, values=self.filters, state='readonly')
        self.select_filter.set('RGB')
        self.select_filter.pack(
            padx=1,
            pady=10
        )
        self.selected_filter=self.select_filter.get()
        self.select_filter.bind(
            "<<ComboboxSelected>>",
            self.click_filter
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
    def open_file(self):
            self.image_path = filedialog.askopenfilename(
                title="Select a File",
                initialdir=self.current_dir,
                filetypes=[("png Files", "*.png"), ("jpeg Files", "*.jpeg"), ("jpg Files", "*.jpg"), ("All Files", "*.*")]
            )

    def click_filter(self, event=None):
        self.selected_filter = self.select_filter.get()

    def apply_filter(self, frame):
        match self.selected_filter:
            case 'RGB':
                return self.RGB(frame=frame)
            case 'HSI' :
                return self.HSI(frame=frame)
            case 'CMYK':
                return self.CMYK(frame=frame)
            case 'HSV':
                return self.HSV(frame=frame)
            case _:
                return self.RGB(frame=frame)

    def RGB(self, frame):
        RGB_Frame = frame.copy()
        displays = [
            (frame, "Original"),
            (RGB_Frame, "RGB")

        ]

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
        self.frames=[frame, RGB_Frame]

    def HSV(self, frame):
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(hsv_frame)
        displays = [
            (frame, "Original"),
            (H, "Hue"),
            (S, "Satutation"),
            (V, "Value")
        ]
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
        self.frames = [frame, H, S, V]
        

    def CMYK(self, frame):
        f = frame.astype(np.float64) / 255.0
        B, G, R = f[:, :, 2], f[:, :, 1], f[:, :, 0]

        K = 1 - np.maximum(R, np.maximum(G, R))
        penyebut = 1.0 - K
        C = np.divide(
            1.0 - R - K, penyebut, out=np.zeros_like(R), where=(penyebut > 1e-12)
        )
        M = np.divide(
            1.0 - G - K, penyebut, out=np.zeros_like(G), where=(penyebut > 1e-12)
        )
        Y = np.divide(
            1.0 - B - K, penyebut, out=np.zeros_like(B), where=(penyebut > 1e-12)
        )

        def format_for_display(channel_img):
            img_uint8 = np.clip(channel_img * 255.0, 0, 255).astype(np.uint8)
            return cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2BGR)
        
        frame_display = frame.copy()
        Cyan = format_for_display(C)
        Magenta = format_for_display(M)
        Yellow = format_for_display(Y)
        Key = format_for_display(K)
        CMY = np.dstack((C, M, Y))
        CMY_display = np.clip(CMY * 255.0, 0, 255).astype(np.uint8)
        displays = [
            (frame, "Original"),
            (Cyan, "Cyan"),
            (Magenta, "Magenta"),
            (Yellow, "Yellow"),
            (Key, "Key"),
            (CMY_display, "CMY")
        ]

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
        self.frames = [frame, Cyan, Magenta, Yellow, Key, CMY_display]

    def HSI(self, frame):
        f = frame.astype(np.float64) / 255.0
        B, G, R = f[:, :, 2], f[:, :, 1], f[:, :, 0]

        pembilang = 0.5 * ((R - G) + (R - B))
        penyebut = np.sqrt(np.square(R - G) + (R - B) * (G - B))

        rasio = np.divide(
            pembilang,
            penyebut,
            out=np.zeros_like(pembilang),
            where=penyebut > 1e-12,
        )

        theta = np.degrees(np.arccos(np.clip(rasio, -1.0, 1.0)))
        hue = np.where(B <= G, theta, 360.0 - theta)

        jumlah = R + G + B
        saturation = 1.0 - 3.0 * np.minimum(np.minimum(R, G), B) / np.where(
            jumlah == 0, 1.0, jumlah
        )
        intensity = jumlah / 3.0

        def format_for_display(img_single_channel, scale=255.0):
            img_uint8 = np.clip(img_single_channel * scale, 0, 255).astype(np.uint8)    
            return cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2BGR)

        hue_display = format_for_display(hue / 360.0)  
        sat_display = format_for_display(saturation)  
        int_display = format_for_display(intensity)  
        displays = [
            (frame, "Original"),
            (hue_display, "Hue"),
            (sat_display, "Saturation"),
            (int_display, "Intensity")
        ]

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

        self.frames = [frame, hue_display, sat_display, int_display]
                
                

        

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
                cv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

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

                #render preview
                self.img_tk_prev=[]
                self.apply_filter(frame)
                for i in range(len(self.frames)):
                    preview = Image.fromarray(self.frames[i])
                    self.img_tk_prev.append(
                        ImageTk.PhotoImage(image=preview)
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
    App(root, "Tugas 4 PCV")
    root.mainloop()