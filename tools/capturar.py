"""Captura index.html em 1920x1080 e no celular, e monta a comparação lado a lado.

Uso: python tools/capturar.py rotulo
"""
import pathlib
import sys

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "comparacoes"
URL = (RAIZ / "index.html").as_uri()


def main(rotulo):
    SAIDA.mkdir(exist_ok=True)
    desktop = SAIDA / f"{rotulo}-desktop.png"
    celular = SAIDA / f"{rotulo}-celular.png"
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome")
        pagina = navegador.new_page(viewport={"width": 1920, "height": 1080})
        pagina.goto(URL, wait_until="networkidle")
        pagina.evaluate("document.fonts.ready")
        pagina.screenshot(path=str(desktop))

        contexto = navegador.new_context(**p.devices["iPhone 14"])
        pagina = contexto.new_page()
        pagina.goto(URL, wait_until="networkidle")
        pagina.evaluate("document.fonts.ready")
        pagina.screenshot(path=str(celular))
        navegador.close()

    alvo = Image.open(RAIZ / "reference" / "relogio-alvo.png").convert("RGB").resize((1920, 1080), Image.LANCZOS)
    pagina_img = Image.open(desktop).convert("RGB")
    lado_a_lado = Image.new("RGB", (1920 * 2 + 20, 1080 + 60), "#222")
    lado_a_lado.paste(alvo, (0, 60))
    lado_a_lado.paste(pagina_img, (1940, 60))
    d = ImageDraw.Draw(lado_a_lado)
    d.text((20, 18), "ALVO (reference/relogio-alvo.png)", fill="#fff")
    d.text((1960, 18), f"PÁGINA (index.html) — {rotulo}", fill="#fff")
    lado_a_lado.save(SAIDA / f"{rotulo}-lado-a-lado.png")
    print(desktop, celular, SAIDA / f"{rotulo}-lado-a-lado.png")


if __name__ == "__main__":
    main(sys.argv[1])
