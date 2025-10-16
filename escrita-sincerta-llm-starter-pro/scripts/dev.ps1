# ==========================================
# ESCRITA SINCERTA LLM - SCRIPT DE DESENVOLVIMENTO (Windows)
# ==========================================

param(
    [string]$Command = "help",
    [string]$File = "",
    [switch]$Force = $false
)

# Configurações
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Cores para PowerShell
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
    White = "White"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Show-Header {
    Write-ColorOutput "🤖 Escrita Sincerta LLM - Ambiente de Desenvolvimento" "Blue"
    Write-ColorOutput "====================================================" "Blue"
    Write-Host ""
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Verificando pré-requisitos..." "Yellow"
    
    # Verifica Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Docker: $dockerVersion" "Green"
        } else {
            throw "Docker não encontrado"
        }
    } catch {
        Write-ColorOutput "❌ Docker não está instalado ou não está no PATH" "Red"
        Write-ColorOutput "   Baixe em: https://docs.docker.com/desktop/install/windows-install/" "Red"
        exit 1
    }
    
    # Verifica Docker Compose
    try {
        $composeVersion = docker compose version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Docker Compose: $composeVersion" "Green"
        } else {
            throw "Docker Compose não encontrado"
        }
    } catch {
        Write-ColorOutput "❌ Docker Compose não disponível" "Red"
        exit 1
    }
    
    # Verifica arquivo .env
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-ColorOutput "📋 Copiando .env.example para .env..." "Yellow"
            Copy-Item ".env.example" ".env"
            Write-ColorOutput "✅ Arquivo .env criado" "Green"
        } else {
            Write-ColorOutput "⚠️  Arquivo .env.example não encontrado" "Yellow"
        }
    } else {
        Write-ColorOutput "✅ Arquivo .env encontrado" "Green"
    }
    
    Write-Host ""
}

function Start-Services {
    Write-ColorOutput "🚀 Iniciando serviços..." "Green"
    
    try {
        docker compose up -d --build
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Serviços iniciados com sucesso!" "Green"
            Write-Host ""
            Write-ColorOutput "🌐 Acessos disponíveis:" "Blue"
            Write-ColorOutput "   • Open WebUI: http://localhost:3000" "Cyan"
            Write-ColorOutput "   • API: http://localhost:8000" "Cyan"  
            Write-ColorOutput "   • PostgreSQL: localhost:5432" "Cyan"
            Write-ColorOutput "   • Ollama: http://localhost:11434" "Cyan"
            Write-Host ""
        } else {
            throw "Erro ao iniciar serviços"
        }
    } catch {
        Write-ColorOutput "❌ Falha ao iniciar serviços: $($_.Exception.Message)" "Red"
        exit 1
    }
}

function Stop-Services {
    Write-ColorOutput "🛑 Parando serviços..." "Yellow"
    
    try {
        docker compose down
        Write-ColorOutput "✅ Serviços parados" "Green"
    } catch {
        Write-ColorOutput "❌ Erro ao parar serviços: $($_.Exception.Message)" "Red"
    }
}

function Show-Logs {
    Write-ColorOutput "📋 Mostrando logs dos serviços..." "Blue"
    docker compose logs -f --tail=100
}

function Pull-Models {
    Write-ColorOutput "📥 Baixando modelos LLM..." "Green"
    
    # Verifica se Ollama está rodando
    $maxRetries = 30
    $retries = 0
    
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
            break
        } catch {
            $retries++
            if ($retries -ge $maxRetries) {
                Write-ColorOutput "❌ Ollama não está disponível após $maxRetries tentativas" "Red"
                Write-ColorOutput "   Execute: .\dev.ps1 start" "Yellow"
                exit 1
            }
            Write-ColorOutput "⏳ Aguardando Ollama... ($retries/$maxRetries)" "Yellow"
            Start-Sleep -Seconds 2
        }
    } while ($retries -lt $maxRetries)
    
    # Executa script de pull
    if (Test-Path "scripts\pull-models.sh") {
        # Se WSL estiver disponível
        try {
            wsl bash scripts/pull-models.sh
        } catch {
            Write-ColorOutput "⚠️  WSL não disponível, usando PowerShell..." "Yellow"
            Pull-ModelsWindows
        }
    } else {
        Pull-ModelsWindows
    }
}

function Pull-ModelsWindows {
    # Implementação PowerShell para pull de modelos
    $models = @("phi3:3.8b", "qwen2.5:7b", "llama3.1:8b-instruct")
    
    foreach ($model in $models) {
        Write-ColorOutput "📥 Baixando modelo: $model" "Green"
        
        try {
            $body = @{ name = $model } | ConvertTo-Json
            Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 300
            Write-ColorOutput "✅ Modelo $model baixado com sucesso" "Green"
        } catch {
            Write-ColorOutput "❌ Erro ao baixar $model" "Red"
        }
    }
}

function Ingest-Documents {
    param([string]$Path = "data/docs")
    
    Write-ColorOutput "📚 Iniciando ingestão de documentos..." "Green"
    
    try {
        $body = @{ path = $Path } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8000/ingest" -Method Post -Body $body -ContentType "application/json"
        
        Write-ColorOutput "✅ Ingestão concluída: $($response.files_processed) arquivos processados" "Green"
    } catch {
        Write-ColorOutput "❌ Erro na ingestão: $($_.Exception.Message)" "Red"
        
        # Tenta com curl se disponível
        try {
            & curl -s -X POST "http://localhost:8000/ingest" -H "Content-Type: application/json" -d "{`"path`":`"$Path`"}"
        } catch {
            Write-ColorOutput "❌ curl também não está disponível" "Red"
        }
    }
}

function Show-Status {
    Write-ColorOutput "📊 Status dos Serviços" "Blue"
    Write-ColorOutput "=====================" "Blue"
    
    # Status dos containers
    docker compose ps
    Write-Host ""
    
    # Health checks
    Write-ColorOutput "🏥 Health Checks" "Blue"
    
    # API
    try {
        $apiResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-ColorOutput "✅ API: $($apiResponse.api_status)" "Green"
    } catch {
        Write-ColorOutput "❌ API: indisponível" "Red"
    }
    
    # Ollama
    try {
        Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 | Out-Null
        Write-ColorOutput "✅ Ollama: ok" "Green"
    } catch {
        Write-ColorOutput "❌ Ollama: indisponível" "Red"
    }
    
    # Open WebUI
    try {
        Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 | Out-Null
        Write-ColorOutput "✅ Open WebUI: ok" "Green"
    } catch {
        Write-ColorOutput "❌ Open WebUI: indisponível" "Red"
    }
}

function Reset-Environment {
    if (-not $Force) {
        $confirmation = Read-Host "⚠️  Isso irá remover todos os dados. Confirma? (y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-ColorOutput "❌ Operação cancelada" "Yellow"
            return
        }
    }
    
    Write-ColorOutput "🔄 Resetando ambiente..." "Yellow"
    
    # Para serviços
    docker compose down -v --remove-orphans
    
    # Remove volumes
    $volumes = docker volume ls -q --filter "name=escrita-sincerta" 2>$null
    if ($volumes) {
        docker volume rm $volumes 2>$null
    }
    
    Write-ColorOutput "✅ Ambiente resetado" "Green"
    Write-ColorOutput "   Execute: .\dev.ps1 start" "Yellow"
}

function Open-Shell {
    param([string]$Service = "api")
    
    Write-ColorOutput "🐚 Abrindo shell no container: $Service" "Blue"
    
    try {
        docker compose exec $Service bash
    } catch {
        # Tenta com sh se bash não estiver disponível
        try {
            docker compose exec $Service sh
        } catch {
            Write-ColorOutput "❌ Erro ao acessar shell do container $Service" "Red"
        }
    }
}

function Show-Help {
    Write-ColorOutput "📚 Comandos Disponíveis" "Blue"
    Write-ColorOutput "======================" "Blue"
    Write-Host ""
    Write-ColorOutput "🚀 Principais:" "Green"
    Write-Host "   start         - Inicia todos os serviços"
    Write-Host "   stop          - Para todos os serviços" 
    Write-Host "   restart       - Reinicia serviços"
    Write-Host "   status        - Mostra status dos serviços"
    Write-Host ""
    Write-ColorOutput "📥 Modelos e Dados:" "Green"
    Write-Host "   pull          - Baixa modelos LLM"
    Write-Host "   ingest        - Ingere documentos do data/docs"
    Write-Host "   ingest-file   - Ingere arquivo específico (-File path)"
    Write-Host ""
    Write-ColorOutput "🔍 Debug:" "Green"
    Write-Host "   logs          - Mostra logs dos serviços"
    Write-Host "   shell         - Acessa shell do container (-Service nome)"
    Write-Host ""
    Write-ColorOutput "🧹 Limpeza:" "Green"
    Write-Host "   reset         - Reset completo (-Force para sem confirmação)"
    Write-Host ""
    Write-ColorOutput "💡 Exemplos:" "Yellow"
    Write-Host "   .\dev.ps1 start"
    Write-Host "   .\dev.ps1 pull"
    Write-Host "   .\dev.ps1 ingest-file -File 'meu-arquivo.md'"
    Write-Host "   .\dev.ps1 shell -Service postgres"
    Write-Host "   .\dev.ps1 reset -Force"
}

# Função principal
function Main {
    Show-Header
    
    switch ($Command.ToLower()) {
        "start" { 
            Test-Prerequisites
            Start-Services 
        }
        "stop" { Stop-Services }
        "restart" { 
            Stop-Services
            Start-Services 
        }
        "pull" { Pull-Models }
        "ingest" { Ingest-Documents }
        "ingest-file" { 
            if ($File) {
                Ingest-Documents -Path $File
            } else {
                Write-ColorOutput "❌ Especifique o arquivo: -File path" "Red"
            }
        }
        "logs" { Show-Logs }
        "status" { Show-Status }
        "reset" { Reset-Environment }
        "shell" { 
            $service = if ($File) { $File } else { "api" }
            Open-Shell -Service $service
        }
        "help" { Show-Help }
        default { 
            Write-ColorOutput "❌ Comando desconhecido: $Command" "Red"
            Write-Host ""
            Show-Help
        }
    }
}

# Execução
try {
    Main
} catch {
    Write-ColorOutput "❌ Erro inesperado: $($_.Exception.Message)" "Red"
    exit 1
}