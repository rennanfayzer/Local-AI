# 📜 CHANGELOG - Escrita Sincerta LLM Pro

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 2025-10-16 (Em Desenvolvimento)

### ✨ Adicionado

#### **Revolução da IA: Agente Orquestrador Autônomo**
- **Agente Orquestrador**: Criado um novo "cérebro" (`orchestrator.py`) que analisa objetivos complexos e os quebra em planos de ação executáveis por outros agentes.
- **Execução de Planos**: Implementado o endpoint `POST /execute_task` e a lógica no frontend para permitir a execução passo a passo de planos gerados pelo Orquestrador.
- **Modo "Auto" Inteligente**: O modo "Auto" agora é controlado pelo Orquestrador, permitindo que a IA trabalhe de forma autônoma para atingir objetivos complexos.

#### **Novos Agentes Especializados**
- **Agente Editor**: Um novo agente (`editor.py`) capaz de ler, analisar e modificar arquivos de código existentes em projetos gerados.
- **Agente Pesquisador**: Um novo agente (`researcher.py`) que pode buscar informações atualizadas na web usando a biblioteca `duckduckgo-search`.

#### **Melhorias de Gerenciamento**
- **Deletar Projetos**: Adicionada a funcionalidade de deletar projetos de conversa, tanto no backend (`DELETE /projects/{name}`) quanto na interface.
- **Integração com VS Code**: Projetos criados pelo Agente Builder agora incluem um botão "Abrir no VS Code" (`vscode://` link) para acesso rápido.

### 🚀 **Reinvenção Completa do Frontend**
- **Nova Stack**: O frontend foi completamente reconstruído do zero usando **Next.js, React, TypeScript e Tailwind CSS**.
- **Design Moderno**: Implementado um novo layout profissional, responsivo e com tema escuro.
- **Componentização**: A interface agora é baseada em componentes React (`Sidebar`, `ChatView`), facilitando a manutenção e expansão.
- **Qualidade de Desenvolvimento**: Resolvidos problemas de configuração do Tailwind CSS no VS Code com a adição da extensão recomendada e configurações de associação de arquivos.

### 🔄 Modificado
- **API Refatorada**: A lógica de chamada de agentes em `app.py` foi centralizada na função `execute_agent_task` para permitir que o Orquestrador delegue tarefas de forma limpa.
- **Agente Builder Aprimorado**: O `BuilderAgent` agora usa um modelo mais capaz (`codegemma:7b`) e tem uma lógica mais robusta para gerar projetos completos no disco.

---

## [2.0.3] - 2025-10-15

### ✨ Adicionado

#### Sistema de Histórico de Conversas Persistente
- **Gerenciamento de Projetos**: Agora é possível criar múltiplos "projetos", onde cada um armazena um histórico de conversa separado.
- **Persistência no Backend**: As conversas são salvas em arquivos JSON no servidor, dentro de `data/conversations/{nome_do_projeto}/history.json`. Isso garante que o histórico não seja perdido ao fechar o navegador.
- **Lógica de Gerenciamento**: Criado um novo módulo `api/tools/history.py` para encapsular toda a lógica de criação de projetos e manipulação de arquivos de histórico.

#### Novos Endpoints de API
- `GET /projects`: Lista todos os projetos de conversa existentes.
- `POST /projects`: Cria um novo projeto de conversa.
- `GET /history/{project_name}`: Carrega o histórico de um projeto específico.
- `POST /history/{project_name}`: Salva o histórico de um projeto específico.

### 🔄 Modificado

#### Interface do Frontend (`index.html`)
- Adicionado um seletor de projetos para carregar e alternar entre diferentes históricos de conversa.
- Adicionado um botão "Novo Projeto" para criar novos contextos de conversa.
- A interface agora se comunica com os novos endpoints da API para carregar e salvar o histórico, em vez de usar o `localStorage` do navegador.

#### API Principal (`app.py`)
- O endpoint `/chat` foi atualizado para receber o histórico de conversa do backend, permitindo um contexto muito maior e mais persistente.
- Integrados os novos endpoints de gerenciamento de projetos e histórico.

### 🎯 Benefícios
- **Persistência Real**: O histórico de conversas agora é salvo no servidor, permitindo continuar o trabalho entre diferentes sessões ou até mesmo dispositivos.
- **Organização**: A separação por projetos permite manter contextos diferentes para tarefas distintas (ex: um projeto para "API de E-commerce" e outro para "App Mobile").
- **Escalabilidade do Contexto**: Remove a limitação de contexto que existia ao depender apenas do histórico da sessão atual.

---

## [2.0.2] - 2025-10-12

### 🚀 Migração para Execução Local (Sem Docker)

Transição completa de Docker para execução nativa com Python venv para melhor performance e economia de espaço.

### ✨ Adicionado

#### Ambiente Virtual Python
- **venv** configurado com Python 3.13.7
- Instalação completa de dependências via pip
- Arquivo `.env.local` com configuração para execução local
- Script automatizado `run_local.ps1` para inicialização rápida

#### Documentação Local
- **README_LOCAL.md** - Guia completo de execução local
  - Instruções de instalação e execução
  - Diferenças entre Docker e local
  - Troubleshooting específico
  - Comandos de teste
  - Métricas de performance

#### Scripts de Automação
- **run_local.ps1** - Script PowerShell para execução local
  - Ativação automática do venv
  - Criação de diretórios necessários
  - Verificação de pré-requisitos (Ollama)
  - Inicialização da API com hot-reload
  - Interface amigável com cores e feedback

#### Configuração
- **`.gitignore`** atualizado
  - venv/ ignorado
  - .env e .env.local ignorados
  - Logs e dados locais ignorados

### 🗑️ Removido

#### Infraestrutura Docker Completa
- Todos os containers do projeto parados
- Imagem API removida (11.8GB liberados)
- Volumes removidos:
  - `postgres_data`
  - `redis_data`
  - `ollama_models`
  - `openwebui_data`
  - `api_logs`
- Cache de build limpo
- **Total de espaço liberado: ~19.25GB**

#### Serviços Externos
- PostgreSQL (substituído por armazenamento local)
- Redis (substituído por cache em memória)
- Open WebUI (interface não essencial)

### 🔄 Modificado

#### Configuração da Aplicação
- `USE_POSTGRES=False` - Database desabilitado
- `USE_REDIS=False` - Cache em memória
- `CHROMA_PATH=./data/vectors` - ChromaDB local
- `DOCS_PATH=./data/docs` - Documentos locais

#### Dependências
- Todas as dependências mantidas (exceto as de voz já removidas)
- Instalação via pip diretamente no venv
- Sem overhead de containers

### 📊 Comparativo Docker vs Local

| Métrica | Docker | Local (venv) |
|---------|---------|--------------|
| **Espaço em disco** | ~19.25GB | ~500MB |
| **Tempo de inicialização** | ~30-60s | ~2-5s |
| **Consumo de RAM** | ~4-6GB | ~1-2GB |
| **Performance I/O** | Overhead de volumes | Nativo |
| **Hot-reload** | ~5-10s | ~1-2s |
| **Build time** | ~13 min | N/A |

### ✅ O que continua funcionando

- ✅ Todos os 5 agentes especializados
- ✅ Sistema de roteamento inteligente
- ✅ RAG com ChromaDB
- ✅ Integração com Ollama
- ✅ Upload e processamento de documentos
- ✅ API REST completa
- ✅ Documentação interativa (/docs)
- ✅ Hot-reload durante desenvolvimento

### 🎯 Benefícios da Migração

1. **Performance Superior**
   - Inicialização 10-15x mais rápida
   - Menor latência de I/O
   - Melhor utilização de recursos do sistema

2. **Economia de Recursos**
   - 19.25GB de espaço liberados
   - 50-70% menos RAM utilizada
   - CPU mais livre (sem overhead de containers)

3. **Desenvolvimento Mais Ágil**
   - Hot-reload instantâneo
   - Debug mais fácil
   - Logs mais acessíveis
   - Sem necessidade de rebuild

4. **Simplicidade**
   - Menos camadas de abstração
   - Configuração mais direta
   - Troubleshooting mais fácil
   - Menos dependências externas

### 📝 Notas de Migração

- O Docker ainda está instalado no sistema (apenas este projeto foi migrado)
- Outros projetos Docker permanecem intactos
- É possível retornar ao Docker se necessário
- Ollama continua necessário (pode rodar local ou Docker)

---

## [2.0.1] - 2025-10-12

### 🗑️ Removido

- **Sistema de Voz Completo** - Removido para economizar espaço em disco
  - Whisper (STT)
  - Coqui TTS (Text-to-Speech)
  - Endpoints `/voice/*`
  - Dependências: openai-whisper, TTS, pydub, soundfile, librosa, torch, torchaudio
  - Volumes Docker: voice_cache, voice_models
  - Bibliotecas do Dockerfile: ffmpeg, libsndfile1
  - **Espaço liberado**: ~8.2GB de cache Docker + volumes

### 🔄 Atualizado

- Versão da API: 2.1.0 → 2.0.0
- `requirements.txt` - Removidas 7 dependências de áudio
- `Dockerfile` - Removidas bibliotecas de áudio (ffmpeg, libsndfile1)
- `docker-compose.yml` - Removidos volumes de voz
- `app.py` - Sistema de voz desabilitado (`VOICE_ENABLED = False`)
- `README.md` - Removidas referências ao sistema de voz

---

## [2.1.0] - 2025-10-11 (REVERTIDO)

### 🎤 Sistema de Voz Completo (Whisper + TTS)

Adição de capacidades completas de processamento de voz, permitindo interação por áudio com os agentes.

### ✨ Adicionado

#### Sistema de Voz
- **VoiceProcessor** - Processador unificado de voz
  - OpenAI Whisper para Speech-to-Text (5 modelos disponíveis)
  - Coqui TTS para Text-to-Speech (português brasileiro)
  - Suporte a 99+ idiomas com auto-detecção
  - Múltiplos formatos de áudio (mp3, wav, ogg, m4a, flac, webm)
  - Lazy loading de modelos para otimização de recursos
  - Arquivo: `api/tools/voice.py` (450+ linhas)

#### Endpoints de Voz
- `POST /voice/transcribe` - Transcrição de áudio para texto
  - Upload de áudio em múltiplos formatos
  - Auto-detecção de idioma
  - Metadados detalhados (segmentos, duração)
  
- `POST /voice/synthesize` - Síntese de voz a partir de texto
  - Saída em WAV ou MP3
  - Vozes configuráveis
  - Qualidade ajustável
  
- `POST /voice/chat` - Conversa completa por voz
  - Transcrição → Agente → Síntese
  - Integração com todos os 5 agentes especializados
  - Processamento assíncrono
  
- `GET /voice/info` - Informações do sistema de voz
  - Status dos modelos carregados
  - Idiomas e formatos suportados
  - Device (CPU/GPU) utilizado
  
- `WS /voice/stream` - WebSocket para streaming em tempo real
  - Streaming bidirecional de áudio
  - Transcrição em tempo real
  - Base para conversação fluida

#### Documentação de Voz
- **VOICE.md** - Guia completo do sistema de voz (440+ linhas)
  - Quick start com exemplos
  - Casos de uso detalhados
  - Configuração avançada
  - Troubleshooting
  - Métricas de performance
  - Referências técnicas

#### Ferramentas e Testes
- **test_voice.py** - Suite de testes automatizados
  - Teste de carregamento de modelos
  - Teste de síntese (TTS)
  - Teste de transcrição (STT)
  - Teste de conversa por voz
  - Teste de endpoints HTTP
  - Geração de relatórios

- **voice_client.py** - Cliente de exemplo
  - Interface CLI para testar todos os endpoints
  - Modo interativo
  - Exemplos de uso em Python
  - Integração via requests

#### Dependências
- `openai-whisper==20231117` - Engine STT
- `TTS==0.22.0` - Engine Text-to-Speech
- `pydub==0.25.1` - Manipulação de áudio
- `soundfile==0.12.1` - I/O de áudio
- `librosa==0.10.1` - Processamento de áudio
- `torch==2.1.0` - Framework ML
- `torchaudio==2.1.0` - Áudio com PyTorch

### 🔄 Modificado

#### Docker
- **Dockerfile** atualizado com dependências de áudio
  - `ffmpeg` instalado para conversão de formatos
  - `libsndfile1` para manipulação de arquivos de áudio
  - Bibliotecas tanto em build quanto runtime stages

#### Docker Compose
- Volumes adicionados para cache de voz:
  - `voice_cache` - Cache temporário de processamento
  - `voice_models` - Persistência de modelos Whisper
- Volumes montados em `/tmp/voice_cache` e `/root/.cache/whisper`

#### API Principal
- `app.py` atualizado para v2.1.0
  - Import condicional das rotas de voz
  - Flag `VOICE_ENABLED` para verificar disponibilidade
  - Rotas de voz registradas automaticamente
  - Endpoints de voz listados em `/` quando disponíveis
  - Nova seção `capabilities` no root endpoint

#### README
- Seção de Sistema de Voz adicionada
  - Descrição das capacidades
  - Exemplos de uso rápido
  - Link para documentação completa (VOICE.md)
- Features principais atualizadas
  - "🎤 Sistema de Voz" destacado
  - Agentes atualizados para 5 especializados
- Características ampliadas com roteamento inteligente

### 📊 Estatísticas desta Versão
- **Arquivos Adicionados**: 4 (voice.py, voice_routes.py, test_voice.py, voice_client.py, VOICE.md)
- **Linhas de Código**: +1,500
- **Linhas de Documentação**: +500
- **Novos Endpoints**: 5 (4 REST + 1 WebSocket)
- **Dependências Adicionadas**: 7
- **Idiomas Suportados**: 99+
- **Formatos de Áudio**: 6

### 🎯 Casos de Uso Habilitados
- Assistente de voz para ideação de produtos
- Documentação por voz (transcrição de reuniões)
- Tutoriais em áudio (acessibilidade)
- Conversação natural com agentes especializados
- Interface hands-free para desenvolvimento

---

## [2.0.0] - 2025-10-11

### 🎉 Versão Maior - Sistema de Roteamento e Agentes Especializados

Esta é uma versão **MAJOR** com mudanças significativas na arquitetura e capacidades do sistema.

### ✨ Adicionado

#### Agentes Especializados
- **Ideator Agent** - Especialista em ideação de SaaS, análise de mercado e MVPs
  - Metodologias: Design Thinking, Lean Startup, Jobs-to-be-Done
  - Capacidades: Geração de ideias, análise de mercado, definição de MVPs, personas
  - Arquivo: `api/agents/ideator_saas.py` (350+ linhas)

- **Architect Agent** - Arquiteto de sistemas fullstack
  - Padrões: MVC, Microservices, Event-Driven, Serverless, Layered
  - Capacidades: Design de arquitetura, seleção de tech stack, database design, API design
  - Suporte a 15+ stacks pré-configurados
  - Arquivo: `api/agents/architect_fullstack.py` (400+ linhas)

- **Builder Agent** - Construtor de projetos multi-framework
  - Frameworks: React, FastAPI, Flutter, Vue.js, Node.js
  - Capacidades: Scaffolding completo, templates otimizados, setup de configurações
  - Arquivo: `api/agents/builder_web.py` (600+ linhas)

#### Sistema de Roteamento Inteligente
- **Advanced Router** - Sistema completo de roteamento automático
  - Análise de complexidade (Simple → Medium → Complex → Expert)
  - Detecção de tipo de tarefa (Ideation, Architecture, Coding, Debugging...)
  - Seleção otimizada de modelo baseada em score
  - Fallback automático quando modelo indisponível
  - Métricas de performance (success rate, response time)
  - Cache inteligente de decisões
  - Arquivo: `api/advanced_router.py` (700+ linhas)

#### Novos Endpoints de API
- `GET /routing/stats` - Estatísticas do sistema de roteamento
- `POST /routing/analyze` - Análise de roteamento sem execução
- `GET /routing/models` - Configurações dos modelos disponíveis
- `POST /routing/test` - Teste de roteamento com mensagens
- `POST /routing/benchmark` - Benchmark de performance dos modelos
- `GET /routing/examples` - Exemplos de uso do roteamento
- `GET /` - Endpoint raiz com informações da API

#### Documentação Completa
- **README.md** - Atualizado com novos agentes e roteamento
- **ROADMAP.md** - Roadmap completo com Gantt chart e estimativas
- **STATUS.md** - Status detalhado do projeto por categoria
- **QUICKSTART.md** - Guia de início rápido
- **RESUMO.md** - Resumo executivo para stakeholders
- **INDICE.md** - Índice navegável da documentação
- **CHANGELOG.md** - Este arquivo

#### Scripts
- `scripts/pull-modelsv2.ps1` - Script PowerShell corrigido para download de modelos
- Melhorias no tratamento de erros dos scripts

### 🔄 Modificado

#### API Principal
- Integração completa do sistema de roteamento em `app.py`
- Endpoint `/chat` agora usa roteamento inteligente automático
- Suporte a contexto expandido nas requisições
- Melhor tratamento de erros e fallbacks
- Metadata de roteamento incluída nas respostas

#### Endpoint `/agents`
- Atualizado para listar todos os 5 agentes
- Informações detalhadas de capacidades
- Modelos padrão configurados

#### Configuração de Modelos
- 4 modelos configurados com perfis completos:
  - `phi3:3.8b` - Tarefas simples (low resource)
  - `qwen2.5:7b` - Raciocínio técnico (medium)
  - `llama3.1:8b-instruct` - Expert/creative (high)
  - `codegemma:7b` - Especialista em código (technical)

### 🐛 Corrigido
- Erro de interpolação de variável em `pull-models.ps1`
- Tratamento de erros melhorado nos scripts PowerShell
- Fallback robusto quando modelos não disponíveis

### 📊 Estatísticas desta Versão
- **Arquivos Adicionados**: 10+
- **Linhas de Código**: +3,000
- **Linhas de Documentação**: +3,000
- **Novos Endpoints**: 7
- **Novos Agentes**: 3

---

## [1.0.0] - 2024-03-01

### 🎉 Lançamento Inicial

Primeira versão estável do sistema LLM local completo.

### ✨ Adicionado

#### Infraestrutura Base
- **Docker Compose** completo com 5 serviços:
  - FastAPI (API Orquestradora)
  - Ollama (Runtime de modelos LLM)
  - Open WebUI (Interface web)
  - PostgreSQL com pgvector (RAG)
  - Redis (Cache)

#### API REST
- FastAPI com 9 endpoints principais:
  - `GET /health` - Health check
  - `GET /models` - Lista modelos disponíveis
  - `GET /agents` - Lista agentes disponíveis
  - `POST /chat` - Chat com agentes
  - `POST /ingest` - Ingestão de documentos
  - `POST /query` - Query no RAG
  - `POST /upload` - Upload de arquivos
  - `GET /files` - Lista arquivos
  - `GET /docs` - Documentação Swagger

#### Agentes Base
- **DevFullstack Agent** - Desenvolvedor full-stack
  - Modelo: `qwen2.5:7b`
  - Capacidades: Code generation, debugging, architecture, testing

- **Reflexivo Agent** - Análise e planejamento
  - Modelo: `phi3:3.8b`
  - Capacidades: Analysis, planning, review, optimization

#### Sistema RAG
- Ingestão de documentos (Markdown, TXT, HTML)
- Embeddings vetoriais com pgvector
- Busca semântica com contexto
- Persistência em PostgreSQL

#### Ferramentas
- `api/tools/rag.py` - Sistema completo de RAG
- `api/tools/files.py` - Manipulação de arquivos
- `api/tools/sysinfo.py` - Informações do sistema

#### Scripts de Automação
- `Makefile` - Comandos universais
- `scripts/pull-models.sh` - Download de modelos (Linux/macOS)
- `scripts/dev.sh` - Toolkit completo Bash
- `scripts/dev.ps1` - Toolkit completo PowerShell

#### Documentação
- README.md completo
- Arquitetura detalhada
- Instruções de instalação
- Troubleshooting

#### Configuração
- Arquivo `.env` com variáveis de ambiente
- Health checks para todos os serviços
- Logs estruturados
- CORS configurado

### 📊 Estatísticas da Versão Inicial
- **Arquivos**: 15+
- **Linhas de Código**: ~2,000
- **Endpoints de API**: 9
- **Agentes**: 2
- **Serviços Docker**: 5

---

## [0.5.0] - 2024-02-15 (Beta)

### ✨ Adicionado
- Protótipo do sistema RAG
- Integração básica com Ollama
- Docker Compose inicial

---

## [0.1.0] - 2024-01-01 (Alpha)

### ✨ Adicionado
- Estrutura inicial do projeto
- FastAPI básica
- Primeiro agente de teste

---

## 🔮 Próximas Versões Planejadas

### [2.1.0] - Previsto para 2025-11
**Conversa por Voz**
- Whisper para Speech-to-Text
- Coqui TTS para Text-to-Speech
- WebSocket para streaming
- Multi-idioma (PT + EN)

### [2.2.0] - Previsto para 2025-12
**Geração Visual**
- Stable Diffusion XL
- Geração de wireframes
- Diagramas técnicos
- FFmpeg para vídeo

### [2.3.0] - Previsto para 2026-01
**Templates Expandidos**
- 6+ templates production-ready
- SaaS, E-commerce, Mobile, APIs, Dashboards
- Customização via CLI

### [3.0.0] - Previsto para 2026-03
**Produção e Deploy**
- Prometheus + Grafana
- Terraform IaC
- CI/CD completo
- Auth JWT + OAuth2
- Auto-scaling

### [4.0.0] - Previsto para 2026-06
**IA Avançada**
- Agentes colaborativos
- Executor de código seguro
- Multi-modal avançado
- Vision models

---

## 📝 Convenções de Versionamento

Este projeto usa [Versionamento Semântico](https://semver.org/):

- **MAJOR** (X.0.0): Mudanças incompatíveis na API
- **MINOR** (0.X.0): Novas funcionalidades compatíveis
- **PATCH** (0.0.X): Correções de bugs compatíveis

### Tipos de Mudanças

- **✨ Adicionado** - Novas funcionalidades
- **🔄 Modificado** - Mudanças em funcionalidades existentes
- **❌ Removido** - Funcionalidades removidas
- **🐛 Corrigido** - Correções de bugs
- **🔒 Segurança** - Vulnerabilidades corrigidas
- **⚠️ Depreciado** - Funcionalidades a serem removidas

---

## 🔗 Links

- **Repositório**: [GitHub](https://github.com/seu-usuario/escrita-sincerta-llm-pro)
- **Documentação**: [README.md](README.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/escrita-sincerta-llm-pro/issues)

---

**Última Atualização**: 11 de Outubro, 2025
