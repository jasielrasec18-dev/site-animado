# Estudo da imagem alvo — `reference/relogio-alvo.png`

Imagem: 1672×941 (16:9). Medidas em px da imagem e em % / vw para o CSS
(1 vw = 16,72 px nessa largura).

## Camadas (de trás para frente)

1. **Fundo**: preto quente (#0a0a08 a #130f0c) com brilho âmbar/cobre vindo do
   canto superior esquerdo (#b27846 no pico, #492d1a perto do canto), névoa
   difusa e rochas escuras e texturizadas na base e à direita (#0a0707).
2. **Palavra "TEMPO"**: atrás do relógio. O relógio cobre parte do "M" e do "P".
3. **Relógio**: na frente da palavra, apoiado nas rochas.
4. **Interface**: navegação, parágrafo e botão, por cima de tudo.

Consequência para a reconstrução: o relógio precisa ser um recorte PNG com
transparência sobre o texto, e o fundo (rochas + luz + névoa) uma placa
separada, sem texto e sem relógio. As duas imagens serão geradas pela Codex CLI
na etapa 3.

## Navegação (faixa superior, centro vertical ≈ y 43 = 4,6%)

| Elemento | Posição | Estilo |
|---|---|---|
| Logo "ATELIER" | x 71–204 (margem esq. 4,2%) | serifa, caixa alta, entreletra bem aberta (~0,35em), altura das maiúsculas ~14px → fonte ~1,2vw, cor #fcedd4 |
| 4 links: Coleção · História · Ofício · Contato | x 634–1042, centralizados (centro 838 ≈ 50%) | serifa, caixa normal, ~1,05vw, espaço ~3,3vw entre eles, cor #f4e9d3 |
| Ícone de busca (lupa) | x 1583–1607 (margem dir. ~3,9%), 24px | traço fino, mesma cor clara |

Fundo da navegação: transparente, sem borda.

## "TEMPO"

- Faixa vertical: topo y 124 (13%) até a base y 435 (46%). Altura das maiúsculas ~311px (33% da altura).
- Faixa horizontal: x ~135 até 1521 (de 8% a 91%), praticamente centralizada.
- Fonte: serifa de alto contraste estilo Didone (hastes grossas, serifas finas e retas). Candidatas: Bodoni Moda, Playfair Display, Cormorant. Tamanho ~26–27vw, entreletra levemente apertada.
- Preenchimento: dourado/cobre metálico com textura martelada/escovada. Gradiente vertical, mais claro no topo (#edbb86) e mais escuro na base (#af6e38). As letras da direita ficam mais apagadas (O: #b98962 → #6f4a32), como se a luz viesse da esquerda.
- CSS provável: `background-clip: text` com gradiente + textura de ruído; brilho mais forte à esquerda.

## Relógio

- Caixa aproximada: x 680–1225, y 185–850 (de 41% a 73% na horizontal, de 20% a 90% na vertical).
- Centro do mostrador ≈ (905, 470). Diâmetro do mostrador ~380px (~23vw).
- Inclinado ~10–15°, com a pulseira subindo para trás à direita e descendo para a frente embaixo.
- Aço escovado com acentos dourados/rose (aro e coroa), mostrador preto sunburst (#1b1714), índices em bastão e ponteiros dourados (#e5d8c4 no realce).
- Coroa às 3h, à direita (x ~1155, y ~550).

## Bloco inferior esquerdo

| Elemento | Posição | Estilo |
|---|---|---|
| Parágrafo (3 linhas) | x 70, y 634–722; largura ~390px (~23vw) | serifa de texto, ~1,3vw, entrelinha ~1,5, cor #f9ecd8 |
| Botão "EXPLORAR COLEÇÃO →" | x 69–402, y 758–815 (333×57px; ~20vw × 3,4vw) | preenchimento cobre com gradiente da esquerda (#bc7e44) para a direita (#704826), cantos retos, texto escuro (~#1a120a) em caixa alta, ~0,95vw, entreletra ~0,2em, seta fina à direita |

Texto do parágrafo: "Precisão mecânica e design atemporal para quem valoriza o essencial e
enxerga o tempo de outra forma."

## Paleta

| Papel | Cor |
|---|---|
| Fundo base | #0a0a08 |
| Fundo quente | #130d07 / #1a120a |
| Brilho cobre | #b27846 |
| Ouro claro (realce) | #edbb86 |
| Cobre médio | #bc7e44 |
| Cobre escuro | #704826 |
| Texto creme | #f6ead6 |

## Grade e margens

- Margem lateral: ~70px (4,2vw) à esquerda e ~65px à direita.
- Nada encosta nas bordas. O conteúdo de texto fica todo na coluna esquerda,
  abaixo da metade da tela, e o relógio domina o centro-direita.

## Observações

- Já existem `assets/relogio-desktop.mp4` e `assets/relogio-mobile.mp4`
  (19/10, de uma tentativa anterior), além de uma pasta `backup/` vazia. Os
  backups do `index.html` vão em `backups/`, como combinado.
