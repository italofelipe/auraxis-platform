# J1 - Exportacao de extrato financeiro (CSV/XLSX)

## Problema
Usuario precisa extrair dados financeiros para analise externa, contabilidade e acompanhamento historico.

## Hipotese de valor
Exportacao padronizada reduz atrito operacional e aumenta percepcao de controle financeiro.

## Escopo v1
- Exportar receitas, despesas ou ambos.
- Presets: 15, 30, 90, 180 dias.
- Opcoes: desde o inicio, range customizado (`start_date`, `end_date`).
- Formatos: CSV e XLSX.
- Colunas minimas:
  - id
  - type (income/expense)
  - title
  - amount
  - due_date
  - status
  - created_at
  - source (`manual`/`imported`)
- Timezone oficial no arquivo (cabecalho/metadado).

## Fora de escopo v1
- Agendamento automatico de exportacao.
- Templates customizados por usuario.
- Criptografia de arquivo por senha.

## Contrato e arquitetura
- REST: endpoint dedicado de exportacao com parametros de periodo/formato.
- GraphQL: mutation/query de export com paridade funcional.
- Geracao de arquivo em camada de aplicacao (nao no controller).
- Versionar contrato de exportacao (`export_schema_version`).

## Regras de negocio
- Limitar volume por export para proteger performance.
- Validar periodo maximo por request.
- Normalizar datas no timezone oficial da conta/tenant.

## Seguranca e compliance
- Autenticacao obrigatoria.
- Autorizar somente dados do proprio usuario.
- Audit log para evento de exportacao.

## Observabilidade
- metricas: total_export_requests, export_success, export_failure, export_latency.
- log estruturado com request_id e periodo solicitado.

## Criterios de aceite
- Usuario exporta com sucesso em CSV e XLSX para qualquer preset.
- Range customizado valida datas e retorna erro publico consistente.
- Conteudo exportado bate com dados do periodo na API.
- Testes de contrato REST/GraphQL cobrem caso feliz e erros.

## Riscos e mitigacao
- Risco: inconsistencia de timezone.
  - Mitigacao: definir timezone canonico e testes com borda de data.
- Risco: arquivo gigante degradando API.
  - Mitigacao: limite por export + pagina interna + async futuro.

## Dependencias
- Definicao final de colunas com produto.
- Definicao de limites operacionais.

## Estimativa
- Complexidade: media
- Urgencia: alta
- Recomendacao: iniciar implementacao primeiro no proximo bloco.
