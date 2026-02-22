# J2 - Importacao de relatorios bancarios

## Problema
Entrada manual de historico financeiro e lenta e sujeita a erro.

## Hipotese de valor
Importacao acelera onboarding de dados reais e melhora aderencia do usuario ao produto.

## Escopo v1
- Upload de arquivo bancario (inicialmente CSV; OFX como fase 1.1).
- Pipeline:
  1. upload
  2. parser
  3. normalizacao
  4. preview
  5. confirmacao de importacao
- Persistir origem do lancamento (`imported`) e metadado de arquivo.
- Consolidar no balanco mensal junto com lancamentos manuais.

## Fora de escopo v1
- Integracao direta por open finance.
- Auto-categorizacao por LLM.
- Regras avancadas por banco com parsing customizavel pelo usuario.

## Contrato e arquitetura
- REST: endpoint de upload + endpoint de preview + endpoint de confirmacao.
- GraphQL: fluxo equivalente (upload/persistencia conforme restricoes de transporte).
- Parser desacoplado por adaptadores de formato (`csv`, `ofx`).
- Normalizador central com contrato interno canonico.

## Regras de negocio
- Idempotencia por assinatura de arquivo + hash de linha normalizada.
- Nao inserir duplicados obvios no mesmo lote.
- Separar estado: `draft_import` vs `committed_import`.

## Seguranca e compliance
- Validar tipo/tamanho de arquivo.
- Sanitizar entradas textuais.
- Auditoria de upload/confirmacao.

## Observabilidade
- metricas: import_requests, import_parse_errors, import_rows_total, import_rows_committed.
- log estruturado por lote (import_batch_id).

## Criterios de aceite
- Usuario consegue importar CSV e visualizar preview antes de confirmar.
- Sistema registra origem do dado e consolida com dados manuais no balanco.
- Duplicidades obvias no mesmo lote sao bloqueadas.
- Testes de parser/normalizacao e contrato cobrindo erros de arquivo invalido.

## Riscos e mitigacao
- Risco: variacao de layout por banco.
  - Mitigacao: contrato canonico + adaptadores por formato/provedor.
- Risco: falso negativo de duplicidade.
  - Mitigacao: regras deterministicas minimas no v1 e revisao manual no preview.

## Dependencias
- Definicao de formato CSV minimo suportado.
- Estrategia de armazenamento de arquivo/lote.

## Estimativa
- Complexidade: alta
- Urgencia: alta
- Recomendacao: iniciar apos J1 estar definido/estavel.
