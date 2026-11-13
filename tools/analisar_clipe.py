"""Folha de 6 frames do clipe e comparação do 1º frame com assets/start-frame.png.

Uso: python tools/analisar_clipe.py caminho/do/clipe.mp4
"""
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "comparacoes"
START = RAIZ / "assets" / "start-frame.png"


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return float("inf") if mse == 0 else 10 * np.log10(255.0 ** 2 / mse)


def main(clipe):
    clipe = pathlib.Path(clipe)
    SAIDA.mkdir(exist_ok=True)
    video = cv2.VideoCapture(str(clipe))
    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    w, h = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"{clipe.name}: {w}x{h}, {fps:.2f} fps, {total} frames, {total / fps:.2f} s")

    indices = [round(i * (total - 1) / 5) for i in range(6)]
    frames = []
    for i in indices:
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, f = video.read()
        assert ok, f"falha ao ler frame {i}"
        frames.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    video.release()

    # Folha 3x2 com rótulo de tempo
    folha = Image.new("RGB", (w * 3 + 40, (h + 30) * 2 + 20), "#222")
    d = ImageDraw.Draw(folha)
    for n, (i, f) in enumerate(zip(indices, frames)):
        x, y = 10 + (n % 3) * (w + 10), 10 + (n // 3) * (h + 30)
        d.text((x, y), f"frame {i}  t={i / fps:.2f}s", fill="#fff")
        folha.paste(f, (x, y + 20))
    folha.save(SAIDA / f"{clipe.stem}-folha.png")

    # 1º frame x start frame, na resolução do clipe
    start = Image.open(START).convert("RGB").resize((w, h), Image.LANCZOS)
    primeiro = frames[0]
    valor = psnr(np.asarray(start), np.asarray(primeiro))
    diff = np.abs(np.asarray(start).astype(int) - np.asarray(primeiro).astype(int)).sum(2)
    diff_img = Image.fromarray(np.clip(diff * 3, 0, 255).astype(np.uint8)).convert("RGB")
    lado = Image.new("RGB", (w * 3 + 40, h + 40), "#222")
    d = ImageDraw.Draw(lado)
    for n, (rot, img) in enumerate([("START FRAME", start), ("1º FRAME DO CLIPE", primeiro), (f"DIFERENÇA x3 — PSNR {valor:.2f} dB", diff_img)]):
        d.text((10 + n * (w + 10), 8), rot, fill="#fff")
        lado.paste(img, (10 + n * (w + 10), 30))
    lado.save(SAIDA / f"{clipe.stem}-primeiro-vs-start.png")
    print(f"PSNR 1º frame x start frame: {valor:.2f} dB")
    print(SAIDA / f"{clipe.stem}-folha.png")
    print(SAIDA / f"{clipe.stem}-primeiro-vs-start.png")


if __name__ == "__main__":
    main(sys.argv[1])
