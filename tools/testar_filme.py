"""Testa a abertura com filme no Chrome headless, abrindo index.html por file://.

Posições 0, 2, 15, 50, 85, 100 e de volta a 50 e 0% da trilha, no desktop (1920x1080)
e no celular emulado (iPhone 14, toque com maxTouchPoints 5), mais o modo de movimento reduzido.
Saída: comparacoes/filme-teste/*.png e uma folha por dispositivo.
Uso: python tools/testar_filme.py
"""
import json
import pathlib
import time

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "comparacoes" / "filme-teste"
URL = (RAIZ / "index.html").as_uri()
POSICOES = [0, 2, 15, 50, 85, 100, 50, 0]


def tempo_esperado(pos, duracao):
    f = min(1, max(0, (pos / 100 - 0.03) / 0.97))
    return f * (duracao - 1 / 24)


def esperar_estavel(pagina, pos, limite=20):
    """Espera o quadro que já leu a nova posição e o vídeo parado no tempo esperado."""
    duracao = pagina.evaluate("document.querySelector('video.video-filme').duration")
    esperado = tempo_esperado(pos, duracao)
    fim = time.time() + limite
    while time.time() < fim:
        e = pagina.evaluate("atelierFilme()")
        if (abs(float(e["p"]) - pos / 100) < 0.002 and abs(e["alvo"] - esperado) < 0.01
                and e["pronto"] >= 2 and not e["buscando"] and abs(e["tempo"] - e["alvo"]) < 0.003
                and abs(e["atual"] - esperado) <= 1 / 48 + 1e-3):
            pagina.wait_for_timeout(250)  # deixa o frame buscado pintar
            e = pagina.evaluate("atelierFilme()")
            assert abs(e["atual"] - esperado) <= 1 / 48 + 1e-3, (pos, esperado, e)
            return e
        pagina.wait_for_timeout(50)
    raise TimeoutError(f"filme não estabilizou em {pos}% (esperado {esperado:.3f}s): {e}")


# Registra cada pedido de frame (currentTime = ...) e os que chegariam com outro ainda carregando
ESPIAO = """
(() => {
  const d = Object.getOwnPropertyDescriptor(HTMLMediaElement.prototype, 'currentTime');
  window.__pedidos = {total: 0, sobrepostos: 0};
  Object.defineProperty(HTMLMediaElement.prototype, 'currentTime', {
    get() { return d.get.call(this); },
    set(v) { window.__pedidos.total++; if (this.seeking) window.__pedidos.sobrepostos++; d.set.call(this, v); },
    configurable: true
  });
})();
"""

SUAVIZACAO = """
async () => {
  // Salta de 0% para 50% e lê o tempo exibido em cada quadro seguinte
  const t = document.querySelector('.trilha');
  scrollTo({top: Math.round(0.5 * (t.offsetHeight - innerHeight)), behavior: 'instant'});
  const amostras = [];
  for (let i = 0; i < 45; i++) {
    await new Promise(r => requestAnimationFrame(r));
    amostras.push(atelierFilme().tempo);
  }
  return {alvo: atelierFilme().alvo, amostras};
}
"""

ESTRESSE = """
async () => {
  // 120 posições aleatórias, uma por quadro, com a CPU estrangulada
  const t = document.querySelector('.trilha');
  const antes = {...window.__pedidos};
  for (let i = 0; i < 120; i++) {
    scrollTo({top: Math.round(Math.random() * (t.offsetHeight - innerHeight)), behavior: 'instant'});
    await new Promise(r => requestAnimationFrame(r));
  }
  return {pedidos: window.__pedidos.total - antes.total, sobrepostos: window.__pedidos.sobrepostos - antes.sobrepostos};
}
"""


def medir(pagina, cdp, nome):
    pagina.evaluate("scrollTo({top: 0, behavior: 'instant'})")
    esperar_estavel(pagina, 0)
    s = pagina.evaluate(SUAVIZACAO)
    a = s["amostras"]
    intermediarios = [x for x in a if 0.01 < x < s["alvo"] - 0.01]
    assert all(b >= x for x, b in zip(a, a[1:])), "tempo exibido voltou durante a suavização"
    assert len(intermediarios) >= 10, a
    chegou = next(i for i, x in enumerate(a) if abs(x - s["alvo"]) < 0.01)
    print(f"  suavização: 0 -> {s['alvo']:.2f}s em {chegou + 1} quadros, {len(intermediarios)} valores intermediários "
          f"({', '.join(f'{x:.2f}' for x in a[:6])} ...)")
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 6})
    e = pagina.evaluate(ESTRESSE)
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
    print(f"  estresse (CPU 6x, 120 saltos em 120 quadros): {e['pedidos']} pedidos de frame, {e['sobrepostos']} com outro carregando")
    assert e["sobrepostos"] == 0 and e["pedidos"] > 0, e


def rodar(navegador, nome, contexto_args, celular):
    contexto = navegador.new_context(**contexto_args)
    contexto.add_init_script(ESPIAO)
    pagina = contexto.new_page()
    cdp = contexto.new_cdp_session(pagina)
    erros = []
    pagina.on("pageerror", lambda ex: erros.append(str(ex)))
    pagina.on("console", lambda m: m.type == "error" and erros.append(m.text))
    if celular:
        cdp.send("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
    pagina.goto(URL, wait_until="load")
    pagina.evaluate("document.fonts.ready")
    if celular:
        antes = pagina.evaluate("atelierFilme().preparo")
        pagina.touchscreen.tap(20, 300)  # primeiro toque: prepara o vídeo (iOS)
        pagina.wait_for_function("atelierFilme().preparo !== 'tocando' && atelierFilme().preparo !== 'aguardando toque'")
        depois = pagina.evaluate("atelierFilme()")
        print(f"  primeiro toque: '{antes}' -> '{depois['preparo']}', vídeo pausado={depois['pausado']}, readyState={depois['pronto']}")
        assert depois["preparo"] == "pronto" and depois["pausado"], depois

    info = pagina.evaluate("({toque: navigator.maxTouchPoints, classe: document.documentElement.className,"
                           " faixa: document.querySelector('.trilha').offsetHeight - innerHeight,"
                           " vh: innerHeight})")
    print(nome, json.dumps(info))
    capturas = []
    for n, pos in enumerate(POSICOES):
        pagina.evaluate("p => scrollTo({top: Math.round(p / 100 * (document.querySelector('.trilha').offsetHeight - innerHeight)), behavior: 'instant'})", pos)
        estado = esperar_estavel(pagina, pos)
        ativo = pagina.evaluate("(document.querySelector('.menu a.ativo') || {}).textContent || '-'")
        palco = pagina.evaluate("""() => { const r = document.querySelector('.palco').getBoundingClientRect();
            const op = s => +getComputedStyle(document.querySelector(s)).opacity;
            return {topo: r.top, altura: r.height, titulo: op('.titulo'), relogio: op('.relogio'), chamada: op('.chamada'),
                    filme: op('.video-filme'), caps: [...document.querySelectorAll('.capitulo')].map(c => +c.style.opacity || 0)} }""")
        assert abs(palco["topo"]) < 0.5, f"palco não ficou preso: {palco}"
        caminho = SAIDA / f"{nome}-{n}-{pos:03d}.png"
        pagina.screenshot(path=str(caminho))
        print(f"  {pos:3d}%  p={estado['p']}  tempo={estado['tempo']:.3f}s  video={estado['atual']:.3f}s  palco.top={palco['topo']:.0f}  "
              f"cena(título/relógio/chamada)={palco['titulo']:.2f}/{palco['relogio']:.2f}/{palco['chamada']:.2f}  filme={palco['filme']:.2f}  "
              f"capítulos={palco['caps']}  menu={ativo}  src={estado['src'].rsplit('/', 1)[-1]}")
        capturas.append((caminho, f"{pos}%  t={estado['atual']:.2f}s  menu: {ativo}"))
    medir(pagina, cdp, nome)
    contexto.close()
    assert not erros, erros
    return capturas


def reduzido(navegador, nome, contexto_args):
    contexto = navegador.new_context(reduced_motion="reduce", **contexto_args)
    pagina = contexto.new_page()
    pagina.goto(URL, wait_until="load")
    pagina.evaluate("document.fonts.ready")
    estado = pagina.evaluate("({filme: document.documentElement.classList.contains('filme'),"
                             " src: document.querySelector('video.video-filme').currentSrc,"
                             " videoVisivel: getComputedStyle(document.querySelector('video.video-filme')).display,"
                             " trilha: document.querySelector('.trilha').offsetHeight})")
    print(nome, "movimento reduzido:", json.dumps(estado))
    assert not estado["filme"] and not estado["src"] and estado["videoVisivel"] == "none"
    pagina.evaluate("document.querySelector('.capitulos').scrollIntoView({behavior: 'instant'})")
    pagina.wait_for_timeout(300)
    caminho = SAIDA / f"{nome}-reduzido.png"
    pagina.screenshot(path=str(caminho))
    contexto.close()
    return caminho


def folha(capturas, destino, largura):
    imgs = [Image.open(c).convert("RGB") for c, _ in capturas]
    escala = largura / imgs[0].width
    w, h = largura, round(imgs[0].height * escala)
    colunas = 4
    linhas = (len(imgs) + colunas - 1) // colunas
    sheet = Image.new("RGB", (colunas * (w + 10) + 10, linhas * (h + 34) + 10), "#1b1b1b")
    d = ImageDraw.Draw(sheet)
    for i, (img, (_, rotulo)) in enumerate(zip(imgs, capturas)):
        x, y = 10 + (i % colunas) * (w + 10), 10 + (i // colunas) * (h + 34)
        d.text((x, y + 4), f"{i + 1}. {rotulo}", fill="#fff")
        sheet.paste(img.resize((w, h), Image.LANCZOS), (x, y + 24))
    sheet.save(destino)
    print(destino)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    desktop = {"viewport": {"width": 1920, "height": 1080}}
    with sync_playwright() as p:
        navegador = p.chromium.launch(channel="chrome", headless=True)
        celular = dict(p.devices["iPhone 14"])
        celular.pop("default_browser_type", None)
        d = rodar(navegador, "desktop", desktop, celular=False)
        c = rodar(navegador, "celular", celular, celular=True)
        rd = reduzido(navegador, "desktop", desktop)
        rc = reduzido(navegador, "celular", celular)
        navegador.close()
    folha(d, SAIDA / "folha-desktop.png", 640)
    folha(c, SAIDA / "folha-celular.png", 300)
    print(rd, rc)


if __name__ == "__main__":
    main()
