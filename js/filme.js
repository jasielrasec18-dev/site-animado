/* Abertura: a rolagem da .trilha (420vh) controla o tempo do filme, nos dois sentidos.
   - 0–3%: a cena estática (título, relógio recortado, chamada) se dissolve no filme parado no 1º frame.
   - 3–100%: o tempo do vídeo segue a rolagem, suavizado a cada quadro, sem pedir um novo frame
     enquanto o anterior ainda carrega.
   Celular (navigator.maxTouchPoints > 1) recebe o arquivo com quadro-chave a cada 4 frames.
   Movimento reduzido: não ativa nada; os capítulos aparecem como seção estática, sem vídeo.
   Carregado sem defer no <head> para marcar html.filme antes da primeira pintura. */
(function () {
  if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.documentElement.classList.add("filme");

  var DISSOLVE = 0.03;   // fração da trilha usada na dissolução
  var SUAVE = 0.14;      // quanto o tempo exibido anda em direção ao alvo a cada quadro
  var ESPACO_FRAME = 1 / 24;

  function limitar(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function suavizar(v) { return v * v * (3 - 2 * v); }

  function iniciar() {
    var trilha = document.querySelector(".trilha");
    var palco = document.querySelector(".palco");
    var video = palco && palco.querySelector(".video-filme");
    if (!trilha || !video) return;

    var celular = navigator.maxTouchPoints > 1;
    video.poster = "assets/filme-poster.jpg";
    video.src = celular ? "assets/filme-mobile.mp4" : "assets/filme-desktop.mp4";
    video.load();

    var duracao = 241 / 24;
    video.addEventListener("loadedmetadata", function () {
      if (isFinite(video.duration) && video.duration > 0) duracao = video.duration;
    });

    // Um pedido de frame por vez: o próximo só sai depois do "seeked" do anterior
    var buscando = false;
    video.addEventListener("seeked", function () { buscando = false; });
    video.addEventListener("error", function () { buscando = false; });

    // iOS só decodifica depois de um gesto: no primeiro toque, toca e pausa para preparar o vídeo
    var preparo = "aguardando toque";
    addEventListener("touchstart", function () {
      preparo = "tocando";
      var pedido = video.play();
      if (pedido && pedido.then) {
        pedido.then(function () { video.pause(); preparo = "pronto"; })
              .catch(function () { video.load(); preparo = "recusado, recarregado"; });
      }
    }, { once: true, passive: true });

    var capitulos = Array.prototype.map.call(palco.querySelectorAll(".capitulo"), function (el) {
      return { el: el, de: parseFloat(el.dataset.de), ate: parseFloat(el.dataset.ate), menu: el.dataset.menu, opacidade: -1 };
    });
    var links = Array.prototype.slice.call(document.querySelectorAll(".menu a"));

    var alvo = 0, tempo = 0, ultimo = {};
    function escrever(nome, valor) {
      if (ultimo[nome] === valor) return;
      ultimo[nome] = valor;
      palco.style.setProperty(nome, valor);
    }

    function opacidadeCapitulo(c, p) {
      var borda = 0.03;
      var entra = limitar((p - c.de) / borda);
      var sai = c.ate >= 1 ? 1 : limitar((c.ate - p) / borda);
      return Math.min(entra, sai);
    }

    function marcarMenu(href) {
      links.forEach(function (a) {
        var ativo = a.getAttribute("href") === href;
        if (a.classList.contains("ativo") !== ativo) a.classList.toggle("ativo", ativo);
        if (ativo) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
      });
    }

    function quadro() {
      var r = trilha.getBoundingClientRect();
      var faixa = r.height - innerHeight;
      var p = faixa > 0 ? limitar(-r.top / faixa) : 0;
      var preso = r.top <= 0 && r.bottom >= innerHeight;

      var k = limitar(p / DISSOLVE);
      var f = limitar((p - DISSOLVE) / (1 - DISSOLVE));
      alvo = f * Math.max(0, duracao - ESPACO_FRAME);

      tempo += (alvo - tempo) * SUAVE;
      if (Math.abs(alvo - tempo) < 0.002) tempo = alvo;

      if (!buscando && video.readyState >= 1 && Math.abs(video.currentTime - tempo) > ESPACO_FRAME / 2) {
        buscando = true;
        video.currentTime = tempo;
      }

      escrever("--k", k.toFixed(3));
      escrever("--p", p.toFixed(4));
      escrever("--z", suavizar(limitar(tempo / duracao / 0.5)).toFixed(4));
      palco.classList.toggle("no-filme", k > 0.5);

      var ativo = null, maior = 0.5;
      capitulos.forEach(function (c) {
        var o = opacidadeCapitulo(c, p);
        if (o !== c.opacidade) {
          c.opacidade = o;
          c.el.style.opacity = o;
          c.el.style.transform = "translateY(" + ((1 - o) * 1.2).toFixed(2) + "rem)";
        }
        if (o >= maior) { maior = o; ativo = c.menu; }
      });
      if (preso) marcarMenu(ativo);

      requestAnimationFrame(quadro);
    }
    requestAnimationFrame(quadro);

    // Estado para os testes (tools/testar_filme.py)
    window.atelierFilme = function () {
      return { celular: celular, src: video.currentSrc, p: ultimo["--p"], k: ultimo["--k"], alvo: alvo, tempo: tempo,
               atual: video.currentTime, buscando: buscando, pronto: video.readyState, preparo: preparo,
               pausado: video.paused };
    };
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
