# Auraxis Platform - Overview

## Objetivo
Centralizar contexto de produto, engenharia e execução para trabalho humano + IA (Agentic Workflows).

## Repositórios
- repos/auraxis-api (backend atual)
- repos/auraxis-web (web atual)
- repos/auraxis-app (app mobile atual)

## Diretriz de hospedagem web
- Web em AWS desde o dia 0.
- Dominio oficial web: `auraxis.com`.
- Nao usar Vercel ou GitHub Pages para ambiente oficial.
- Segmentar experiencia em:
  - paginas publicas (institucional + SEO + superficies de aquisicao)
  - paginas privadas (rotas autenticadas)

## Fonte de verdade
- Status global e handoff da plataforma: `.context/01_status_atual.md` e `.context/05_handoff.md`
- Status e andamento por produto: `tasks.md` de cada repositório em `repos/`
- Produto e visao (canonico): `product.md` na raiz da plataforma
- Referencia visual de layout (frontend): `designs/` + `.context/30_design_reference.md`
- `product.md` em `repos/*` sao briefs operacionais derivados
- Diretrizes de execução: steering.md

## Regra operacional
Toda decisão relevante deve gerar atualização em .context + tasks.md.
