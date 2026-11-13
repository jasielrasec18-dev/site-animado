"""Mede limites do título (cobre) nas duas imagens, em px de 1920x1080."""
import sys
import numpy as np
from PIL import Image

def limites(caminho):
    a = np.asarray(Image.open(caminho).convert("RGB").resize((1920, 1080))).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    cobre = (r > 110) & (r - b > 45) & (r - g > 15)
    faixa = cobre[150:230]  # topo das letras, acima do relógio
    cols = np.where(faixa.sum(0) > 8)[0]
    cols = cols[cols > 100]
    linhas_t = np.where(cobre[:, 200:300].sum(1) > 20)[0]  # haste do T
    return dict(x0=int(cols.min()), x1=int(cols.max()), y_topo=int(linhas_t[linhas_t > 90].min()), y_base=int(linhas_t[linhas_t < 560].max()))

print("alvo  ", limites("reference/relogio-alvo.png"))
print("pagina", limites(sys.argv[1]))
