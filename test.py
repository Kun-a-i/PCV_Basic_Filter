import tkinter as tk

root = tk.Tk()
root.geometry("400x200")

# 1. Gunakan tk.Text (bukan Label)
text_info = tk.Text(root, height=5, width=40)
text_info.pack(pady=20)

# 2. Buat Tag untuk warna highlight
# 'background' untuk warna highlight/stabilo, 'foreground' untuk warna teks
text_info.tag_config("highlight_kuning", background="yellow", foreground="black")
text_info.tag_config("highlight_merah", background="red", foreground="white")

# 3. Masukkan teks (Pastikan state tk.NORMAL dulu jika sebelumnya DISABLED)
text_info.config(state=tk.NORMAL)

# Cara A: Terapkan tag langsung saat insert teks
text_info.insert("end", "Ini adalah teks ")
text_info.insert("end", "baris pertama", "highlight_kuning")  # Hanya kata ini yang dihighlight
text_info.insert("end", ".\n")

text_info.insert("end", "Peringatan: ", "highlight_merah")
text_info.insert("end", "Terjadi kesalahan pada sistem.\n")

# Disable kembali agar tidak bisa diedit pengguna
text_info.config(state=tk.DISABLED)

root.mainloop()