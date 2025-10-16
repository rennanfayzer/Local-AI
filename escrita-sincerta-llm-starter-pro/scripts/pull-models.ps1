# Baixa os modelos LLM necessários para o projeto usando Ollama
# Execute este script no PowerShell

$models = @(
    "phi3:3.8b",
    "qwen2.5:7b",
    "llama3.1:8b-instruct",
    "codegemma:7b"
)

$ollamaUrl = "http://localhost:11434"

foreach ($model in $models) {
    Write-Host "Baixando modelo: $model..."
    try {
        Invoke-RestMethod -Uri "$ollamaUrl/api/pull" -Method POST -Body (@{ name = $model } | ConvertTo-Json) -ContentType "application/json"
        Write-Host "Modelo $model baixado com sucesso!"
    } catch {
    Write-Host ("Erro ao baixar modelo: " + $model)
    Write-Host $_.Exception.Message
    }
}

Write-Host "Download dos modelos LLM finalizado."
