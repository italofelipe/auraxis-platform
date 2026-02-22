# Release Governance

## Estratégia de ambientes
- DEV: deploy automático após merge (com smoke).
- PROD: pipeline preparado automaticamente após DEV, com aprovação manual.

## Gates de release
- Build e testes obrigatórios.
- Checagens de segurança obrigatórias.
- Contrato de API consistente (sem drift silencioso).

## Fluxo recomendado
1. Merge em branch principal.
2. Deploy automático em DEV.
3. Smoke DEV automático.
4. Pipeline de PROD pronto aguardando aprovação.
5. Aprovação manual para deploy PROD.
6. Smoke PROD e monitoramento inicial.

## Incidentes
- Toda falha de deploy deve gerar registro em backlog técnico.
- Documentar causa raiz, mitigação e ação preventiva.
