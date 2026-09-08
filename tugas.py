import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.figure import Figure

GAMBAR_KONTRAS_RENDAH = "/home/kuna.ibad/Documents/Project Python/PCV_Tugas 1/foto/lowcontrast.jpeg"
GAMBAR_GELAP = "/home/kuna.ibad/Documents/Project Python/PCV_Tugas 1/foto/lowlight.jpeg"
GAMBAR_TERANG = "/home/kuna.ibad/Documents/Project Python/PCV_Tugas 1/foto/toomuchlight.jpeg"

class App :
    def __init__(self, window, window_title):
        #set up main window and camera view
        self.window = window
        self.window_title = window_title
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bnw = False

        #load image menu
        self.img = None
        self.ui = tk.Frame(self.window)
        self.pilihan_foto = ['gambar_gelap', 'gambar_terang', 'gambar_kontras_rendah']
        self.pilih = ttk.Combobox(
            master=self.ui, 
            values=self.pilihan_foto, 
            state='readonly'
        )
        self.pilih.pack(padx=10, pady=20)
        self.pilih.bind(
             "<<ComboboxSelected>>",
             self.foto_terpilih
        )

        self.pilihan_resolusi = ['1440x1080', '8x8', '1440x1080 B&W', '8x8 B&W']
        self.pilih_reso = ttk.Combobox(
            master=self.ui, 
            values=self.pilihan_resolusi, 
            state='readonly'
        )
        self.pilih_reso.pack(padx=10, pady=20)
        self.pilih_reso.bind(
            "<<ComboboxSelected>>",
            self.resolusi_terpilih
        )
        self.img_frame = tk.Frame(master=window)
        self.ui.pack(side="left")

        #image info

        self.label_info = tk.Text(self.window, height=20, width=36, state=tk.DISABLED)

        self.label_info.tag_config("title_tag", font=("Arial", 10, "bold"), foreground="blue")
        self.label_info.tag_config("red_tag", background="#ffcccc", foreground="black")  
        self.label_info.tag_config("green_tag", background="#ccffcc", foreground="black")
        self.label_info.tag_config("blue_tag", background="#ccccff", foreground="black") 
\

        self.label_info.pack(side="right")

    def foto_terpilih(self, event=None) :
        rgb_img = None
        match self.pilih.get() :
            case 'gambar_gelap':
                self.img = cv2.imread(GAMBAR_GELAP)
            case 'gambar_terang' :
                self.img = cv2.imread(GAMBAR_TERANG)
            case 'gambar_kontras_rendah' :
                self.img = cv2.imread(GAMBAR_KONTRAS_RENDAH)
            case _:
                self.img = None
        self.resolusi_terpilih()
        


    def resolusi_terpilih(self, event=None) :
        
        if self.img is not None  :
            for widget in self.img_frame.winfo_children():
                widget.destroy()
            
            rgb_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            h, w =rgb_img[:,:,0].shape
            match self.pilih_reso.get():
                case '1440x1080' :
                    img_8x8 = cv2.resize(rgb_img, (1080, 1440), interpolation=cv2.INTER_AREA)
                    self.get_img_info(img_8x8)
                    pil_img = Image.fromarray(img_8x8)
                    tk_img = ImageTk.PhotoImage(image=pil_img)
                    label = tk.Label(self.img_frame, image=tk_img)
                    label.image = tk_img
                    self.img_frame.pack()
                    label.pack()
                case '8x8':
                    img_8x8 = cv2.resize(rgb_img, (8, 8) , interpolation=cv2.INTER_AREA)
                    self.get_img_info(img_8x8)
                    img_8x8 = cv2.resize(img_8x8, (int(w/4), int(w/4)), interpolation=cv2.INTER_AREA)
                    pil_img = Image.fromarray(img_8x8)
                    tk_img = ImageTk.PhotoImage(image=pil_img)
                    label = tk.Label(self.img_frame, image=tk_img)
                    label.image = tk_img
                    self.img_frame.pack()
                    label.pack()
                case '1440x1080 B&W':
                    bw_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
                    img_8x8 = cv2.resize(bw_img, (1080, 1440), interpolation=cv2.INTER_AREA)
                    self.get_img_info(img_8x8)
                    pil_img = Image.fromarray(img_8x8)
                    tk_img = ImageTk.PhotoImage(image=pil_img)
                    label = tk.Label(self.img_frame, image=tk_img)
                    label.image = tk_img
                    self.img_frame.pack()
                    label.pack()
                      
                case '8x8 B&W':             
                    bw_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
                    img_8x8 = cv2.resize(bw_img, (8, 8) , interpolation=cv2.INTER_AREA)
                    self.get_img_info(img_8x8)
                    img_8x8 = cv2.resize(img_8x8, (int(w/4), int(w/4)), interpolation=cv2.INTER_AREA)
                    pil_img = Image.fromarray(img_8x8)
                    tk_img = ImageTk.PhotoImage(image=pil_img)
                    label = tk.Label(self.img_frame, image=tk_img)
                    label.image = tk_img
                    self.img_frame.pack()
                    label.pack()

            
        else : 
            self.img_frame.pack_forget()

    def get_img_info(self, img):
        if img is None:
            return

        height, width, channels = None, None, None

        if (self.pilih_reso.get() == '1440x1080') or (self.pilih_reso.get() == '8x8'):
            height, width, channels = img.shape
        else:
            height, width = img.shape[:2]
            channels = 1

        dtype = img.dtype


        self.label_info.config(state=tk.NORMAL)
        self.label_info.delete("1.0", tk.END)  
        
        self.label_info.insert("end",  "=========== INFO GAMBAR ===========\n", "title_tag")
        self.label_info.insert("end", f"Dimensi   : {width} x {height} ({channels} Channel)\n")
        self.label_info.insert("end", f"Tipe Data : {dtype}\n\n")

        if channels == 3:
            blue_min, blue_max, blue_mean = np.min(img[:, :, 2]), np.max(img[:, :, 2]), np.mean(img[:,:,2])
            green_min, green_max, green_mean = np.min(img[:, :, 1]), np.max(img[:, :, 1]), np.mean(img[:,:,1])
            red_min, red_max, red_mean = np.min(img[:, :, 0]), np.max(img[:, :, 0]), np.mean(img[:,:,0])            

            self.label_info.insert("end", f"Red Channel   :\n", "red_tag")
            self.label_info.insert("end", f"Min={red_min}, Max={red_max}, Mean={red_mean:.2f}\n", "red_tag")

            self.label_info.insert("end", f"Green Channel :\n", "green_tag")
            self.label_info.insert("end", f"Min={green_min}, Max={green_max}, Mean={green_mean:.2f}\n", "green_tag")

            self.label_info.insert("end", f"Blue Channel  :\n", "blue_tag")
            self.label_info.insert("end", f"Min={blue_min}, Max={blue_max}, Mean={blue_mean:.2f}\n", "blue_tag")

        elif channels ==1:
            min_val, max_val, mean_val =  np.min(img[:, :]), np.max(img[:, :]), np.mean(img[:,:])
            self.label_info.insert("end", f"Channel Value  :\n", "red_tag")
            self.label_info.insert("end", f"Min={min_val:.2f}, Max={max_val:.2f}, Mean={mean_val:.2f}\n")


        self.label_info.config(state=tk.DISABLED)
        
        

    def on_closing(self):
            """Clean up video resources on window close."""
            self.window.destroy()


#start app
if __name__ == "__main__":
    root = tk.Tk()
    App(root, "Tugas 1 PCV")
    root.mainloop()