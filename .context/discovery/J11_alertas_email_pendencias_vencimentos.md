# J11 - Alertas por email de pendencias e contas a vencer

## Problema
Usuarios podem perder vencimentos por falta de notificacao proativa fora do app.

## Hipotese de valor
Alertas por email aumentam utilidade pratica e reduzem risco de esquecimento de contas/prazos.

## Escopo de discovery
- Definir eventos de alerta v1:
  - conta vencendo;
  - conta vencida;
  - pendencias de cadastro/fluxo.
- Definir politicas:
  - janela de envio (ex.: D-3, D-1, D+1);
  - anti-spam/frequencia maxima;
  - opt-in/opt-out por tipo de alerta.
- Definir stack de envio low-cost/free e observabilidade minima.
- Definir contrato tecnico:
  - scheduler;
  - template engine;
  - trilha de entrega/falha.

## Fora de escopo v1
- Canais adicionais (SMS/WhatsApp/push).
- Orquestracao multicanal com score de engajamento.

## Criterios de aceite
- Matriz de alertas v1 aprovada (evento, timing, destinatario, template).
- Arquitetura de envio e monitoramento definida.
- Risco de spam/compliance documentado com mitigacoes.
