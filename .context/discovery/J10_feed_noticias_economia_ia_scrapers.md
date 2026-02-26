# J10 - Feed de noticias de economia com IA/Scrapers

## Problema
Nao existe hoje uma superficie de noticias economicas curadas para contextualizar decisoes financeiras do usuario.

## Hipotese de valor
Feed curado com sumarizacao por IA pode aumentar recorrencia e engajamento, desde que haja governanca de fonte e qualidade.

## Escopo de discovery
- Definir fontes permitidas e politicas de coleta (RSS/APIs/public scraping legalmente permitido).
- Definir pipeline:
  - ingestao;
  - deduplicacao;
  - classificacao por tema;
  - sumarizacao assistida por IA;
  - ranking/priorizacao.
- Definir guardrails:
  - citacao de fonte;
  - deteccao de baixa confiabilidade;
  - fallback quando IA falhar.
- Definir custo operacional (coleta + inferencia) e limites.

## Fora de escopo v1
- Recomendacao hiperpersonalizada por portfolio.
- Cobertura em tempo real tick-by-tick.

## Criterios de aceite
- Arquitetura de ingestao e curadoria definida.
- Politica de fontes e compliance documentada.
- Prototipo de feed v1 com risco e custo estimados.
