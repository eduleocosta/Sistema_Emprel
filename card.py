from PIL import Image, ImageDraw, ImageFont
import numpy as np

caminho_imagem = r"C:\Users\EMPREL03\Desktop\Sistema Emprel 03\img\card.png"

img = Image.open(caminho_imagem).convert("RGB")
draw = ImageDraw.Draw(img)

# Gradient rect
def gradient_rect(width, height, top_color, bottom_color):
    base = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        base[y, :] = (r, g, b)
    return Image.fromarray(base)

x1, y1, x2, y2 = 150, 30, 1150, 320
grad = gradient_rect(x2 - x1, y2 - y1, (0, 90, 180), (0, 50, 120))
img.paste(grad, (x1, y1))

try:
    fonte_topo = ImageFont.truetype("arialbd.ttf", 140)
    fonte_baixo = ImageFont.truetype("arialbd.ttf", 110)
except:
    fonte_topo = ImageFont.load_default()
    fonte_baixo = ImageFont.load_default()

# Texto
def texto(draw, pos, txt, fonte, cor):
    x, y = pos
    draw.text((x+4, y+4), txt, font=fonte, fill=(0,0,0))
    draw.text((x, y), txt, font=fonte, fill=cor)

texto(draw, (180, 40), "VAN", fonte_topo, "white")
texto(draw, (180, 170), "CONECTA RECIFE", fonte_baixo, (160,255,0))

saida = r"C:\Users\EMPREL03\Desktop\Sistema Emprel 03\img\resultado_final.png"
img.save(saida)

print("Imagem salva em:", saida)