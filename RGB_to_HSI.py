import numpy as np

R = 144
G = 190
B = 222

R = R/255
G = G/255
B = B/255

pembilang = 0.5*((R-G)+(R-B))

penyebut = np.sqrt(np.square(R-G)+(R-B)*(G-B))

theta = np.arccos(pembilang/penyebut)
theta = np.degrees(theta)
if(B>G):
    theta = 360 -theta
print(f"Nilai Theta      : {theta}")

saturation = 1 - (3/(R+G+B))*min(R, G, B)
print(f"Nilai Saturasi   : {saturation}")

intensity = (R+G+B)/3
print(f"Nilai Intensitas : {intensity}")

