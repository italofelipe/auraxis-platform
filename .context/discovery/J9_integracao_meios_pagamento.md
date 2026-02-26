# J9 - Integracao de meios de pagamento (Brasil)

## Problema
Para monetizacao futura, a plataforma precisa de meio de pagamento simples, confiavel, com suporte a BRL, parcelamento e taxas competitivas.

## Hipotese de valor
Escolha correta de PSP reduz atrito de compra, custo de transacao e risco operacional.

## Escopo de discovery
- Mapear provedores do mais simples ao mais complexo para integracao no Brasil.
- Comparar:
  - suporte a BRL;
  - parcelamento (cartao, recorrencia, split se necessario);
  - taxas e custos fixos;
  - disponibilidade/SLA;
  - maturidade de SDK/docs;
  - antifraude e chargeback;
  - compliance (LGPD/PCI escopo da integracao).
- Definir recomendacao por fase:
  - fase 1 (go-live rapido);
  - fase 2 (otimizacao de taxa/retencao).

## Fora de escopo v1
- Integracao multiprovedor simultanea.
- Marketplace split avancado.

## Criterios de aceite
- Matriz comparativa com custo total estimado e trade-offs.
- Recomendacao tecnica com plano de implantacao por fases.
- Go/no-go documentado para primeiro provedor.
