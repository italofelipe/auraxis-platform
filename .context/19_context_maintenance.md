# Context Maintenance

## Objetivo
Evitar drift de contexto entre repositórios e agentes.

## Fonte de verdade
- Contexto global: `auraxis-platform/.context`
- Execução por repo: `tasks.md` e `steering.md` locais

## Regra de atualização mínima
Atualizar `.context` quando houver:
- mudança de prioridade
- decisão de arquitetura
- alteração em políticas de qualidade/segurança
- incidente com impacto de processo

## Cadência de revisão
- semanal: revisar backlog global e riscos
- quinzenal: revisar políticas e templates
- mensal: limpeza de decisões obsoletas

## Qualidade do contexto
Evitar:
- duplicidade de informações conflitantes
- instruções ambíguas
- status sem data/rastreabilidade

## Checklist de consistência
- [ ] índice aponta para arquivos atuais
- [ ] status reflete realidade dos repos
- [ ] backlog global alinhado com backlog local
- [ ] handoff atualizado após bloco concluído
