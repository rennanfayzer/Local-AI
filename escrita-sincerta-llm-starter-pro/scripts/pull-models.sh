#!/usr/bin/env bash

# ==========================================
# ESCRITA SINCERTA LLM - PULL DE MODELOS
# ==========================================

set -euo pipefail

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
MODELS=${OLLAMA_MODELS:-"phi3:3.8b,qwen2.5:7b,llama3.1:8b-instruct"}
TIMEOUT=300 # 5 minutos por modelo

echo -e "${BLUE}🤖 Escrita Sincerta LLM - Download de Modelos${NC}"
echo -e "${BLUE}=============================================${NC}"

# Verifica se Ollama está rodando
check_ollama() {
    echo -e "${YELLOW}🔍 Verificando conectividade com Ollama...${NC}"
    
    for i in {1..30}; do
        if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Ollama disponível em $OLLAMA_URL${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Aguardando Ollama... ($i/30)${NC}"
        sleep 2
    done
    
    echo -e "${RED}❌ Ollama não está disponível em $OLLAMA_URL${NC}"
    echo -e "${RED}   Certifique-se de que o Ollama está rodando:${NC}"
    echo -e "${RED}   docker compose up -d ollama${NC}"
    exit 1
}

# Lista modelos já baixados
list_existing_models() {
    echo -e "${BLUE}📋 Modelos já disponíveis:${NC}"
    
    if models_json=$(curl -s "$OLLAMA_URL/api/tags" 2>/dev/null); then
        if echo "$models_json" | jq -e '.models | length > 0' > /dev/null 2>&1; then
            echo "$models_json" | jq -r '.models[]? | "  • \(.name) (\(.size // "tamanho desconhecido"))"'
        else
            echo -e "${YELLOW}  (nenhum modelo baixado)${NC}"
        fi
    else
        echo -e "${YELLOW}  (erro ao listar modelos)${NC}"
    fi
    echo ""
}

# Baixa um modelo específico
pull_model() {
    local model="$1"
    echo -e "${GREEN}📥 Baixando modelo: $model${NC}"
    
    # Inicia o pull
    if ! curl -s "$OLLAMA_URL/api/pull" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$model\"}" \
        --max-time $TIMEOUT > /tmp/ollama_pull.log 2>&1; then
        
        echo -e "${RED}❌ Erro no download de $model${NC}"
        if [[ -f /tmp/ollama_pull.log ]]; then
            echo -e "${RED}   Log de erro:${NC}"
            cat /tmp/ollama_pull.log | tail -5
        fi
        return 1
    fi
    
    # Verifica se o modelo foi instalado
    if curl -s "$OLLAMA_URL/api/tags" | jq -e --arg model "$model" '.models[]? | select(.name == $model)' > /dev/null; then
        echo -e "${GREEN}✅ Modelo $model baixado com sucesso${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Modelo $model pode não ter sido instalado corretamente${NC}"
        return 1
    fi
}

# Função principal
main() {
    echo -e "Modelos configurados: ${BLUE}$MODELS${NC}"
    echo ""
    
    check_ollama
    list_existing_models
    
    # Converte string de modelos em array
    IFS=',' read -ra model_array <<< "$MODELS"
    
    local success_count=0
    local total_models=${#model_array[@]}
    
    echo -e "${BLUE}🚀 Iniciando download de $total_models modelos...${NC}"
    echo ""
    
    for model in "${model_array[@]}"; do
        # Remove espaços em branco
        model=$(echo "$model" | xargs)
        
        if [[ -n "$model" ]]; then
            if pull_model "$model"; then
                ((success_count++))
            fi
            echo ""
        fi
    done
    
    # Relatório final
    echo -e "${BLUE}📊 Relatório Final${NC}"
    echo -e "${BLUE}=================${NC}"
    echo -e "Modelos baixados com sucesso: ${GREEN}$success_count${NC}/$total_models"
    
    if [[ $success_count -eq $total_models ]]; then
        echo -e "${GREEN}🎉 Todos os modelos foram baixados com sucesso!${NC}"
        
        # Lista final de modelos
        echo ""
        list_existing_models
        
        echo -e "${GREEN}✨ Pronto para usar! Acesse:${NC}"
        echo -e "   🌐 Open WebUI: http://localhost:3000"
        echo -e "   🔌 API: http://localhost:8000"
        
    elif [[ $success_count -eq 0 ]]; then
        echo -e "${RED}❌ Nenhum modelo foi baixado. Verifique sua conexão.${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Alguns modelos falharam no download.${NC}"
        echo -e "${YELLOW}   Você pode tentar novamente mais tarde.${NC}"
    fi
}

# Executa com tratamento de erros
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    trap 'echo -e "\n${RED}❌ Script interrompido${NC}"' INT TERM
    main "$@"
fi
