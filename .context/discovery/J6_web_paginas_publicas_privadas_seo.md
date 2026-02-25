# J6 - Web: paginas publicas/privadas e SEO institucional

## Problema
A web precisa operar com duas superficies claras desde o dia 0:
- paginas publicas de aquisicao (institucional e conteudo indexavel);
- area privada (exige autenticacao).

Sem essa separacao, ha risco de SEO fraco, roteamento confuso e falhas de seguranca em conteudo logado.

## Hipotese de valor
Separar arquitetura publica vs privada melhora descoberta organica, reduz friccao de onboarding e prepara funil para conversao em area logada.

## Escopo v1
- Definir mapa de rotas publicas minimas:
  - institucional com SEO tecnico completo
  - landing de ferramentas publicas
  - pagina base de newsletter (captura de lead simples)
- Definir mapa de rotas privadas minimas:
  - dashboard/logado
  - ferramentas com persistencia de simulacoes
- Definir guardrails de autenticacao por segmento de rota.
- Definir baseline SEO para area publica.

## Fora de escopo v1
- Blog completo com CMS robusto.
- Segmentacao SEO por cluster avancado.

## Dependencias
- Definicao de dominio final na AWS.
- Politica de session/auth da web.

## Criterios de aceite
- Mapa de rotas aprovado (publico x privado).
- Checklist SEO institucional v1 aprovado.
- Regras de protecao de rota documentadas e testaveis.
