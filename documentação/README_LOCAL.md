# Execução Local (sem Docker)

## Pré-requisitos

1. **Python 3.13+** instalado
2. **Ollama** rodando localmente em `http://localhost:11434`

## Instalação

Já está tudo configurado! O ambiente virtual foi criado e as dependências instaladas.

## Execução

### Opção 1: Script automatizado (Recomendado)

```powershell
.\run_local.ps1
```

### Opção 2: Manual

```powershell
# 1. Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# 2. Copiar configuração local
Copy-Item .env.local .env

# 3. Criar diretórios
New-Item -ItemType Directory -Path data\docs, data\vectors, logs -Force

# 4. Rodar API
cd api
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Acesso

- **API**: http://localhost:8000
- **Documentação Interativa**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🌐 Acesso em Rede Local

Por padrão, a API já inicia de forma a aceitar conexões de outros dispositivos na sua rede, pois o comando de execução inclui `--host 0.0.0.0`.

Para que funcione, você precisa garantir que o **Ollama** também aceite essas conexões.

**Passo 1: Configurar o Ollama para Acesso em Rede**

1.  Clique no Menu Iniciar e digite `env`.
2.  Selecione "Editar as variáveis de ambiente para sua conta".
3.  Na seção "Variáveis de usuário", clique em **Novo...**.
    *   **Nome da variável:** `OLLAMA_HOST`
    *   **Valor da variável:** `0.0.0.0`
4.  Clique em **OK** em todas as janelas e **reinicie o aplicativo Ollama** (feche-o na bandeja do sistema e abra-o novamente).

**Passo 2: Encontrar seu IP e Acessar**

1.  Abra o Prompt de Comando (`cmd`) e execute `ipconfig`.
2.  Anote o seu "Endereço IPv4" (ex: `192.168.1.10`).
3.  Após iniciar o projeto com `.\run_local.ps1`, você pode acessar a API de outro dispositivo na mesma rede usando o IP que você anotou:
    *   **Exemplo de Acesso:** `http://192.168.1.10:8000/docs`

## Estrutura de Dados

```
data/
  ├── docs/      # Documentos para RAG
  └── vectors/   # ChromaDB (vetores)
logs/
  └── api.log    # Logs da aplicação
```

## Diferenças do Docker

### ✅ O que funciona igual
- Agentes (Ideator, Architect, Builder, Dev, Reflexivo)
- RAG (Retrieval Augmented Generation)
- ChromaDB (armazenamento de vetores local)
- Integração com Ollama
- API REST completa

### ❌ O que foi removido
- PostgreSQL (não é essencial para o core)
- Redis (cache em memória)
- Sistema de Voz (removido anteriormente)
- Open WebUI (interface web separada)

## Testando

```powershell
# Verificar saúde da API
Invoke-RestMethod -Uri http://localhost:8000/health

# Listar agentes disponíveis
Invoke-RestMethod -Uri http://localhost:8000/agents

# Testar um agente
$body = @{
    agent = "ideator_saas"
    prompt = "Crie uma ideia de SaaS para gestão de tarefas"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/generate -Method Post -Body $body -ContentType "application/json"
```

## Liberação de Espaço

Total liberado do Docker: **~19.25 GB**
- Imagem API: 11.8 GB
- Volumes (postgres, redis, ollama cache): ~7 GB
- Build cache: ~0.45 GB

## Troubleshooting

### Erro: "Ollama não está rodando"
```powershell
# Verificar se o Ollama está ativo
curl http://localhost:11434/api/tags
```

### Erro: "ModuleNotFoundError"
```powershell
# Reinstalar dependências
pip install -r api\requirements.txt
```

### Erro: "Permission denied"
```powershell
# Executar PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Desenvolvimento

Para adicionar novos pacotes:

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Instalar pacote
pip install nome-do-pacote

# Atualizar requirements.txt
pip freeze > api\requirements.txt
```

## Performance

Executando localmente (sem Docker):
- ✅ Inicialização mais rápida (~2-5s vs ~30-60s)
- ✅ Menos consumo de memória RAM
- ✅ Sem overhead de containers
- ✅ Melhor performance de I/O de arquivos
- ✅ Hot-reload mais rápido durante desenvolvimento

---

**Versão**: 2.0.0 (Local)  
**Última atualização**: 12/10/2025