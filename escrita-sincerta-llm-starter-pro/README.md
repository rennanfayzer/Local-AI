# 🤖 Escrita Sincerta LLM - Starter Pro

**Sistema LLM local completo com agentes especializados, RAG vetorial e interface web**

![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Ollama%20%7C%20PostgreSQL%20%7C%20OpenWebUI-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker](https://img.shields.io/badge/Docker-Compose%20Ready-2496ED)

---

## 🎯 **Visão Geral**

Sistema LLM 100% local que implementa o **Manifesto "Escrita Sincerta"** - comunicação direta, técnica e honesta. Inclui agentes especializados, memória vetorial persistente e interface web intuitiva.

### ✨ **Características Principais**

- 🔒 **100% Local** - Sem dependência de APIs externas
- 🤖 **5 Agentes Especializados** - Ideator, Architect, Builder, Dev, Reflexivo
- 📚 **RAG Avançado** - ChromaDB + embeddings locais
- 🔀 **Roteamento Inteligente** - Seleção automática de modelo por complexidade
- 💾 **Histórico Persistente** - Salve e gerencie conversas por projeto
- 🚀 **Execução Local Nativa** - Rápido, leve e sem Docker
- 🔧 **Multiplataforma** - Windows (PowerShell) e Linux/macOS (Bash)

---

## 🚀 **Início Rápido**

### 1. **Pré-requisitos**
- Python 3.11+
- Ollama instalado e rodando

### 2. **Instalação e Execução**

```powershell
# Clone ou extraia o projeto
cd escrita-sincerta-llm-starter-pro

# Windows (Recomendado)
.\\run_local.ps1

# Linux/macOS (ou Manual no Windows)
# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\\venv\\Scripts\\Activate.ps1 # Windows

# 2. Instale as dependências
pip install -r api/requirements.txt

# 3. Inicie a API
cd api
uvicorn app:app --reload
```

### 3. **Acessos**
- 🌐 **Interface Web**: http://localhost:3000 (requer `python -m http.server 3000` na pasta `frontend`)
- 🔌 **API**: http://localhost:8000
- 📊 **Documentação**: http://localhost:8000/docs

---

## 🏗️ **Arquitetura**

A arquitetura foi simplificada para execução local, removendo a necessidade de Docker, PostgreSQL e Redis.

```mermaid
graph TB
    UI[Interface Web :3000] --> API[FastAPI Orquestradora :8000]
    API --> OLLAMA[Ollama :11434]
    API --> RAG[Sistema RAG com ChromaDB]
    API --> HIST[Gerenciador de Histórico]
    
    HIST --> FS[Sistema de Arquivos (data/conversations)]
    DOCS[data/docs] --> RAG
    
    OLLAMA --> M1[phi3:3.8b]
    OLLAMA --> M2[qwen2.5:7b] 
    OLLAMA --> M3[llama3.1:8b]
```

### 🧱 **Componentes**

| Serviço | Responsabilidade |
|---------|------------------|
| **FastAPI** | Orquestração, agentes, RAG, histórico |
| **Ollama** | Runtime de modelos LLM |
| **ChromaDB**| Banco de dados vetorial para RAG |
| **Frontend**| Interface de chat estática (HTML/JS) |

---

## 🤖 **Agentes Especializados**

### 💡 **Ideator SaaS**
- **Especialidades**: Ideação de produtos, análise de mercado, MVP, personas
- **Metodologias**: Design Thinking, Lean Startup, Jobs-to-be-Done
- **Capacidades**: Validação de ideias, competição, monetização, pitch

### 🏗️ **Architect Fullstack**
- **Especialidades**: Arquitetura de sistemas, escalabilidade, cloud native
- **Padrões**: Microservices, Event-Driven, CQRS, DDD
- **Capacidades**: Design de sistemas complexos, seleção de tecnologias, DevOps

### 🛠️ **Builder Web**
- **Especialidades**: Scaffolding multi-framework (React, Vue, Flutter, FastAPI, Node.js)
- **Templates**: SaaS, E-commerce, Dashboards, APIs, Mobile
- **Capacidades**: Geração de projetos completos, boilerplates, best practices

### 🔧 **Dev Fullstack**
- **Modelo**: `qwen2.5:7b` (configurável)
- **Especialidades**: Python, JavaScript, APIs, debugging, desenvolvimento geral
- **Capacidades**: Code generation, review, refactoring, testing

### 🧠 **Reflexivo**
- **Modelo**: `phi3:3.8b` (otimizado para análise)
- **Especialidades**: Análise de problemas, planejamento estratégico, decisões
- **Capacidades**: Decomposição de problemas, risk assessment, retrospectivas

---

## 📋 **Comandos Disponíveis**

### **Via Makefile (Universal)**
```bash
make help          # Lista todos os comandos
make up            # Inicia todos os serviços
make pull          # Baixa modelos LLM
make ingest        # Processa documentos para RAG
make logs          # Mostra logs em tempo real
make status        # Status dos serviços
make reset         # Reset completo do ambiente
```

### **Via Scripts Dedicados**

**Windows (PowerShell)**
```powershell
.\scripts\dev.ps1 start         # Inicia ambiente
.\scripts\dev.ps1 pull          # Baixa modelos  
.\scripts\dev.ps1 ingest        # Ingere documentos
.\scripts\dev.ps1 logs          # Logs em tempo real
.\scripts\dev.ps1 status        # Health check
.\scripts\dev.ps1 shell         # Acessa container
```

**Linux/macOS (Bash)**
```bash
./scripts/dev.sh start          # Inicia ambiente
./scripts/dev.sh pull           # Baixa modelos
./scripts/dev.sh ingest         # Ingere documentos  
./scripts/dev.sh logs           # Logs em tempo real
./scripts/dev.sh status         # Health check
./scripts/dev.sh shell          # Acessa container
```

---

## 🔧 **Configuração**

### **Arquivo .env**
```bash
# Portas principais
OPENWEBUI_PORT=3000
API_PORT=8000

# Modelos (ajustar conforme hardware)
SMALL_MODEL=phi3:3.8b
GENERAL_MODEL=qwen2.5:7b  
HEAVY_MODEL=llama3.1:8b-instruct

# PostgreSQL
POSTGRES_USER=sincerta
POSTGRES_PASSWORD=escrita_segura_2024
POSTGRES_DB=sincerta_memory

# RAG
RAG_TOP_K=5
RAG_CHUNK_SIZE=1000
EMBEDDING_MODEL=bge-m3
```

### **Modelos Recomendados por Uso**

| Cenário | Modelo | RAM Necessária | Performance |
|---------|--------|----------------|-------------|
| **Desenvolvimento Rápido** | `phi3:3.8b` | 6GB | ⚡⚡⚡ |
| **Uso Geral** | `qwen2.5:7b` | 8GB | ⚡⚡ |
| **Arquitetura Complexa** | `llama3.1:8b` | 12GB | ⚡ |

---

## 📚 **Sistema RAG**

### **Como Funciona**
1. **Ingestão**: Documentos → Chunks → Embeddings → pgvector
2. **Query**: Pergunta → Embedding → Busca vetorial → Contexto
3. **Resposta**: LLM + Contexto → Resposta enriquecida

### **Tipos de Arquivo Suportados**
- 📄 Markdown (.md)
- 📝 Texto (.txt) 
- 🌐 HTML (.html)
- 📑 PDF (.pdf) - *em desenvolvimento*

### **Uso do RAG**
```bash
# Adicionar documentos
cp meus-docs/* data/docs/
make ingest

# Query via API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como implementar autenticação?"}'
```

---

## 🔌 **API Endpoints**

### **Principais**
```http
GET  /health              # Health check
GET  /models              # Modelos disponíveis  
GET  /agents              # Agentes ativos
POST /chat                # Chat com agentes
POST /ingest              # Ingestão de documentos
POST /query               # Busca RAG
POST /upload              # Upload de arquivos

### **Gerenciamento de Histórico**
```http
GET  /projects            # Lista todos os projetos
POST /projects            # Cria um novo projeto
GET  /history/{project_name} # Carrega o histórico de um projeto
POST /history/{project_name} # Salva o histórico de um projeto
```

### **Exemplo de Chat**
```json
{
  "agent": "dev_fullstack",
  "message": "Como criar uma API REST com FastAPI?",
  "task_type": "generate", 
  "complexity": "normal",
  "context": {
    "project_type": "backend_api",
    "database": "postgresql"
  }
}
```

---

## 🎨 **Manifesto "Escrita Sincerta"**

### **Princípios Core**
- ✅ **Verdade > Agradar** - Se não souber, admita
- ⚡ **Direção > Divagação** - Resolva antes de pedir dados
- 🎯 **Clareza + Empatia** - Técnico mas humano

### **Formato Obrigatório**
```markdown
🔍 CONTEXTO
[Problema identificado, situação atual]

⚡ SOLUÇÃO  
[Abordagem técnica, decisões justificadas]

💻 CÓDIGO/EXEMPLO
[Implementação funcional, production-ready]

✅ CHECKLIST
[Critérios de validação, passos de teste]
```

---

## 🛠️ **Desenvolvimento**

### **Estrutura do Projeto**Nao
```
escrita-sincerta-llm-starter-pro/
├── api/                    # FastAPI + Agentes
│   ├── agents/            # Agentes especializados  
│   ├── tools/             # RAG, arquivos, histórico, etc.
│   ├── prompts/           # Manifesto e styles
│   └── app.py             # API principal
├── data/
│   ├── docs/              # Documentos para RAG
│   ├── vectors/           # Dados ChromaDB
│   └── conversations/     # Históricos de conversa salvos
├── scripts/               # Automação
│   ├── pull-models.sh     # Download de modelos
│   ├── dev.ps1           # Windows toolkit
│   └── dev.sh            # Linux/macOS toolkit  
├── docker-compose.yml     # Orquestração
├── Makefile              # Comandos universais
└── README.md             # Este arquivo
```

### **Adicionando Novos Agentes**
1. Crie arquivo em `api/agents/meu_agente.py`
2. Herde de `BaseAgent` ou use `@register_agent`
3. Implemente `get_system_prompt()` e `process_message()`
4. Teste via API endpoint `/chat`

### **Customizando Prompts**
- **Manifesto**: `api/prompts/manifesto_sincerta.md`
- **System Base**: `api/prompts/system_base.md` 
- **Estilos**: `api/prompts/styles.json`

---

## 🚨 **Troubleshooting**

### **Problemas Comuns**

| Problema | Diagnóstico | Solução |
|----------|-------------|---------|
| **API não inicia** | `ModuleNotFoundError` | Ative o ambiente virtual (`.\\venv\\Scripts\\Activate.ps1`) e rode `pip install -r api/requirements.txt` |
| **API erro 500** | `make logs-api` | Verifique os logs no terminal onde a API está rodando |
| **Modelos não carregam** | `curl localhost:11434` não responde | Verifique se o Ollama está em execução |
| **RAG não funciona** | Erros de permissão em `data/` | Verifique as permissões da pasta |

### **Comandos de Debug**
```bash
# Verificar saúde da API (após iniciar)
curl http://localhost:8000/health

# Listar modelos no Ollama
curl http://localhost:11434/api/tags
```

---

## 🔮 **Roadmap e Status**

### **📊 Status Atual**: 60% Completo - [Ver STATUS.md](STATUS.md)

**✅ Implementado:**
- 5 Agentes Especializados (Ideator, Architect, Builder, Dev, Reflexivo)
- Sistema de Roteamento Inteligente
- RAG com ChromaDB
- API Completa (20+ endpoints)
- Histórico de Conversas Persistente
- Execução Local Nativa

**🚧 Próximas Funcionalidades:**
- 🎤 Conversa por Voz (Whisper + TTS)
- 🎨 Geração de Imagem e Vídeo (Stable Diffusion + FFmpeg)
- 📦 Biblioteca de Templates Expandida
- 📊 Monitoramento Avançado (Prometheus + Grafana)
- 🚀 Deploy em Cloud
- 🔐 Segurança e Autenticação

**📋 Roadmap Completo**: [ROADMAP.md](ROADMAP.md)

---

## 📜 **Licença**

MIT License - Veja arquivo `LICENSE` para detalhes.

---

## 🤝 **Contribuição**

1. Fork do projeto
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Crie Pull Request

---

## 📞 **Suporte**

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/escrita-sincerta-llm/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/escrita-sincerta-llm/discussions)
- 📧 **Contato**: [seu-email@exemplo.com]

---

**🚀 Desenvolvido com o Manifesto "Escrita Sincerta" - Direto, Técnico, Honesto.**
