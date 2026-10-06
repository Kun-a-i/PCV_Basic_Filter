import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Tkinter Plot Example")

# Create Matplotlib figure and axis
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

# Plot data and set the plot title
ax.plot([1, 2, 3, 4], [1, 4, 9, 16])
ax.set_title("My Embedded Plot Title") 

# Embed into Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()
