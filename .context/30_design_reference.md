# Design Reference Spec — Auraxis Platform

Ultima atualizacao: 2026-02-26

## Objetivo

Padronizar como agentes devem consumir os assets visuais em `designs/` para implementar
layout com alta fidelidade visual, sem drift entre `web` e `app`.

Este documento e operacional e obrigatorio para qualquer tarefa de UI/layout frontend.

---

## Fonte visual canonica

1. `designs/1920w default.png` (1920x1200)
2. `designs/Background.svg` (1512x2457)

Regra de precedencia:
1. Estrutura visual (composicao e hierarquia) vem das imagens.
2. Tokens e constraints tecnicos vem de `product.md` e `.context/26_frontend_architecture.md`.
3. Em conflito, nao inventar novo layout: abrir task de alinhamento no `tasks.md` do repo alvo.

---

## Tokens visuais extraidos dos assets

### Superficies principais
- `surface.base`: `#272020`
- `surface.deep`: `#0c0909`
- `surface.card`: `#413a3a`
- `surface.card.active`: `#322a2a`

### Acentos de marca
- `brand.primary`: `#ffab1a`
- `brand.secondary`: `#ffbe4d`
- `brand.highlight`: `#ffd080`

### Texto de apoio
- `text.muted`: `#bcb3b3`

### Semantica de dashboard (imagem 1920w)
- `status.success`: `#059669`
- `status.success.soft`: `#4ade80`
- `status.danger`: `#ef4343`
- `status.danger.soft`: `#f87171`

Observacao: os tokens semanticos (`success`/`danger`) devem ser definidos no tema.
Nao usar valores literais em componentes.

---

## Blueprint de layout — Dashboard autenticado

Referencia: `designs/1920w default.png`.

### Estrutura de alto nivel
1. Sidebar fixa na esquerda (altura total da viewport).
2. Area principal a direita com header + conteudo.
3. Header com titulo da pagina, subtitulo de periodo e acoes primarias.
4. Linha de KPIs com 3 cards (`Receitas`, `Despesas`, `Saldo`).
5. Linha principal em duas colunas:
   - esquerda: grafico de receitas vs despesas;
   - direita: lista de transacoes.

### Regras de composicao
1. Sidebar:
   - bloco de logo no topo;
   - secao `MENU`;
   - item ativo com fundo destacado;
   - link de retorno no rodape.
2. Header:
   - titulo `Dashboard`;
   - subtitulo no formato `Mes de AAAA`;
   - botoes `+ Receita` e `+ Despesa` alinhados a direita.
3. Cards KPI:
   - icone em chip com opacidade baixa;
   - label pequena + valor de destaque;
   - valores positivos em `status.success`;
   - valores negativos em `status.danger`;
   - saldo em cor de acento (`brand.secondary`/`brand.highlight`).
4. Card de transacoes:
   - filtros no topo (`Todas`, `Receitas`, `Despesas`);
   - cada item com icone, titulo, metadata e valor alinhado a direita.
5. Spacing/radius:
   - spacing estrutural em multiplos de `8px`;
   - radius base entre `6` e `8` via token.

---

## Blueprint de layout — Publico/institucional

Referencia: `designs/Background.svg`.

### Estrutura visual principal
1. Fundo escuro em camadas com gradiente vertical:
   - `#272020` com opacidade crescente (0.6 -> 0.8 -> 1.0).
2. Acento em gradiente horizontal:
   - `#ffab1a -> #ffbe4d -> #ffd080`.
3. Glow/blur circular de destaque em baixa opacidade (`#ffbe4d` com 0.05 a 0.1).
4. CTA principal:
   - botao base `#ffbe4d`, `214x52`, `radius 6`.
5. Blocos de cards em secoes inferiores com superficie `#413a3a`.

---

## Protocolo obrigatorio para agentes (web/app)

Antes de codar UI:
1. Ler este arquivo + abrir os dois assets em `designs/`.
2. Validar se tokens necessarios existem no tema do repo alvo.
3. Criar/ajustar tokens semanticos antes de construir telas.

Durante implementacao:
1. Nao usar Tailwind.
2. Nao hardcodar cor/spacing/radius/font-size.
3. Usar componentes da UI library oficial da plataforma e extender por tema.

Antes de concluir o bloco:
1. Capturar screenshot local da tela implementada.
2. Comparar manualmente com o asset de referencia (hierarquia e proporcao).
3. Registrar no handoff o nivel de fidelidade e gaps conhecidos.

---

## Criterios minimos de aceite de layout

1. Ordem e hierarquia dos blocos iguais ao reference asset.
2. Tokens de tema aplicados em 100% dos valores visuais.
3. Tipografia oficial (`Playfair Display` / `Raleway`) aplicada.
4. Grid de 8px respeitado nos espacamentos estruturais.
5. Estados semanticos de valor financeiro (positivo/negativo/saldo) consistentes.
