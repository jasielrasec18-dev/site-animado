"""Remove o fundo verde chroma (#00FF00) de uma imagem e exporta em webp.

Uso: python tools/recortar_verde.py entrada.png saida.webp
"""
import sys

import numpy as np
from PIL import Image, ImageFilter


def recortar(caminho_entrada, caminho_saida):
    img = Image.open(caminho_entrada).convert("RGB")
    rgb = np.asarray(img).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    # Transparência pela diferença entre o verde e o maior valor de vermelho/azul.
    # Diferença alta = fundo verde (transparente); baixa = relógio (opaco).
    diferenca = g - np.maximum(r, b)
    limite_opaco, limite_transparente = 20.0, 90.0
    alfa = 1.0 - np.clip((diferenca - limite_opaco) / (limite_transparente - limite_opaco), 0, 1)

    # Remoção do reflexo verde: o verde nunca passa do maior entre vermelho e azul.
    g_limpo = np.minimum(g, np.maximum(r, b))
    rgb_limpo = np.stack([r, g_limpo, b], axis=-1)

    # Corte no contorno: mantém só o maior objeto e fecha pequenos buracos.
    mascara = Image.fromarray((alfa * 255).astype(np.uint8))
    solido = mascara.point(lambda v: 255 if v > 128 else 0)
    solido = solido.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    rotulo = _maior_componente(np.asarray(solido) > 0)
    regiao = Image.fromarray((rotulo * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))
    alfa = alfa * (np.asarray(regiao) / 255.0)

    # Encolhe a borda 1px e suaviza para não deixar halo.
    alfa_img = Image.fromarray((alfa * 255).astype(np.uint8))
    alfa_img = alfa_img.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    alfa = np.asarray(alfa_img).astype(np.float32) / 255.0

    # Recorta a área vazia ao redor do relógio.
    ys, xs = np.where(alfa > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([rgb_limpo, alfa * 255]).clip(0, 255).astype(np.uint8)[y0:y1, x0:x1]

    Image.fromarray(rgba, "RGBA").save(caminho_saida, "WEBP", quality=90, method=6)
    print(f"{caminho_saida}: {x1 - x0}x{y1 - y0} (corte x{x0}-{x1}, y{y0}-{y1})")


def _maior_componente(mascara):
    """Rotula componentes conectados e devolve só o maior (busca em largura)."""
    altura, largura = mascara.shape
    rotulos = np.zeros(mascara.shape, np.int32)
    tamanhos = {}
    atual = 0
    for y0, x0 in zip(*np.where(mascara)):
        if rotulos[y0, x0]:
            continue
        atual += 1
        pilha = [(y0, x0)]
        rotulos[y0, x0] = atual
        n = 0
        while pilha:
            y, x = pilha.pop()
            n += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < altura and 0 <= nx < largura and mascara[ny, nx] and not rotulos[ny, nx]:
                    rotulos[ny, nx] = atual
                    pilha.append((ny, nx))
        tamanhos[atual] = n
    maior = max(tamanhos, key=tamanhos.get)
    return rotulos == maior


if __name__ == "__main__":
    recortar(sys.argv[1], sys.argv[2])
