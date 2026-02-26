SHELL := /bin/bash

PLATFORM_ROOT := /Users/italochagas/Desktop/projetos/auraxis-platform
SQUAD_DIR := $(PLATFORM_ROOT)/ai_squad
NEXT_TASK_SCRIPT := $(PLATFORM_ROOT)/scripts/ai-next-task.sh
BRIEFING ?= Execute a próxima tarefa

.PHONY: help squad-setup lock-status next-task next-task-all next-task-api next-task-web next-task-app next-task-safe next-task-plan

help:
	@echo "Targets:"
	@echo "  make squad-setup      - create/update ai_squad virtualenv and install deps"
	@echo "  make lock-status      - show current agent lock status"
	@echo "  make next-task        - run orchestrator for all repos (api/web/app)"
	@echo "  make next-task-all    - same as next-task"
	@echo "  make next-task-safe   - run orchestrator with automatic lock acquire/release"
	@echo "  make next-task-plan   - dry-run plan only (no writes/commits)"
	@echo "  make next-task-api    - run orchestrator only for auraxis-api"
	@echo "  make next-task-web    - run orchestrator only for auraxis-web"
	@echo "  make next-task-app    - run orchestrator only for auraxis-app"
	@echo ""
	@echo "Optional:"
	@echo "  BRIEFING='Seu comando' make next-task"

squad-setup:
	@test -d "$(SQUAD_DIR)" || (echo "Missing ai_squad dir: $(SQUAD_DIR)" && exit 1)
	cd "$(SQUAD_DIR)" && \
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

lock-status:
	cd "$(PLATFORM_ROOT)" && ./scripts/agent-lock.sh status

next-task: next-task-all

next-task-all:
	"$(NEXT_TASK_SCRIPT)" "all" "$(BRIEFING)"

next-task-safe:
	"$(NEXT_TASK_SCRIPT)" "all" "$(BRIEFING)" "safe"

next-task-plan:
	"$(NEXT_TASK_SCRIPT)" "all" "$(BRIEFING)" "plan"

next-task-api:
	"$(NEXT_TASK_SCRIPT)" "auraxis-api" "$(BRIEFING)"

next-task-web:
	"$(NEXT_TASK_SCRIPT)" "auraxis-web" "$(BRIEFING)"

next-task-app:
	"$(NEXT_TASK_SCRIPT)" "auraxis-app" "$(BRIEFING)"
