"""Mede a escala e o deslocamento que alinham o 1º frame do filme com o start frame.

Modelo (igual ao CSS `transform: translate(tx, ty) scale(s)`, origem no centro):
    saída = centro + t + s * (frame - centro)
Uso: python tools/alinhar.py [assets/filme-desktop.mp4]
"""
import pathlib
import sys

import cv2
import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parent.parent
W, H = 640, 360
MARGEM = 24  # ignora as bordas, onde o filme escalado não tem conteúdo


def carregar(clipe):
    start = cv2.imread(str(RAIZ / "assets" / "start-frame.png"))
    video = cv2.VideoCapture(str(clipe))
    ok, frame = video.read()
    video.release()
    assert ok
    return cv2.resize(start, (W, H), interpolation=cv2.INTER_AREA), cv2.resize(frame, (W, H), interpolation=cv2.INTER_AREA)


def warp(img, s, tx, ty):
    cx, cy = W / 2, H / 2
    m = np.float32([[s, 0, cx + tx - s * cx], [0, s, cy + ty - s * cy]])
    return cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def erro(a, b):
    a, b = a[MARGEM:-MARGEM, MARGEM:-MARGEM].astype(np.float64), b[MARGEM:-MARGEM, MARGEM:-MARGEM].astype(np.float64)
    return np.mean((a - b) ** 2)


def psnr(mse):
    return 10 * np.log10(255.0 ** 2 / mse)


def main(clipe):
    start, frame = carregar(clipe)
    borrar = lambda im: cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (0, 0), 2)
    gs, gf = borrar(start), borrar(frame)

    melhor = (erro(gs, gf), 1.0, 0.0, 0.0)
    passos = [(np.arange(0.95, 1.20, 0.01), np.arange(-40, 41, 2.0)), (0.01, 2.0), (0.002, 0.5), (0.0005, 0.125)]
    escalas, desloc = passos[0]
    for s in escalas:
        for tx in desloc:
            for ty in desloc:
                e = erro(gs, warp(gf, s, tx, ty))
                if e < melhor[0]:
                    melhor = (e, s, tx, ty)
    for ds, dt in passos[1:]:
        _, s0, tx0, ty0 = melhor
        for s in s0 + ds * np.arange(-4, 5):
            for tx in tx0 + dt * np.arange(-4, 5):
                for ty in ty0 + dt * np.arange(-4, 5):
                    e = erro(gs, warp(gf, s, tx, ty))
                    if e < melhor[0]:
                        melhor = (e, s, tx, ty)

    _, s, tx, ty = melhor
    antes, depois = erro(start, frame), erro(start, warp(frame, s, tx, ty))
    print(f"escala {s:.4f}  tx {tx / W * 100:+.3f}%  ty {ty / H * 100:+.3f}%")
    print(f"PSNR (cor, sem bordas) antes {psnr(antes):.2f} dB -> depois {psnr(depois):.2f} dB")
    saida = RAIZ / "comparacoes" / "alinhamento.png"
    cv2.imwrite(str(saida), np.vstack([np.hstack([start, frame]), np.hstack([warp(frame, s, tx, ty), cv2.addWeighted(start, 0.5, warp(frame, s, tx, ty), 0.5, 0)])]))
    print(saida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "assets" / "filme-desktop.mp4")
