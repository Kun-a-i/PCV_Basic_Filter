import cv2 as cv
import numpy as np

import tkinter as tk
from PIL import Image, ImageTk

class App:
    def __init__(self, window, window_title):
        #set up main window and camera view
        self.window = window
        self.window_title = window_title
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        