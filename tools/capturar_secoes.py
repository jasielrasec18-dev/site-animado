"""Captura cada seção de index.html em desktop (1920x1080) e no celular emulado (iPhone 14).

Uso: python tools/capturar_secoes.py rotulo
Saída: comparacoes/<rotulo>-<secao>-{desktop,celular}.png e uma folha por aparelho.
"""
import pathlib
import sys

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "comparacoes"
URL = (RAIZ / "index.html").as_uri()
# (nome, seletor): seções e, nas mais altas, o trecho de baixo
SECOES = [("inicio", "#inicio"), ("calibre", "#calibre"), ("calibre-specs", ".specs"),
          ("angulos", "#angulos"), ("angulos-legendas", ".galeria figcaption"),
          ("oficio", "#oficio"), ("oficio-etapas", ".etapas"), ("contato", "#contato"),
          ("rodape", "footer.rodape")]


def capturar(pagina, rotulo, aparelho):
    pagina.goto(URL, wait_until="networkidle")
    pagina.evaluate("document.fonts.ready")
    arquivos = []
    for secao, seletor in SECOES:
        # rola até o topo da seção, descontando o menu fixo
        pagina.evaluate(
            """s => { const el = document.querySelector(s);
                      const r = el.getBoundingClientRect();
                      const y = s.startsWith('#') || s.startsWith('footer')
                        ? r.top + scrollY - (s === '#inicio' ? 0 : 72)
                        : r.bottom + scrollY - innerHeight + 48;
                      document.documentElement.style.scrollBehavior = 'auto';
                      scrollTo(0, Math.min(y, document.documentElement.scrollHeight - innerHeight)); }""",
            seletor,
        )
        pagina.wait_for_timeout(1400)
        destino = SAIDA / f"{rotulo}-{secao}-{aparelho}.png"
        pagina.screenshot(path=str(destino))
        arquivos.append(destino)
    ativos = pagina.evaluate("[...document.querySelectorAll('.menu a.ativo')].map(a => a.textContent)")
    print(aparelho, "item ativo no fim:", ativos)
    return arquivos


def folha(arquivos, destino, largura):
    imgs = [Image.open(a).convert("RGB") for a in arquivos]
    esc = largura / imgs[0].width
    imgs = [i.resize((largura, round(i.height * esc))) for i in imgs]
    cols = 3
    linhas = -(-len(imgs) // cols)
    w, h = imgs[0].size
    f = Image.new("RGB", (cols * w + (cols + 1) * 16, linhas * (h + 40) + 16), "#222")
    d = ImageDraw.Draw(f)
    for n, (img, arq) in enumerate(zip(imgs, arquivos)):
        x = 16 + (n % cols) * (w + 16)
        y = 16 + (n // cols) * (h + 40)
        d.text((x, y), arq.stem, fill="#fff")
        f.paste(img, (x, y + 20))
    f.save(destino)
    print(destino)


def main(rotulo):
    SAIDA.mkdir(exist_ok=True)
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome")
        pagina = navegador.new_page(viewport={"width": 1920, "height": 1080})
        desk = capturar(pagina, rotulo, "desktop")
        contexto = navegador.new_context(**p.devices["iPhone 14"])
        cel = capturar(contexto.new_page(), rotulo, "celular")
        navegador.close()
    folha(desk, SAIDA / f"{rotulo}-folha-desktop.png", 960)
    folha(cel, SAIDA / f"{rotulo}-folha-celular.png", 390)


if __name__ == "__main__":
    main(sys.argv[1])
