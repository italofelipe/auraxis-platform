# J4 - Aba de Ferramentas de conveniencia

## Problema
Usuario precisa executar calculos financeiros/trabalhistas recorrentes fora da plataforma.

## Hipotese de valor
Ferramentas utilitarias aumentam recorrencia de uso e ampliam utilidade diaria.

## Escopo v1
- Ferramentas iniciais:
  - salario liquido
  - rescisao contratual (estimativa)
  - ferias
  - 13o salario
  - hora extra
  - FGTS (estimativa)
  - dividir conta (bar/restaurante)
- Tela unica com catalogo de calculadoras.
- Resultado com explicacao do calculo e disclaimer.

## Fora de escopo v1
- Consultoria juridica/tributaria.
- Simulacoes oficiais com validade legal.

## Contrato e arquitetura
- Dominio separado de calculadoras com estrategias por ferramenta.
- Entradas/saidas tipadas e testaveis.
- Possibilidade de executar parte client-side no futuro para UX.

## Regras de negocio
- Regras de calculo versionadas por data/base legal.
- Exibir versao da regra utilizada.

## Compliance e risco legal
- Disclaimers claros: "estimativa, nao substitui calculo oficial".
- Fonte de regra documentada por calculadora.

## Observabilidade
- metricas por ferramenta: usage_count, completion_rate, error_rate.

## Criterios de aceite
- Usuario executa cada calculadora v1 com resultado consistente.
- Sistema informa premissas, formula e versao da regra.
- Testes unitarios validam formulas principais.

## Riscos e mitigacao
- Risco: regra desatualizada.
  - Mitigacao: versionamento e rotina de revisao periodica.
- Risco: interpretacao juridica incorreta.
  - Mitigacao: escopo de estimativa + disclaimer + fonte da regra.

## Dependencias
- Definicao de backlog de calculadoras por prioridade real de uso.

## Estimativa
- Complexidade: media
- Urgencia: media
- Recomendacao: pode rodar paralelo apos J1, sem bloquear J2/J3.
