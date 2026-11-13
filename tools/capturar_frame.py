"""Captura index.html#frame (só fundo + relógio) em 1920x1080 com o Chrome headless.

Uso: python tools/capturar_frame.py  ->  assets/start-frame.png
"""
import pathlib

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
URL = (RAIZ / "index.html").as_uri() + "#frame"
SAIDA = RAIZ / "assets" / "start-frame.png"


def main():
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome", headless=True)
        pagina = navegador.new_page(viewport={"width": 1920, "height": 1080})
        pagina.goto(URL, wait_until="networkidle")
        pagina.evaluate("document.fonts.ready")
        assert pagina.evaluate("document.documentElement.classList.contains('modo-frame')")
        pagina.screenshot(path=str(SAIDA))
        navegador.close()
    print(SAIDA)


if __name__ == "__main__":
    main()
