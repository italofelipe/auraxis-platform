# X3 - Migração gradual Flask -> FastAPI (com coexistência)

## Resumo executivo
A migração é viável, mas não deve começar por reescrita ampla. O caminho seguro é coexistência faseada com redução prévia de acoplamentos a Flask.

## Estado atual observado (base técnica)
- App principal em Flask WSGI (`create_app`, blueprints, middleware `before_request`/`after_request`).
- Runtime de produção com `gunicorn` executando `run:app`.
- Autenticação e revogação acopladas a `flask-jwt-extended`.
- OpenAPI gerado por `flask-apispec`.
- GraphQL exposto em endpoint Flask (`/graphql`).
- Boa evolução de arquitetura por domínio/adapters finos já existe (X2 concluído), mas ainda há pontos com `request/current_app/g` fora da borda ideal.

## Débitos técnicos que bloqueiam migração direta
1. Acoplamento de runtime:
- Uso extensivo de `flask` globals (`request`, `g`, `current_app`) em middleware/controladores e alguns serviços utilitários.

2. Acoplamento de autenticação:
- Validação de token/revogação dependente do ciclo de callbacks do Flask-JWT-Extended.

3. Acoplamento de documentação:
- Contratos REST vinculados ao pipeline Flask-apispec.

4. Acoplamento de observabilidade:
- Métricas e logs dependentes de hooks Flask (`before_request`, `after_request`).

## Estratégia recomendada (coexistência sem downtime)
### Fase 0 - Pré-requisitos (obrigatória)
- Extrair camada de auth framework-agnostic (parse/verify token + policy + jti check).
- Extrair request context adapter (request_id, client_ip, headers) para interface comum.
- Isolar serialização de erro/contrato v1-v2 em pacote reutilizável.

### Fase 1 - Coexistência por borda
- Manter Flask como runtime principal de legado.
- Introduzir FastAPI para novos endpoints via path prefix (`/api/v-next/*`) com roteamento no reverse proxy.
- Não migrar GraphQL nesta fase.

### Fase 2 - Migração por bounded context
- Migrar contextos REST com maior isolamento e menor risco primeiro.
- Validar paridade funcional com testes de contrato e smoke por contexto.
- Preservar o mesmo esquema de banco e políticas de auth.

### Fase 3 - Consolidação
- Migrar restante dos endpoints REST.
- Decidir estratégia para GraphQL:
  - manter endpoint atual no Flask temporariamente, ou
  - migrar para stack ASGI compatível em etapa dedicada.

### Fase 4 - Deprecação
- Congelar Flask para manutenção corretiva.
- Marcar janela de deprecação e retirar endpoints legados gradualmente.

## Estratégias de coexistência (trade-off)
### Opção A (recomendada): dois serviços atrás do mesmo proxy
- Flask (legado) + FastAPI (novo), roteamento por prefixo.
- Prós: menor risco operacional, rollback simples por rota.
- Contras: mais complexidade temporária de deploy/infra.

### Opção B: FastAPI montando Flask via WSGI middleware
- Prós: stack unificada em um processo.
- Contras: fronteiras menos claras, risco de comportamento inesperado em middlewares.

## Riscos principais
- Regressão transversal em autenticação/autorização.
- Divergência de contrato entre frameworks.
- Aumento temporário de custo operacional (dupla stack).

## Mitigações
- Contract tests obrigatórios por endpoint migrado.
- Checklist de segurança por rota (authz, rate limit, sanitização).
- Feature flags e canary por prefixo.
- Rollback por roteamento no proxy.

## Critérios de saída do X3 (análise)
- Estratégia de coexistência escolhida e ADR aprovada.
- Plano de fases com critérios de entrada/saída definidos.
- Lista de pré-requisitos de desacoplamento priorizada no backlog.

## Recomendação final
Aprovar migração via coexistência (Opção A), iniciando apenas após concluir os pré-requisitos de desacoplamento de auth/contexto/erros.
