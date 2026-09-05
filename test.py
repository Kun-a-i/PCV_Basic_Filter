import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()

# Create Matplotlib Figure
fig = Figure(figsize=(5, 4), dpi=100)
fig.add_subplot(111).plot([1, 2, 3], [4, 5, 6])

# Create the canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()

# Position using grid
canvas_widget.grid(row=0, column=10, padx=20, pady=20)

root.mainloop()
