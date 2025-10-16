# Script para rodar a API localmente (sem Docker)

Write-Host "=== Escrita Sincerta - API Local ===" -ForegroundColor Cyan
Write-Host ""

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Criar diretórios necessários
Write-Host "Criando diretórios necessários..." -ForegroundColor Yellow
if (-not (Test-Path ".\data\docs")) {
    New-Item -ItemType Directory -Path ".\data\docs" -Force | Out-Null
}
if (-not (Test-Path ".\data\vectors")) {
    New-Item -ItemType Directory -Path ".\data\vectors" -Force | Out-Null
}
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs" -Force | Out-Null
}

Write-Host "Diretórios criados com sucesso!" -ForegroundColor Green

# Copiar .env.local para .env se não existir
if (-not (Test-Path ".\.env")) {
    Write-Host "Copiando configuração local (.env.local -> .env)..." -ForegroundColor Yellow
    Copy-Item ".\.env.local" ".\.env"
    Write-Host "Configuração copiada!" -ForegroundColor Green
}

# Verificar se Ollama está rodando
Write-Host ""
Write-Host "Verificando Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2
    Write-Host "OK - Ollama esta rodando!" -ForegroundColor Green
    Write-Host "  Modelos disponiveis:" -ForegroundColor Gray
    $response.models | ForEach-Object { Write-Host "    - $($_.name)" -ForegroundColor Gray }
} catch {
    Write-Host "ERRO - Ollama nao esta rodando" -ForegroundColor Red
    Write-Host "  Por favor, inicie o Ollama antes de continuar." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Deseja continuar mesmo assim? (S/N): " -NoNewline -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne "S" -and $continue -ne "s") {
        Write-Host "Execucao cancelada." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Iniciando API na porta 8000..." -ForegroundColor Yellow
Write-Host "Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor." -ForegroundColor Gray
Write-Host ""

# Rodar a API (deve executar do diretorio api/)
Set-Location -Path ".\api"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
