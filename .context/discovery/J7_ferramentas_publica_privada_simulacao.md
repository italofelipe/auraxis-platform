# J7 - Ferramentas hibridas (publico + logado) com simulacao persistivel

## Problema
A area de ferramentas tera duas camadas:
- uma camada publica (uso sem login, foco aquisicao);
- uma camada logada (simulacao salva, historico e continuidade).

Sem discovery dedicado, ha risco de duplicidade de fluxo, regras inconsistentes e baixa conversao de anonimo para conta.

## Hipotese de valor
Um fluxo hibrido bem desenhado aumenta uso organico das ferramentas e cria ponte direta para ativacao no produto logado.

## Escopo v1
- Definir quais calculadoras entram na camada publica.
- Definir quais capacidades extras exigem login (salvar, comparar, acompanhar).
- Definir contrato de simulacao:
  - payload de entrada
  - resultado calculado
  - versao da regra
  - metadados de persistencia no logado
- Definir CTA de conversao publico -> login.

## Fora de escopo v1
- Personalizacao avancada por perfil comportamental.
- Automacoes multi-etapa de recomendacao.

## Dependencias
- J4 (catalogo de ferramentas).
- B12/J6 (calculadora "pedir aumento").

## Criterios de aceite
- Matriz publica x privada por ferramenta aprovada.
- Fluxo de persistencia da simulacao definido.
- Regras de conversao anonimo -> autenticado documentadas.
