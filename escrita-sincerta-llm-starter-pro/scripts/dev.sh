#!/usr/bin/env bash

# ==========================================
# ESCRITA SINCERTA LLM - SCRIPT DE DESENVOLVIMENTO (Linux/macOS)
# ==========================================

set -euo pipefail

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variáveis padrão
COMMAND="${1:-help}"
FILE_PATH="${2:-}"
FORCE_FLAG="${FORCE:-false}"

# Funções utilitárias
log_info() {
    echo -e "${BLUE}$1${NC}"
}

log_success() {
    echo -e "${GREEN}$1${NC}"
}

log_warning() {
    echo -e "${YELLOW}$1${NC}"
}

log_error() {
    echo -e "${RED}$1${NC}"
}

show_header() {
    echo -e "${BLUE}🤖 Escrita Sincerta LLM - Ambiente de Desenvolvimento${NC}"
    echo -e "${BLUE}====================================================${NC}"
    echo ""
}

# Verifica pré-requisitos
check_prerequisites() {
    log_info "🔍 Verificando pré-requisitos..."
    
    # Docker
    if command -v docker >/dev/null 2>&1; then
        local docker_version=$(docker --version)
        log_success "✅ Docker: $docker_version"
    else
        log_error "❌ Docker não está instalado"
        log_error "   Instale em: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Docker Compose
    if docker compose version >/dev/null 2>&1; then
        local compose_version=$(docker compose version)
        log_success "✅ Docker Compose: $compose_version"
    else
        log_error "❌ Docker Compose não está disponível"
        exit 1
    fi
    
    # Arquivo .env
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            log_warning "📋 Copiando .env.example para .env..."
            cp .env.example .env
            log_success "✅ Arquivo .env criado"
        else
            log_warning "⚠️  Arquivo .env.example não encontrado"
        fi
    else
        log_success "✅ Arquivo .env encontrado"
    fi
    
    # jq (opcional)
    if command -v jq >/dev/null 2>&1; then
        log_success "✅ jq disponível para parsing JSON"
    else
        log_warning "⚠️  jq não encontrado (opcional, mas recomendado)"
        log_info "   Instale com: sudo apt install jq (Ubuntu) ou brew install jq (macOS)"
    fi
    
    echo ""
}

# Inicia serviços
start_services() {
    log_info "🚀 Iniciando serviços..."
    
    if docker compose up -d --build; then
        log_success "✅ Serviços iniciados com sucesso!"
        echo ""
        log_info "🌐 Acessos disponíveis:"
        echo -e "   • ${CYAN}Open WebUI: http://localhost:3000${NC}"
        echo -e "   • ${CYAN}API: http://localhost:8000${NC}"
        echo -e "   • ${CYAN}PostgreSQL: localhost:5432${NC}"
        echo -e "   • ${CYAN}Ollama: http://localhost:11434${NC}"
        echo ""
        
        # Aguarda serviços estarem prontos
        wait_for_services
    else
        log_error "❌ Falha ao iniciar serviços"
        exit 1
    fi
}

# Para serviços
stop_services() {
    log_warning "🛑 Parando serviços..."
    
    if docker compose down; then
        log_success "✅ Serviços parados"
    else
        log_error "❌ Erro ao parar serviços"
    fi
}

# Aguarda serviços ficarem prontos
wait_for_services() {
    log_info "⏳ Aguardando serviços ficarem prontos..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            log_success "✅ API está respondendo"
            break
        fi
        
        echo -ne "${YELLOW}\r   Tentativa $attempt/$max_attempts...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo ""
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_warning "⚠️  API ainda não está respondendo após $max_attempts tentativas"
        log_info "   Verifique os logs: ./dev.sh logs"
    fi
}

# Mostra logs
show_logs() {
    log_info "📋 Mostrando logs dos serviços..."
    docker compose logs -f --tail=100
}

# Baixa modelos
pull_models() {
    log_info "📥 Baixando modelos LLM..."
    
    # Verifica se Ollama está disponível
    local max_retries=30
    local retry=1
    
    while [[ $retry -le $max_retries ]]; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            break
        fi
        
        log_warning "⏳ Aguardando Ollama... ($retry/$max_retries)"
        sleep 2
        ((retry++))
    done
    
    if [[ $retry -gt $max_retries ]]; then
        log_error "❌ Ollama não está disponível"
        log_error "   Execute: ./dev.sh start"
        exit 1
    fi
    
    # Executa script de pull
    if [[ -x "scripts/pull-models.sh" ]]; then
        bash scripts/pull-models.sh
    else
        log_error "❌ Script pull-models.sh não encontrado ou não executável"
        exit 1
    fi
}

# Ingere documentos
ingest_documents() {
    local path="${1:-data/docs}"
    
    log_info "📚 Iniciando ingestão de documentos: $path"
    
    # Verifica se a API está disponível
    if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log_error "❌ API não está disponível"
        log_error "   Execute: ./dev.sh start"
        exit 1
    fi
    
    # Executa ingestão
    if command -v jq >/dev/null 2>&1; then
        curl -s -X POST "http://localhost:8000/ingest" \
            -H "Content-Type: application/json" \
            -d "{\"path\": \"$path\"}" | jq .
    else
        curl -s -X POST "http://localhost:8000/ingest" \
            -H "Content-Type: application/json" \
            -d "{\"path\": \"$path\"}"
    fi
    
    if [[ $? -eq 0 ]]; then
        log_success "✅ Ingestão concluída"
    else
        log_error "❌ Erro na ingestão"
    fi
}

# Mostra status dos serviços
show_status() {
    log_info "📊 Status dos Serviços"
    log_info "======================"
    
    # Status dos containers
    docker compose ps
    echo ""
    
    # Health checks
    log_info "🏥 Health Checks"
    
    # API
    if api_response=$(curl -s http://localhost:8000/health 2>/dev/null); then
        if command -v jq >/dev/null 2>&1; then
            local api_status=$(echo "$api_response" | jq -r '.api_status // "error"')
            log_success "✅ API: $api_status"
        else
            log_success "✅ API: ok"
        fi
    else
        log_error "❌ API: indisponível"
    fi
    
    # Ollama
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        log_success "✅ Ollama: ok"
    else
        log_error "❌ Ollama: indisponível"
    fi
    
    # Open WebUI
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        log_success "✅ Open WebUI: ok"
    else
        log_error "❌ Open WebUI: indisponível"
    fi
}

# Reset do ambiente
reset_environment() {
    if [[ "$FORCE_FLAG" != "true" ]]; then
        echo -n "⚠️  Isso irá remover todos os dados. Confirma? (y/N): "
        read -r confirmation
        
        if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
            log_warning "❌ Operação cancelada"
            return
        fi
    fi
    
    log_warning "🔄 Resetando ambiente..."
    
    # Para serviços e remove volumes
    docker compose down -v --remove-orphans
    
    # Remove volumes específicos
    local volumes=$(docker volume ls -q --filter name=escrita-sincerta 2>/dev/null || true)
    if [[ -n "$volumes" ]]; then
        docker volume rm $volumes 2>/dev/null || true
    fi
    
    log_success "✅ Ambiente resetado"
    log_info "   Execute: ./dev.sh start"
}

# Acessa shell do container
open_shell() {
    local service="${1:-api}"
    
    log_info "🐚 Abrindo shell no container: $service"
    
    if docker compose exec "$service" bash 2>/dev/null; then
        return 0
    elif docker compose exec "$service" sh 2>/dev/null; then
        return 0
    else
        log_error "❌ Erro ao acessar shell do container $service"
        return 1
    fi
}

# Testa API
test_api() {
    log_info "🧪 Testando API..."
    
    echo "Health:"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
    echo ""
    
    echo "Models:"
    curl -s http://localhost:8000/models | jq . 2>/dev/null || curl -s http://localhost:8000/models
    echo ""
    
    echo "Agents:"
    curl -s http://localhost:8000/agents | jq . 2>/dev/null || curl -s http://localhost:8000/agents
}

# Mostra ajuda
show_help() {
    log_info "📚 Comandos Disponíveis"
    log_info "======================"
    echo ""
    log_success "🚀 Principais:"
    echo "   start         - Inicia todos os serviços"
    echo "   stop          - Para todos os serviços"
    echo "   restart       - Reinicia serviços"
    echo "   status        - Mostra status dos serviços"
    echo ""
    log_success "📥 Modelos e Dados:"
    echo "   pull          - Baixa modelos LLM"
    echo "   ingest        - Ingere documentos do data/docs"
    echo "   ingest-file   - Ingere arquivo específico"
    echo ""
    log_success "🔍 Debug:"
    echo "   logs          - Mostra logs dos serviços"
    echo "   test-api      - Testa endpoints da API"
    echo "   shell         - Acessa shell do container"
    echo ""
    log_success "🧹 Limpeza:"
    echo "   reset         - Reset completo"
    echo ""
    log_warning "💡 Exemplos:"
    echo "   ./dev.sh start"
    echo "   ./dev.sh pull"
    echo "   ./dev.sh ingest-file meu-arquivo.md"
    echo "   ./dev.sh shell postgres"
    echo "   FORCE=true ./dev.sh reset"
}

# Função principal
main() {
    show_header
    
    case "${COMMAND}" in
        "start")
            check_prerequisites
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            ;;
        "pull")
            pull_models
            ;;
        "ingest")
            ingest_documents
            ;;
        "ingest-file")
            if [[ -n "$FILE_PATH" ]]; then
                ingest_documents "$FILE_PATH"
            else
                log_error "❌ Especifique o arquivo: ./dev.sh ingest-file path/to/file.md"
                exit 1
            fi
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "reset")
            reset_environment
            ;;
        "shell")
            service="${FILE_PATH:-api}"
            open_shell "$service"
            ;;
        "test-api")
            test_api
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "❌ Comando desconhecido: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Tratamento de sinais
trap 'echo -e "\n${RED}❌ Script interrompido${NC}"; exit 1' INT TERM

# Executa função principal
main "$@"