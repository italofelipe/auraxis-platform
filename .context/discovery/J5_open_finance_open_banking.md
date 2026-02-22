# J5 - Open Finance / Open Banking

## Status
Blocked (fase posterior)

## Problema
Importacao por arquivo nao cobre sincronizacao continua de contas e movimentacoes.

## Hipotese de valor
Integracao direta com instituicoes financeiras reduz friccao de entrada e aumenta fidelizacao.

## Escopo de discovery
- Avaliar requisitos regulatorios e compliance.
- Avaliar provedores agregadores e custos.
- Avaliar arquitetura de consentimento, renovacao e revogacao.
- Definir estrategia de seguranca para dados financeiros sensiveis.

## Fora de escopo atual
- Implementacao tecnica de conectores reais.
- Go-live de integracao bancaria.

## Gates para desbloqueio
- J1 e J2 consolidados em producao.
- Politica de privacidade e governanca de dados revisada.
- Modelo de custo e retorno aprovado.
- Avaliacao juridica/compliance favoravel.

## Riscos principais
- Complexidade regulatoria elevada.
- Custo operacional e dependencia de terceiro.
- Risco de seguranca e reputacao em incidente.

## Resultado esperado do discovery
- Documento de viabilidade (`go/no-go`) com:
  - requisitos
  - arquitetura alvo
  - estimativa de custo
  - riscos e mitigacao
  - plano faseado de rollout
