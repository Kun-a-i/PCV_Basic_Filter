import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
    def update_frame(self):
        cv_frame=None
        frame = None
        if self.cap :
            ret, frame = self.cap.read()
            h, w = frame[:,:,0].shape
            if ret:
                frame = cv2.flip(frame, 1) 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv_frame = frame

                #render preview
                self.preview = Image.fromarray(frame)
                self.img_tk_prev = ImageTk.PhotoImage(image=self.preview)
                self.canvas.create_image(0, 0, image=self.img_tk_prev, anchor=tk.NW)
                self.apply_filter(frame, cv_frame, h, w)
        else :
            frame = cv2.resize(self.selected_photo, (640, 480), interpolation=cv2.INTER_AREA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv_frame = frame
            h, w = frame[:,:,0].shape
            self.preview = Image.fromarray(frame)
            self.img_tk_prev = ImageTk.PhotoImage(image=self.preview)
            self.canvas.create_image(0, 0, image=self.img_tk_prev, anchor=tk.NW)
            self.apply_filter(frame, cv_frame, h, w)

        

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