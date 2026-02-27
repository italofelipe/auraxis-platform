# Product - Auraxis Platform (Fonte Unica)

Ultima atualizacao: 2026-02-26

## Objetivo deste documento
Este arquivo e a fonte unica de verdade para visao de produto, posicionamento, escopo, prioridades e direcao cross-repo da Auraxis.

Status de execucao continua sendo rastreado em:
- `.context/01_status_atual.md` (estado global)
- `.context/02_backlog_next.md` (proximas prioridades)
- `tasks.md` de cada repositorio (`api`, `web`, `app`)

## Contexto de produto
Auraxis e uma plataforma de gestao financeira pessoal focada em transformar dados financeiros em direcao pratica.

Objetivo central:
1. Dar visibilidade clara do presente financeiro.
2. Permitir simulacao de cenarios futuros (metas, carteira, ferramentas).
3. Evoluir para assistencia inteligente com guardrails de seguranca e explicabilidade.

## Problemas que resolvemos
1. Falta de clareza para transformar movimentacoes em plano financeiro acionavel.
2. Dificuldade de simular impacto de aportes, inflacao e metas ao longo do tempo.
3. Baixa capacidade de consolidar saude financeira com explicacao simples.

## Proposta de valor
1. Base financeira consolidada e confiavel.
2. Ferramentas de simulacao orientadas a decisao.
3. Fluxo evolutivo de recomendacoes com modo advisory-only.

## Superficie de produto por canal

### Backend (`repos/auraxis-api`)
1. Contratos de autenticacao, transacoes, carteira, metas e ferramentas.
2. Base de dominio para suportar web/app de forma consistente.
3. Evolucao com compatibilidade contratual e quality/security gates.

### Web (`repos/auraxis-web`)
1. Dominio oficial: `auraxis.com`.
2. Hospedagem oficial em AWS (sem Vercel/GitHub Pages para producao).
3. Superficie publica:
- institucional com SEO
- area publica de ferramentas (escopo controlado)
- newsletter (em discovery)
4. Superficie privada:
- dashboard
- carteira
- ferramentas com simulacoes persistiveis

### App (`repos/auraxis-app`)
1. Aplicativo mobile para fluxo financeiro diario.
2. Escopo MVP:
- autenticacao
- dashboard
- carteira
- ferramentas
3. Publicacao em stores permanece dependente de janela de execucao definida no backlog global.

## Diretrizes de UX/UI
1. Paleta oficial: `#262121`, `#ffbe4d`, `#413939`, `#0b0909`, `#ffd180`, `#ffab1a`.
2. Tipografia oficial: `Playfair Display` (headings) + `Raleway` (body).
3. Grid base: 8px.
4. Tailwind proibido em web e app.
5. UI library-first:
- web: Chakra (se houver compatibilidade estavel em Vue) ou alternativa equivalente de mercado aprovada.
- app: React Native Paper.
6. Token-first styling:
- proibido valor visual literal solto (cor, spacing, radius, shadow, font-size, line-height).
- sempre usar tokens semanticos do tema.
7. Referencias visuais canonicas para layout:
- `designs/1920w default.png` (dashboard autenticado, referencia desktop).
- `designs/Background.svg` (base visual publico/institucional).
- detalhamento operacional em `.context/30_design_reference.md` (obrigatorio para tarefas de UI).

## Priorizacao atual (alto nivel)
1. Estabilizacao de fundacoes (governanca, qualidade, seguranca, CI parity).
2. Fechamento do bloco funcional atual do backend.
3. Evolucao de features de produto por ciclos sincronizados entre `api`, `web`, `app`.
4. Publicacao de lojas/deploy externos conforme marco definido no backlog global.

## Discovery ativo
Itens em refinamento continuo:
1. J6 - paginas publicas/privadas + SEO
2. J7 - ferramentas hibridas (publico/logado) com persistencia
3. J8 - newsletter e growth loop
4. J9 - meios de pagamento (BRL, parcelamento, taxas)
5. J10 - feed de noticias de economia com IA/scrapers
6. J11 - alertas por email de pendencias e vencimentos

## Politica anti-desync de documentacao de produto
1. Este arquivo (`/product.md`) e a referencia canonica de produto.
2. `product.md` dos repositorios de produto devem ser tratados como briefs operacionais derivados.
3. Qualquer decisao de produto deve atualizar primeiro este arquivo.
4. Se houver divergencia entre documentos, prevalece este arquivo central.

## Relacao com os demais documentos
1. `product.md` (este): estrategia e direcao de produto.
2. `.context/01_status_atual.md`: estado atual consolidado da execucao.
3. `.context/02_backlog_next.md`: ordem de proximas prioridades.
4. `tasks.md` por repo: backlog executavel e rastreabilidade tecnica.
