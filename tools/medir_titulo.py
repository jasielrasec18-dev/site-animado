"""Renderiza só o título (sem fundo e sem relógio) e mede a tinta em 1920x1080."""
import pathlib
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    nav = p.chromium.launch(channel="chrome")
    pg = nav.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto((RAIZ / "index.html").as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.add_style_tag(content=".atmosfera,.relogio,.topo,.chamada{visibility:hidden}.hero{background:#000}")
    pg.screenshot(path=str(RAIZ / "comparacoes" / "_titulo.png"))
    nav.close()
a = np.asarray(Image.open(RAIZ / "comparacoes" / "_titulo.png").convert("L")).astype(int)
ys, xs = np.where(a > 40)
print("pagina titulo x", xs.min(), xs.max(), "y", ys.min(), ys.max())
print("alvo   titulo x", round(135 * 1920 / 1672), round(1521 * 1920 / 1672), "y", round(124 * 1080 / 941), round(435 * 1080 / 941))
