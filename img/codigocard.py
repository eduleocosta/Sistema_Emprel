from PIL import Image
import numpy as np

img = Image.open(r"C:\Users\EMPREL03\Desktop\Sistema Emprel 03\img\resultado_final.png").convert("RGB")

np_img = np.array(img)

r, g, b = np_img[:,:,0], np_img[:,:,1], np_img[:,:,2]

mask = (b > 100) & (b > r) & (b > g)

nova_cor = (200, 30, 30)

np_img[mask] = [
    nova_cor[0],
    nova_cor[1],
    nova_cor[2]
]

nova_img = Image.fromarray(np_img)
nova_img.save(r"C:\Users\EMPREL03\Desktop\Sistema Emprel 03\img\Card.png")

print("Cor alterada!")