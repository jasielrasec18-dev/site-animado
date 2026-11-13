/* Menu fixo: fundo escuro depois da abertura e item ativo seguindo a seção visível.
   Entrada suave das seções (desligada em prefers-reduced-motion, ver style.css). */
(function () {
  var topo = document.querySelector(".topo");
  var hero = document.querySelector(".hero");
  var trilha = document.querySelector(".trilha"); // trilho do filme (js/filme.js), se existir
  var links = Array.prototype.slice.call(document.querySelectorAll(".menu a"));
  var raiz = document.documentElement;
  // Com html.filme, a abertura é o trilho inteiro (o hero fica preso na tela); sem ele, só o hero
  function temFilme() { return !!trilha && raiz.classList.contains("filme"); }

  // 1. Fundo escuro quando a abertura já ocupa menos de 65% da tela
  //    (antes disso o botão do hero ainda pode passar por baixo do menu transparente)
  var visivel = new Map();
  function atualizarTopo() {
    var aberto = visivel.get(temFilme() ? trilha : hero);
    topo.classList.toggle("solido", !aberto);
  }
  var observaAbertura = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) { visivel.set(e.target, e.isIntersecting); });
    atualizarTopo();
  }, { rootMargin: "-65% 0px 0px 0px" });
  observaAbertura.observe(hero);
  if (trilha) observaAbertura.observe(trilha);

  // 2. Item ativo: a seção que cruza a faixa central da tela
  var secoes = links.map(function (a) { return document.querySelector(a.getAttribute("href")); });
  function marcar(id) {
    links.forEach(function (a) {
      var ativo = a.getAttribute("href") === "#" + id;
      a.classList.toggle("ativo", ativo);
      if (ativo) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
    });
  }
  var observaSecao = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) { if (e.isIntersecting) marcar(e.target.id); });
  }, { rootMargin: "-45% 0px -50% 0px" });
  secoes.forEach(function (s) { if (s) observaSecao.observe(s); });
  // Durante o filme, quem marca o item ativo é o filme.js
  new IntersectionObserver(function (entradas) {
    if (entradas[0].isIntersecting && !temFilme()) marcar("inicio");
  }, { rootMargin: "-45% 0px -50% 0px" }).observe(hero);

  // 3. Entrada suave
  var revelar = document.querySelectorAll(".revelar");
  var observaEntrada = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add("visivel");
      observaEntrada.unobserve(e.target);
    });
  }, { rootMargin: "0px 0px -12% 0px" });
  revelar.forEach(function (el) { observaEntrada.observe(el); });
})();
