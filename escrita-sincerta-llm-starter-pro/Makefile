# ==========================================
# ESCRITA SINCERTA LLM - MAKEFILE
# ==========================================

# Carrega variáveis do .env se existir
-include .env
export

# Valores padrão
OPENWEBUI_PORT ?= 3000
API_PORT ?= 8000
POSTGRES_USER ?= sincerta
POSTGRES_DB ?= sincerta_memory

# Cores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m  
RED := \033[0;31m
NC := \033[0m # No Color

.DEFAULT_GOAL := help

##@ 🚀 Comandos Principais

.PHONY: up
up: ## Inicia todos os serviços (build se necessário)
	@echo "$(GREEN)🔧 Iniciando Escrita Sincerta LLM...$(NC)"
	@cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --build
	@echo "$(GREEN)✅ Serviços iniciados!$(NC)"
	@echo "$(YELLOW)🌐 Open WebUI: http://localhost:$(OPENWEBUI_PORT)$(NC)"
	@echo "$(YELLOW)🔌 API: http://localhost:$(API_PORT)$(NC)"
	@echo "$(YELLOW)🐘 PostgreSQL: localhost:5432$(NC)"

.PHONY: down  
down: ## Para todos os serviços
	@echo "$(YELLOW)🛑 Parando serviços...$(NC)"
	docker compose down
	@echo "$(GREEN)✅ Serviços parados$(NC)"

.PHONY: restart
restart: down up ## Reinicia todos os serviços

##@ 📥 Modelos e Dados

.PHONY: pull
pull: ## Baixa modelos LLM configurados
	@echo "$(GREEN)📥 Baixando modelos...$(NC)"
	@if [ -f "scripts/pull-models.sh" ]; then \
		bash scripts/pull-models.sh; \
	else \
		echo "$(YELLOW)⚠️  Script pull-models.sh não encontrado$(NC)"; \
	fi

.PHONY: ingest
ingest: ## Ingere documentos do diretório data/docs
	@echo "$(GREEN)📚 Iniciando ingestão de documentos...$(NC)"
	@curl -s -X POST "http://localhost:$(API_PORT)/ingest" \
		-H "Content-Type: application/json" \
		-d '{"path": "data/docs"}' | \
	jq . 2>/dev/null || \
	curl -s -X POST "http://localhost:$(API_PORT)/ingest" \
		-H "Content-Type: application/json" \
		-d '{"path": "data/docs"}'
	@echo "$(GREEN)✅ Ingestão concluída$(NC)"

.PHONY: ingest-file
ingest-file: ## Ingere arquivo específico (uso: make ingest-file FILE=caminho/arquivo.md)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Uso: make ingest-file FILE=caminho/arquivo.md$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)📄 Ingerindo arquivo: $(FILE)$(NC)"
	@curl -s -X POST "http://localhost:$(API_PORT)/ingest" \
		-H "Content-Type: application/json" \
		-d "{\"path\": \"$(FILE)\"}"

##@ 🔍 Monitoramento e Debug

.PHONY: logs
logs: ## Mostra logs de todos os serviços
	docker compose logs -f --tail=100

.PHONY: logs-api
logs-api: ## Mostra logs apenas da API
	docker compose logs -f --tail=100 api

.PHONY: logs-ollama  
logs-ollama: ## Mostra logs do Ollama
	docker compose logs -f --tail=100 ollama

.PHONY: logs-webui
logs-webui: ## Mostra logs do Open WebUI
	docker compose logs -f --tail=100 openwebui

.PHONY: status
status: ## Verifica status dos serviços
	@echo "$(GREEN)📊 Status dos Serviços$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(GREEN)🏥 Health Checks$(NC)"
	@echo "API: $$(curl -s http://localhost:$(API_PORT)/health | jq -r '.api_status // "error"' 2>/dev/null || echo "error")"
	@echo "Ollama: $$(curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && echo "ok" || echo "error")"

##@ 🛠️ Desenvolvimento

.PHONY: dev
dev: ## Inicia modo desenvolvimento (rebuild automático)
	@echo "$(GREEN)🔧 Modo desenvolvimento...$(NC)"
	docker compose up --build --watch

.PHONY: shell-api
shell-api: ## Acessa shell do container da API
	docker compose exec api bash

.PHONY: shell-db
shell-db: ## Acessa PostgreSQL via psql
	docker compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

.PHONY: test-api
test-api: ## Testa endpoints da API
	@echo "$(GREEN)🧪 Testando API...$(NC)"
	@echo "Health: $$(curl -s http://localhost:$(API_PORT)/health)"
	@echo "Models: $$(curl -s http://localhost:$(API_PORT)/models)"
	@echo "Agents: $$(curl -s http://localhost:$(API_PORT)/agents)"

##@ 🧹 Limpeza e Reset

.PHONY: clean
clean: ## Remove containers, volumes e imagens
	@echo "$(YELLOW)🧹 Limpando containers e volumes...$(NC)"
	docker compose down -v --remove-orphans
	docker compose rm -f
	@echo "$(GREEN)✅ Limpeza concluída$(NC)"

.PHONY: reset
reset: clean ## Reset completo (remove tudo e reinicia)
	@echo "$(YELLOW)🔄 Reset completo...$(NC)"
	docker volume rm $$(docker volume ls -q --filter name=escrita-sincerta) 2>/dev/null || true
	$(MAKE) up
	@echo "$(GREEN)✅ Reset concluído$(NC)"

.PHONY: reset-db
reset-db: ## Reset apenas do banco de dados
	@echo "$(YELLOW)🗃️ Resetando banco de dados...$(NC)"
	docker compose stop postgres
	docker volume rm $$(docker volume ls -q --filter name=postgres) 2>/dev/null || true
	docker compose up -d postgres
	@echo "$(GREEN)✅ Banco resetado$(NC)"

##@ 📋 Utilitários

.PHONY: backup
backup: ## Backup do banco de dados
	@echo "$(GREEN)💾 Criando backup...$(NC)"
	@mkdir -p backups
	docker compose exec postgres pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Backup criado em backups/$(NC)"

.PHONY: stats
stats: ## Mostra estatísticas do sistema
	@echo "$(GREEN)📊 Estatísticas RAG$(NC)"
	@curl -s "http://localhost:$(API_PORT)/query" \
		-X POST \
		-H "Content-Type: application/json" \
		-d '{"query": "stats"}' | \
	jq . 2>/dev/null || echo "$(RED)❌ API indisponível$(NC)"

.PHONY: models
models: ## Lista modelos disponíveis no Ollama
	@echo "$(GREEN)🤖 Modelos Disponíveis$(NC)"
	@curl -s http://localhost:11434/api/tags | jq -r '.models[]?.name // "Nenhum modelo encontrado"' 2>/dev/null || echo "$(RED)❌ Ollama indisponível$(NC)"

.PHONY: env
env: ## Cria arquivo .env a partir do exemplo
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Arquivo .env criado$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Arquivo .env já existe$(NC)"; \
	fi

##@ ℹ️ Ajuda

.PHONY: help  
help: ## Mostra esta ajuda
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(GREEN)Escrita Sincerta LLM - Comandos Disponíveis$(NC)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

.PHONY: info
info: ## Informações do projeto
	@echo "$(GREEN)📋 Informações do Projeto$(NC)"
	@echo "Nome: Escrita Sincerta LLM"
	@echo "Versão: 1.0.0"
	@echo "Stack: FastAPI + Ollama + Open WebUI + PostgreSQL + pgvector"
	@echo "Portas:"
	@echo "  - Open WebUI: $(OPENWEBUI_PORT)"
	@echo "  - API: $(API_PORT)"
	@echo "  - PostgreSQL: 5432"
	@echo "  - Ollama: 11434"
	@echo "  - Redis: 6379"
