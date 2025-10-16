# ⚡ QUICK START - Escrita Sincerta LLM Pro
# ⚡ QUICK START - Escrita Sincerta LLM Pro (Execução Local)

## 🎯 O QUE É?

Sistema LLM 100% local com **5 agentes especializados**, **roteamento inteligente** e **histórico de conversas persistente**.

**Versão**: 2.0.2 | **Status**: 70% ✅

---

## 🚀 INSTALAÇÃO RÁPIDA

### Pré-requisitos
- **Python 3.11+**
- **Ollama** instalado e rodando.

### Windows (PowerShell) - Recomendado
```powershell
# 1. Iniciar a API (Backend)
cd escrita-sincerta-llm-starter-pro
.\\run_local.ps1

# 2. Em um NOVO terminal, iniciar a Interface (Frontend)
cd escrita-sincerta-llm-starter-pro\\frontend
python -m http.server 3000
```

### Linux/macOS (ou Manual no Windows)
```bash
# 1. Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# .\\venv\\Scripts\\Activate.ps1 # Windows

# 2. Instale as dependências
pip install -r api/requirements.txt

# 3. Baixe os modelos LLM (se ainda não tiver)
./scripts/pull-models.sh

# 4. Inicie a API
cd api
uvicorn app:app --reload

# 5. Em um NOVO terminal, inicie o Frontend
cd frontend
python3 -m http.server 3000
```

---

## 🌐 ACESSOS

- **Interface Web**: http://localhost:3000
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

---

## 🤖 AGENTES DISPONÍVEIS

### 1. **Ideator** 💡
**Uso**: Ideação de SaaS, análise de mercado, MVPs  
**Modelo**: qwen2.5:7b  
**Exemplo**:
```json
POST /chat
{
  "agent": "ideator",
  "message": "Preciso de uma ideia inovadora para SaaS de gestão"
}
```

### 2. **Architect** 🏗️
**Uso**: Arquitetura de sistemas, tech stack  
**Modelo**: llama3.1:8b-instruct  
**Exemplo**:
```json
POST /chat
{
  "agent": "architect",
  "message": "Design uma arquitetura para e-commerce escalável"
}
```

### 3. **Builder** 🛠️
**Uso**: Scaffolding de projetos (React, FastAPI, Flutter...)  
**Modelo**: codegemma:7b  
**Exemplo**:
```json
POST /chat
{
  "agent": "builder",
  "message": "Crie um projeto React com TypeScript"
}
```

### 4. **DevFullstack** 💻
**Uso**: Desenvolvimento geral, código, debug  
**Modelo**: qwen2.5:7b  
**Exemplo**:
```json
POST /chat
{
  "agent": "dev_fullstack",
  "message": "Crie uma API REST com autenticação JWT"
}
```

### 5. **Reflexivo** 🧠
**Uso**: Análise, planejamento, otimização  
**Modelo**: phi3:3.8b  
**Exemplo**:
```json
POST /chat
{
  "agent": "reflexivo",
  "message": "Analise os prós e contras de microservices"
}
```

---

## 🧠 ROTEAMENTO AUTOMÁTICO

**O sistema escolhe o modelo automaticamente** baseado em:
- Complexidade da tarefa
- Tipo de tarefa
- Performance histórica

**Endpoints:**
- `GET /routing/stats` - Estatísticas
- `POST /routing/test` - Testar roteamento
- `GET /routing/examples` - Ver exemplos

---

## 💾 GERENCIAMENTO DE HISTÓRICO

**O sistema agora salva suas conversas no servidor.**

**Endpoints:**
- `GET /projects` - Lista seus projetos de conversa
- `POST /projects` - Cria um novo projeto
- `GET /history/{project_name}` - Carrega o histórico de um projeto

---

## 📊 RECURSOS IMPLEMENTADOS

✅ **Infraestrutura Local** (100%)
- Execução nativa com Python venv
- FastAPI + Ollama
- ChromaDB para RAG
- Persistência de histórico em arquivos

✅ **Agentes** (100%)
- 5 agentes especializados
- Sistema de roteamento inteligente

✅ **RAG** (100%)
- Ingestão de documentos
- Busca semântica
- Embeddings vetoriais

✅ **API** (100%)
- 20+ endpoints funcionais
- Health checks
- Documentação automática

---

## 🚧 PRÓXIMAS FEATURES

🔲 **Conversa por Voz** (Whisper + TTS)  
🔲 **Geração Visual** (Stable Diffusion)  
🔲 **Templates Expandidos**  
🔲 **Monitoramento Avançado**  
🔲 **Deploy em Cloud**  

---

## 🛠️ COMANDOS ÚTEIS

```powershell
# (No terminal da API) Para parar a API
Ctrl + C

# Verificar se o Ollama está rodando
curl http://localhost:11434

# Listar modelos baixados
ollama list
```

---

## 📚 DOCUMENTAÇÃO

- **README Completo**: [README.md](README.md)
- **Roadmap Detalhado**: [ROADMAP.md](ROADMAP.md)
- **Status do Projeto**: [STATUS.md](STATUS.md)

---

## 🆘 TROUBLESHOOTING

### Problema: Modelos não carregam
**Solução**:
```powershell
# Windows
.\\scripts\\pull-modelsv.2.ps1

# Linux/macOS
./scripts/pull-models.sh
```

### Problema: API não responde
**Solução**:
- Verifique se o `run_local.ps1` (ou `uvicorn`) está em execução sem erros.
- Certifique-se de que o Ollama está rodando.

### Problema: `ModuleNotFoundError`
**Solução**:
- Certifique-se de que seu ambiente virtual está ativado.
- Rode `pip install -r api/requirements.txt` novamente.

---

## 💡 EXEMPLOS DE USO

### Ideação de SaaS
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "ideator",
    "message": "Gere uma ideia de SaaS para gestão de equipes remotas"
  }'
```

### Arquitetura
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "architect",
    "message": "Design uma arquitetura microservices para streaming"
  }'
```

### Scaffolding
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "builder",
    "message": "Crie um projeto FastAPI com PostgreSQL"
  }'
```

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Baixe os modelos LLM (se necessário)
2. ✅ Inicie a API com `.\\run_local.ps1`
3. ✅ Inicie a interface com `python -m http.server 3000`
4. ✅ Acesse http://localhost:3000
5. ✅ Teste os agentes e o novo sistema de projetos
6. ✅ Explore a API em http://localhost:8000/docs

---

**🚀 Desenvolvido com o Manifesto "Escrita Sincerta" - Direto, Técnico, Honesto.**
