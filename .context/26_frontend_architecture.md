# Frontend Architecture — Auraxis Platform

Última atualização: 2026-02-23

> Documento canônico de arquitetura, padrões e diretrizes para `auraxis-app` (React Native)
> e `auraxis-web` (Nuxt 4). Toda decisão de design de código nos frontends deriva deste
> documento. Agentes e engenheiros devem ler este arquivo antes de qualquer trabalho frontend.

---

## 1. Princípios imutáveis

Estes princípios não são negociáveis. Nenhuma tarefa, prazo ou conveniência os cancela.

| Princípio | Descrição |
|:----------|:----------|
| **SOLID** | Single responsibility, Open/closed, Liskov, Interface segregation, Dependency inversion |
| **KISS** | A solução mais simples que funciona corretamente é a certa |
| **DRY** | Nenhuma lógica duplicada. Se copiou, abstraiu errado |
| **DI** | Componentes e hooks recebem dependências — não as instanciam |
| **Zero `any`** | TypeScript sem `any`. Jamais. Veja seção 4 |
| **Qualidade não é negociável** | Código de engenheiro sênior em toda linha entregue |

---

## 2. Foco de plataforma

- **App mobile (auraxis-app)** é o foco primário de uso e de produto.
- **Web (auraxis-web)** é importante, mas com ênfase em **PWA** que simule a experiência nativa do app.
- Decisões de UX, performance e prioridade de feature devem considerar mobile-first.
- A web não é uma versão simplificada — é uma versão adaptada para tela grande com paridade funcional.

**PWA requirements (auraxis-web):**
- Service worker com estratégia offline-first para rotas críticas
- `manifest.json` correto (ícones, `display: standalone`, `theme_color`)
- Lighthouse PWA score ≥ 90 (gate de CI)
- Instalável em iOS Safari e Android Chrome

---

## 3. Arquitetura de pastas — Feature-based

### Regra central

> **Features não importam de outras features.** Todo compartilhamento passa por `shared/`.

```
src/
  shared/                  ← código agnóstico de feature
    components/            ← Button, Input, Modal, Card (sem lógica de negócio)
    composables/ (web)     ← useDebounce, useMediaQuery, useLocalStorage
    hooks/ (app)           ← mesma ideia, nomenclatura React
    theme/                 ← TODOS os tokens de design (ver seção 5)
    types/                 ← tipos globais compartilhados
    utils/                 ← funções puras agnósticas
    constants/             ← constantes globais

  features/
    auth/
      components/          ← LoginForm, OTPInput (só usados por auth)
      composables|hooks/   ← useAuth, useSession
      screens|pages/       ← LoginScreen, ForgotPasswordScreen
      services/            ← authService (chama a API)
      types/               ← AuthUser, LoginPayload, SessionToken
      tests/               ← unitários co-localizados
      e2e/                 ← specs Playwright/Detox desta feature
    transactions/
      ...
    profile/
      ...

  app/ (ou layouts/ no Nuxt)
    ← routing, providers, bootstrapping global
```

### O que pertence a `shared/`

- Componentes que mais de uma feature usa
- Hooks/composables de utilidade geral (sem conhecimento de domínio)
- Tokens de design e tema
- Tipos TypeScript sem vínculo com uma feature específica

### O que pertence a uma feature

- Tudo que só faz sentido dentro daquele contexto de produto
- Serviços de API específicos da feature
- Tipos de domínio da feature
- Testes unitários e E2E da feature

---

## 4. TypeScript — Zero `any`, tipagem como Java

TypeScript no Auraxis é tratado como uma linguagem fortemente tipada.
Assuma que o código será lido por um desenvolvedor Java experiente que não conhece `any`.

### Proibições absolutas

```typescript
// ❌ NUNCA — any explícito
const process = (data: any): any => { ... }

// ❌ NUNCA — any implícito via cast
const result = (response as any).data

// ❌ NUNCA — unknown sem narrowing
function handle(value: unknown) {
  return value.name // erro: não houve narrowing
}

// ❌ NUNCA — object genérico quando há forma conhecida
const config: object = { timeout: 3000 }
```

### Padrões obrigatórios

```typescript
// ✅ Tipos de domínio explícitos
interface Transaction {
  id: string
  amount: number
  description: string
  category: TransactionCategory
  createdAt: Date
}

// ✅ Generics com restrições
function getById<T extends { id: string }>(list: T[], id: string): T | undefined {
  return list.find(item => item.id === id)
}

// ✅ Discriminated unions para estados
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error }

// ✅ unknown com narrowing explícito
function parseApiError(value: unknown): string {
  if (typeof value === 'string') return value
  if (value instanceof Error) return value.message
  return 'Unknown error'
}

// ✅ satisfies para validação sem perda de tipo
const theme = {
  colors: { primary: '#6366F1' }
} satisfies ThemeConfig

// ✅ Readonly para dados imutáveis
type Config = Readonly<{
  apiBaseUrl: string
  timeout: number
}>
```

### Tipos de retorno explícitos obrigatórios

```typescript
// ✅ Obrigatório em funções públicas e hooks/composables
function useTransactions(): UseTransactionsReturn { ... }
async function fetchUser(id: string): Promise<User> { ... }

// Props com interface nomeada — nunca inline em componentes públicos
interface ButtonProps {
  label: string
  variant: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onPress: () => void
}
```

---

## 5. Design Tokens — Zero valores hardcoded

Nenhum valor de estilo (cor, espaçamento, tipografia, sombra, borda) pode aparecer
diretamente em um componente. Todos os valores pertencem ao sistema de tokens.

### Hierarquia de tokens

```
shared/theme/
  tokens/
    primitives.ts    ← valores brutos (não usar diretamente em componentes)
    semantic.ts      ← tokens semânticos (use estes nos componentes)
    typography.ts    ← escala tipográfica
    spacing.ts       ← escala de espaçamento
    radius.ts        ← escala de border-radius
    shadows.ts       ← elevações/sombras
    motion.ts        ← durações e easings de animação
  index.ts           ← exporta tudo
```

### Camadas de token

```typescript
// primitives.ts — valores brutos, não usar em componentes
export const primitives = {
  color: {
    indigo500: '#6366F1',
    indigo600: '#4F46E5',
    red500:    '#EF4444',
    gray100:   '#F3F4F6',
    gray900:   '#111827',
  },
  space: {
    1: 4,
    2: 8,
    3: 12,
    4: 16,
    6: 24,
    8: 32,
  },
} as const

// semantic.ts — tokens de significado, use estes nos componentes
export const colors = {
  action: {
    primary:         primitives.color.indigo500,
    primaryHover:    primitives.color.indigo600,
    destructive:     primitives.color.red500,
  },
  surface: {
    background:      primitives.color.gray100,
    foreground:      primitives.color.gray900,
  },
} as const satisfies SemanticColors

// typography.ts
export const typography = {
  size: {
    xs:   12,
    sm:   14,
    md:   16,  // ← font-size: $font-md
    lg:   18,
    xl:   20,
    '2xl': 24,
    '3xl': 30,
  },
  weight: {
    regular: '400',
    medium:  '500',
    semibold: '600',
    bold:    '700',
  },
  lineHeight: {
    tight:   1.25,
    normal:  1.5,
    relaxed: 1.75,
  },
} as const

// spacing.ts
export const spacing = {
  xs:   primitives.space[1],   // 4px
  sm:   primitives.space[2],   // 8px
  md:   primitives.space[4],   // 16px
  lg:   primitives.space[6],   // 24px
  xl:   primitives.space[8],   // 32px
} as const
```

### Uso correto vs. errado

```typescript
// ❌ NUNCA — valor hardcoded
const styles = StyleSheet.create({
  title: { fontSize: 16, color: '#6366F1', marginTop: 8 }
})

// ✅ SEMPRE — token semântico
import { typography, colors, spacing } from '@/shared/theme'

const styles = StyleSheet.create({
  title: {
    fontSize:   typography.size.md,
    color:      colors.action.primary,
    marginTop:  spacing.sm,
  }
})
```

---

## 6. Componentes — Estrutura e limites

### Regra de tamanho

- **Máximo 250 linhas por arquivo de componente.** Acima disso, algo deve ser extraído.
- Se o componente tem mais de um "pedaço" visual independente, é dois componentes.
- Se o componente tem lógica que poderia ser reutilizada, é um hook/composable.

### O que um componente faz

```
✅ Faz
- Renderiza UI baseada em props
- Chama hooks/composables para obter dados e handlers
- Delega eventos para callbacks recebidos via props
- Aplica tokens de tema para estilos
- Tem contratos de props explícitos (interface nomeada)

❌ Não faz
- Chama API diretamente
- Contém lógica de negócio
- Conhece detalhes de roteamento (exceto primitivos de nav)
- Tem estado global
- Tem valores hardcoded de estilo
```

### Estrutura de arquivo de componente

```typescript
// 1. Imports externos
// 2. Imports internos (theme, types, hooks)
// 3. Interface de props (nomeada, exportada)
// 4. Componente (função nomeada, nunca arrow anônima no export)
// 5. Estilos (sempre no final, sempre via tokens)

// ✅ Exemplo canônico (React Native)
import React from 'react'
import { Pressable, Text, StyleSheet, ViewStyle } from 'react-native'

import { colors, typography, spacing, radius } from '@/shared/theme'
import type { HapticFeedbackType } from '@/shared/types'

export interface ButtonProps {
  label: string
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onPress: () => void
  testID?: string
}

export function Button({
  label,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onPress,
  testID,
}: ButtonProps): React.JSX.Element {
  return (
    <Pressable
      style={[styles.base, styles[variant], styles[size], disabled && styles.disabled]}
      onPress={onPress}
      disabled={disabled || loading}
      accessibilityRole="button"
      accessibilityLabel={label}
      testID={testID}
    >
      <Text style={[styles.label, styles[`label_${size}`]]}>
        {loading ? '...' : label}
      </Text>
    </Pressable>
  )
}

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: radius.md,
  },
  primary: {
    backgroundColor: colors.action.primary,
  },
  secondary: {
    backgroundColor: colors.surface.background,
    borderWidth: 1,
    borderColor: colors.action.primary,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  sm:    { paddingVertical: spacing.xs, paddingHorizontal: spacing.sm },
  md:    { paddingVertical: spacing.sm, paddingHorizontal: spacing.md },
  lg:    { paddingVertical: spacing.md, paddingHorizontal: spacing.lg },
  disabled: { opacity: 0.5 },
  label: {
    fontWeight: typography.weight.semibold,
    color:      colors.text.onPrimary,
  },
  label_sm: { fontSize: typography.size.sm },
  label_md: { fontSize: typography.size.md },
  label_lg: { fontSize: typography.size.lg },
})
```

---

## 7. Hooks e Composables — Lógica de negócio

Toda lógica que não é renderização mora aqui.

```typescript
// ✅ Hook com tipo de retorno explícito e DI
interface UseTransactionsOptions {
  userId: string
  limit?: number
}

interface UseTransactionsReturn {
  transactions: Transaction[]
  isLoading: boolean
  error: Error | null
  refetch: () => Promise<void>
  createTransaction: (payload: CreateTransactionPayload) => Promise<Transaction>
}

export function useTransactions({
  userId,
  limit = 20,
}: UseTransactionsOptions): UseTransactionsReturn {
  // lógica aqui
}
```

**Regras:**
- Tipo de retorno sempre explícito e exportado
- Nunca retornar `any` ou objeto sem tipo
- Dependências injetadas via parâmetros (não instanciadas internamente)
- Um hook = uma responsabilidade

---

## 8. Serviços de API

```typescript
// ✅ Serviço tipado, sem any, sem conhecimento de UI
interface TransactionService {
  list(userId: string, options: PaginationOptions): Promise<PaginatedResult<Transaction>>
  create(payload: CreateTransactionPayload): Promise<Transaction>
  delete(id: string): Promise<void>
}

export const transactionService: TransactionService = {
  async list(userId, options) {
    const response = await apiClient.get<PaginatedResult<Transaction>>(
      `/transactions?userId=${userId}&limit=${options.limit}&offset=${options.offset}`
    )
    return response.data
  },
  // ...
}
```

**Regras:**
- Interface declarada separadamente da implementação (DI / testabilidade)
- Erros de API convertidos para tipos de erro do domínio antes de propagar
- Nunca retornar a resposta HTTP bruta — sempre o dado tipado

---

## 9. Testes — Critério de aceite

Feature não está entregue sem:

| Tipo | Cobertura mínima | Ferramenta |
|:-----|:-----------------|:-----------|
| Unitários (componentes, hooks) | ≥ 85% das linhas | Vitest (web) / jest-expo (app) |
| E2E (fluxos completos) | Todo fluxo de usuário | Playwright (web) / Detox (app) |

### E2E como gate de merge

```
✅ PR aceito   → testes unitários passam + E2E do fluxo passam
❌ PR bloqueado → qualquer E2E falhando, mesmo que unitários passem
```

### O que tem E2E obrigatório

- Login, logout, recuperação de senha
- Criação, edição e exclusão de qualquer entidade principal
- Fluxos de pagamento ou transação
- Onboarding e cadastro
- Qualquer fluxo com mais de 2 passos sequenciais

---

## 10. Performance

Referência de fluidez: Airbnb, Netflix, Facebook.
Não é estética — é ausência de gargalo, travamento, delay e stuttering.

### Budgets por plataforma

| Métrica | Web (Lighthouse) | App (Perfmon) |
|:--------|:-----------------|:--------------|
| LCP | ≤ 2.5s | — |
| FID / INP | ≤ 100ms | — |
| CLS | ≤ 0.1 | — |
| Bundle inicial | ≤ 250KB gzip | — |
| Frame rate | 60fps | 60fps estável |
| JS thread block | — | ≤ 16ms |

**Regras:**
- Listas longas: virtualização obrigatória (`FlashList` no app, virtual scroll no web)
- Imagens: lazy load + dimensões explícitas (evita CLS)
- Animações: apenas na thread de UI (`Reanimated` no app, CSS transforms no web)
- Code splitting: cada feature é um chunk separado
- Memoização: `useMemo`/`useCallback`/`computed` apenas quando há benchmark justificando — nunca prematuramente

---

## 11. Acessibilidade (piso obrigatório)

- WCAG AA em todos os componentes base
- `accessibilityRole` e `accessibilityLabel` em todo elemento interativo (app)
- `role` e `aria-label` em todo elemento interativo (web)
- Imagens: `alt` descritivo obrigatório
- Formulários: `label` associado a todo `input`
- Contraste de cores: mínimo 4.5:1 para texto normal, 3:1 para texto grande
- Lighthouse A11y score ≥ 90 (gate de CI no web)

---

## 12. Sequência de entrega — "Bases antes de features"

```
Antes de implementar uma feature:
  → Identificar quais componentes de shared/ ela precisa
  → Se o componente não existe: criá-lo primeiro (com testes + docs)
  → Se o componente existe mas incompleto: completá-lo antes
  → Só então implementar a feature

Critério de "componente pronto":
  → Props tipadas com interface nomeada
  → Testes unitários cobrindo variantes principais
  → Usa apenas tokens de tema (zero hardcode)
  → Acessibilidade básica (role + label)
  → Máximo 250 linhas
```

**Just-in-time:** não construir o design system inteiro antes de começar.
Construir cada componente quando a primeira feature que o usa é implementada.
Isso garante momentum sem sacrificar qualidade.

---

## 13. Referências por repo

| Arquivo | Repo | Conteúdo |
|:--------|:-----|:---------|
| `CODING_STANDARDS.md` | `auraxis-app` | Padrões RN + Expo específicos |
| `CODING_STANDARDS.md` | `auraxis-web` | Padrões Vue/Nuxt específicos |
| `steering.md` | ambos | Quality gates, CI, branching |
| `.context/quality_gates.md` | ambos | Jobs de CI detalhados |
| `25_quality_security_playbook.md` | platform | Playbook unificado de qualidade |
