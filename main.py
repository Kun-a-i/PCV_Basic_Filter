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
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        #set up  button for GUI
        self.selected_filter = None
        self.filter = ['rgb', 'grayscale', 'red', 'green', 'blue', 'magenta','yellow', 'cyan']
        self.filters = ttk.Combobox(self.window, values=self.filter, state='readonly')
        self.filters.set('rgb')
        self.filters.pack(
            padx=1, 
            pady=10
            )
        self.filters.bind(
            "<<ComboboxSelected>>", 
            self.click_filter
            )

        # set up 3D plot for each channel
        self.fig_red = Figure(figsize=(5, 5), dpi=100)
        self.ax_red = self.fig_red.add_subplot(projection='3d', proj_type='ortho')
        self.plot_canvas_red = FigureCanvasTkAgg(self.fig_red, master=self.window)
        self.canvas_widget_red = self.plot_canvas_red.get_tk_widget()
        self.canvas_widget_red.pack(side="left")

        self.fig_green = Figure(figsize=(5, 5), dpi=100)
        self.ax_green = self.fig_green.add_subplot(projection='3d', proj_type='ortho')
        self.plot_canvas_green = FigureCanvasTkAgg(self.fig_green, master=self.window)
        self.canvas_widget_green = self.plot_canvas_green.get_tk_widget()
        self.canvas_widget_green.pack(side="left")

        self.fig_blue = Figure(figsize=(5, 5), dpi=100)
        self.ax_blue = self.fig_blue.add_subplot(projection='3d', proj_type='ortho')
        self.plot_canvas_blue = FigureCanvasTkAgg(self.fig_blue, master=self.window)
        self.canvas_widget_blue = self.plot_canvas_blue.get_tk_widget()
        self.canvas_widget_blue.pack(side="left")

        self.update_frame()

    def update_frame(self):
        cv_frame=None
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1) 
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv_frame = frame

            #render preview
            self.preview = Image.fromarray(frame)
            self.img_tk_prev = ImageTk.PhotoImage(image=self.preview)
            self.canvas.create_image(0, 0, image=self.img_tk_prev, anchor=tk.NW)

            # set filter
            match self.selected_filter:
                case 'rgb':
                    cv_frame = frame
                case 'grayscale':
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    cv_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                case 'red':
                    cv_frame[:,:,2] = 0
                    cv_frame[:,:,1] = 0
                case 'green':
                    cv_frame[:,:,2] = 0
                    cv_frame[:,:,0] = 0
                case 'blue':
                    cv_frame[:,:,0] = 0
                    cv_frame[:,:,1] = 0
                case 'magenta':
                    # cv_frame[:,:,0] = 0
                    cv_frame[:,:,1] = 0
                    # cv_frame[:,:,2] = 0
                case 'yellow' :
                    # cv_frame[:,:,0] = 0
                    # cv_frame[:,:,1] = 0
                    cv_frame[:,:,2] = 0
                case 'cyan' :
                    cv_frame[:,:,0] = 0
                    # cv_frame[:,:,1] = 0
                    # cv_frame[:,:,2] = 0

            # render filtered
            self.photo = Image.fromarray(cv_frame)
            self.img_tk = ImageTk.PhotoImage(image=self.photo)
            self.canvas.create_image(720, 0, image=self.img_tk, anchor=tk.NW)


            # render 3D plot
            self.create_3d_scatter(cv_frame)

        self.window.after(15, self.update_frame)

    def click_filter(self, event=None):
        self.selected_filter = self.filters.get()
        # print(self.selected_filter)

    def create_3d_scatter(self, frame):
        red_channel = frame[::16, ::16, 0]
        green_channel = frame[::16, ::16, 1]
        blue_channel = frame[::16, ::16, 2]

        h, w = red_channel.shape

        x = np.arange(0, w)
        y = np.arange(0, h)
        X, Y = np.meshgrid(x, y)

        self.ax_red.cla()
        self.ax_green.cla()
        self.ax_blue.cla()

        #plot channel intensity surfaces/scatters
        self.ax_red.scatter(
            X, Y, red_channel, color="red", label="Red"
        )
        self.ax_green.scatter(
            X, Y, green_channel, color="green", label="Green"
        )
        self.ax_blue.scatter(
            X, Y, blue_channel, color="blue", label="Blue"
        )

        self.ax_red.set_zlim([0,255])
        self.ax_red.set_xlabel("X")
        self.ax_red.set_ylabel("Y")

        self.ax_green.set_zlim([0,255])
        self.ax_green.set_xlabel("X")
        self.ax_green.set_ylabel("Y")

        self.ax_blue.set_zlim([0,255])
        self.ax_blue.set_xlabel("X")
        self.ax_blue.set_ylabel("Y")

        self.plot_canvas_red.draw()
        self.plot_canvas_green.draw()
        self.plot_canvas_blue.draw()

    def on_closing(self):
        """Clean up video resources on window close."""
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 1 PCV")
    root.mainloop()