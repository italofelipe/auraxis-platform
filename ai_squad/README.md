# Auraxis AI Squad - Agentes Autônomos

Esta pasta contém o ecossistema de agentes agênticos (Agentic AI) para automatizar o ciclo de desenvolvimento do Auraxis.
Ela agora fica no repositório de plataforma (`auraxis-platform`) e seleciona o repo-alvo por variável de ambiente.

## Estrutura do Esquadrão
- **PM (Gerente):** Analisa o `TASKS.md` e define o que fazer.
- **Backend Dev:** Implementa lógica em Flask/SQLAlchemy.
- **QA Engineer:** Roda o `pytest` e valida a implementação.

## Como usar (Mac OS)

1.  **Instalação (Crie um venv isolado):**
    ```bash
    cd ai_squad
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Configuração da API:**
    Crie um arquivo `.env` dentro de `ai_squad/` e adicione sua chave:
    ```bash
    OPENAI_API_KEY=sk-xxxx...
    ```
    *Nota: Você também pode usar modelos locais com **Ollama** se preferir.*

3.  **Configuração do repositório alvo (obrigatório):**
    ```bash
    export AURAXIS_TARGET_REPO=auraxis-api   # auraxis-api | auraxis-web | auraxis-app
    ```

4.  **Briefing da execução:**
    ```bash
    export AURAXIS_BRIEFING="Implementar task B9 ..."
    ```

5.  **Execução:**
    ```bash
    python3 main.py
    ```

## Status operacional e bloqueios

- Ao iniciar/finalizar uma execução, o squad registra status em `tasks_status/<TASK_ID>.md`.
- Em caso de erro/bloqueio, o run registra o motivo e imprime notificação para gestor e agentes paralelos no terminal.
- `tasks_status/` é telemetria local e **não deve ser commitado**.
- A única fonte de verdade de progresso continua sendo `tasks.md`/`TASKS.md` do repositório alvo.

## Como estender
- Adicione novos agentes (Frontend, Mobile, DevOps) no `main.py`.
- Crie novas ferramentas em `tools/project_tools.py` (ex: ferramenta de git commit, ferramenta de deploy aws).
- Mude o `Process.sequential` para `Process.hierarchical` para que o PM tome decisões mais complexas.
