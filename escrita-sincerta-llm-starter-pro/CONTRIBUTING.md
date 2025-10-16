# 🤝 GUIA DE CONTRIBUIÇÃO

Obrigado por considerar contribuir para o **Escrita Sincerta LLM Pro**!

Este documento fornece diretrizes para contribuir com o projeto.

---

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Documentação](#documentação)

---

## 📜 Código de Conduta

Este projeto adere ao **Manifesto "Escrita Sincerta"**: comunicação direta, técnica e honesta.

### Princípios
- ✅ Seja respeitoso e profissional
- ✅ Foque em soluções técnicas
- ✅ Critique ideias, não pessoas
- ✅ Seja direto e objetivo
- ✅ Admita quando não souber algo

---

## 🚀 Como Posso Contribuir?

### 1. Reportar Bugs 🐛

**Antes de reportar:**
- Verifique se o bug já foi reportado nas [Issues](https://github.com/seu-usuario/escrita-sincerta-llm-pro/issues)
- Teste com a versão mais recente

**Ao reportar, inclua:**
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Ambiente (OS, versões, etc.)

**Template:**
```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Execute '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Ambiente**
- OS: [Windows 11, Ubuntu 22.04, etc.]
- Docker: [versão]
- Python: [versão]
- Modelos LLM: [quais]

**Logs**
```
Colar logs relevantes aqui
```
```

### 2. Sugerir Features ✨

**Antes de sugerir:**
- Verifique o [ROADMAP.md](ROADMAP.md)
- Procure por sugestões similares

**Ao sugerir, inclua:**
- Problema que a feature resolve
- Solução proposta
- Alternativas consideradas
- Complexidade estimada
- Casos de uso

**Template:**
```markdown
**Problema**
Descrição do problema que a feature resolve.

**Solução Proposta**
Como a feature funcionaria.

**Alternativas**
Outras abordagens consideradas.

**Casos de Uso**
1. Caso 1
2. Caso 2

**Complexidade Estimada**
Baixa / Média / Alta
```

### 3. Contribuir com Código 💻

#### Tipos de Contribuição
- 🐛 Correção de bugs
- ✨ Novas features
- 📚 Melhorias na documentação
- 🎨 Melhorias de UI/UX
- ⚡ Otimizações de performance
- 🧪 Adicionar testes

---

## 🔄 Processo de Desenvolvimento

### 1. Fork e Clone

```bash
# Fork no GitHub, depois:
git clone https://github.com/SEU-USUARIO/escrita-sincerta-llm-pro.git
cd escrita-sincerta-llm-pro
```

### 2. Crie uma Branch

Use nomes descritivos:

```bash
# Features
git checkout -b feature/nome-da-feature

# Bugs
git checkout -b fix/descricao-do-bug

# Documentação
git checkout -b docs/melhoria-docs
```

**Convenção de Nomes:**
- `feature/` - Novas funcionalidades
- `fix/` - Correções de bugs
- `docs/` - Documentação
- `refactor/` - Refatorações
- `test/` - Testes
- `perf/` - Performance

### 3. Desenvolva

```bash
# Instale dependências
pip install -r api/requirements.txt

# Execute o ambiente de desenvolvimento
docker-compose up -d

# Faça suas alterações
# ...

# Teste localmente
docker-compose logs -f
```

### 4. Commit

Use mensagens de commit claras e descritivas:

```bash
git add .
git commit -m "feat: adiciona agente de tradução automática"
```

**Convenção de Commits (Conventional Commits):**
- `feat:` - Nova feature
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação (não afeta código)
- `refactor:` - Refatoração
- `test:` - Testes
- `chore:` - Manutenção

**Exemplos:**
```bash
feat: adiciona suporte a multi-idioma no Ideator Agent
fix: corrige erro de roteamento quando modelo indisponível
docs: atualiza README com novos endpoints
refactor: simplifica lógica de seleção de modelo
test: adiciona testes para advanced_router
```

### 5. Push e Pull Request

```bash
# Push para seu fork
git push origin feature/nome-da-feature

# Crie Pull Request no GitHub
```

**Template de Pull Request:**
```markdown
## Descrição
Descrição clara das mudanças.

## Tipo de Mudança
- [ ] Bug fix (non-breaking change)
- [ ] Nova feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Comentários adicionados onde necessário
- [ ] Documentação atualizada
- [ ] Testes passando
- [ ] Sem novos warnings
```

---

## 📝 Padrões de Código

### Python

#### Estilo
- Seguir **PEP 8**
- Usar **type hints**
- Máximo 100 caracteres por linha
- Docstrings para funções e classes

**Exemplo:**
```python
from typing import Dict, List, Optional

def process_message(
    message: str, 
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Processa uma mensagem com contexto opcional.
    
    Args:
        message: Mensagem a ser processada
        context: Contexto adicional opcional
        
    Returns:
        Mensagem processada
        
    Raises:
        ValueError: Se mensagem estiver vazia
    """
    if not message:
        raise ValueError("Mensagem não pode estar vazia")
    
    # Implementação...
    return processed_message
```

#### Imports
Ordem dos imports:
1. Biblioteca padrão
2. Bibliotecas de terceiros
3. Imports locais

```python
# Biblioteca padrão
import os
import json
from typing import Dict, List

# Terceiros
import aiohttp
from fastapi import FastAPI

# Locais
from .agents.base import BaseAgent
from .tools.rag import query_vectors
```

#### Nomes
- **Classes**: `PascalCase` (ex: `AdvancedRouter`)
- **Funções/Métodos**: `snake_case` (ex: `process_message`)
- **Constantes**: `UPPER_CASE` (ex: `MAX_RETRIES`)
- **Variáveis**: `snake_case` (ex: `user_message`)

### Agentes

#### Estrutura de um Agente
```python
from typing import List, Dict, Any
from .base import BaseAgent

class MeuAgente(BaseAgent):
    """
    Descrição do propósito do agente.
    
    Capacidades:
    - Capacidade 1
    - Capacidade 2
    """
    
    def __init__(self):
        super().__init__()
        self.name = "meu_agente"
        self.description = "Descrição breve"
    
    def get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para este agente"""
        return """
        Você é um agente especializado em...
        
        Suas responsabilidades:
        1. Responsabilidade 1
        2. Responsabilidade 2
        """
    
    async def process(
        self, 
        message: str, 
        messages: List[Dict[str, str]], 
        model: str
    ) -> str:
        """
        Processa uma mensagem.
        
        Args:
            message: Mensagem do usuário
            messages: Histórico completo
            model: Modelo LLM a usar
            
        Returns:
            Resposta do agente
        """
        # Implementação específica
        pass
```

### Testes

```python
import pytest
from api.advanced_router import AdvancedRouter

def test_router_selects_correct_model():
    """Testa se o router seleciona o modelo correto"""
    router = AdvancedRouter()
    
    # Teste com tarefa simples
    message = "Olá, como você está?"
    model, info = await router.route_request(message)
    
    assert model == "phi3:3.8b"
    assert info["task_complexity"] == "simple"

def test_router_handles_complex_task():
    """Testa roteamento de tarefa complexa"""
    router = AdvancedRouter()
    
    message = "Design uma arquitetura microservices enterprise"
    model, info = await router.route_request(message)
    
    assert model in ["llama3.1:8b-instruct", "qwen2.5:7b"]
    assert info["task_complexity"] in ["complex", "expert"]
```

---

## 🏗️ Estrutura do Projeto

```
escrita-sincerta-llm-starter-pro/
├── api/                        # Código da API
│   ├── agents/                # Agentes especializados
│   │   ├── base.py           # Classe base
│   │   ├── ideator_saas.py   # Ideator
│   │   ├── architect_fullstack.py  # Architect
│   │   ├── builder_web.py    # Builder
│   │   ├── dev_fullstack.py  # Dev
│   │   └── reflexivo.py      # Reflexivo
│   ├── tools/                 # Ferramentas auxiliares
│   │   ├── rag.py            # Sistema RAG
│   │   ├── files.py          # Manipulação arquivos
│   │   └── sysinfo.py        # Info do sistema
│   ├── prompts/              # Prompts e estilos
│   │   ├── manifesto_sincerta.md
│   │   ├── system_base.md
│   │   └── styles.json
│   ├── app.py                # API principal
│   ├── advanced_router.py    # Roteamento
│   ├── router.py             # Router básico
│   └── requirements.txt      # Dependências
├── data/                      # Dados
│   ├── docs/                 # Documentos para RAG
│   └── vectors/              # Vetores persistentes
├── scripts/                   # Scripts de automação
│   ├── pull-modelsv2.ps1    # Windows
│   └── pull-models.sh       # Linux/macOS
├── tests/                     # Testes (criar)
├── docs/                      # Documentação adicional
├── docker-compose.yml        # Orquestração
├── Makefile                  # Comandos
├── README.md                 # Docs principal
├── ROADMAP.md               # Roadmap
├── STATUS.md                # Status
├── CHANGELOG.md             # Histórico
└── CONTRIBUTING.md          # Este arquivo
```

---

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_router.py

# Com cobertura
pytest --cov=api tests/
```

### Escrever Testes

- Teste cada função pública
- Use fixtures para setup/teardown
- Nomes descritivos: `test_<funcao>_<cenario>_<resultado>`
- Organize em `tests/` espelhando estrutura de `api/`

---

## 📚 Documentação

### Quando Atualizar

- ✅ Ao adicionar nova feature
- ✅ Ao mudar comportamento existente
- ✅ Ao adicionar novo endpoint
- ✅ Ao criar novo agente

### Arquivos a Atualizar

1. **README.md** - Overview e referência
2. **ROADMAP.md** - Se feature estava planejada
3. **STATUS.md** - Marcar como implementado
4. **CHANGELOG.md** - Registrar mudança
5. **Docstrings** - Documentar código

### Estilo de Documentação

- Markdown para docs
- Docstrings para código Python
- Exemplos práticos
- Links internos para navegação

---

## 🎯 Áreas Que Precisam de Contribuição

### Alta Prioridade
- 🎤 Conversa por Voz (Whisper + TTS)
- 🎨 Geração Visual (Stable Diffusion)
- 📦 Templates expandidos
- 🧪 Testes automatizados

### Média Prioridade
- 📊 Monitoramento (Prometheus/Grafana)
- 🚀 Deploy em cloud
- 🔐 Segurança e auth

### Documentação
- 📖 Tutoriais detalhados
- 🎥 Vídeos explicativos
- 🌍 Traduções
- 📝 Exemplos de uso

---

## ❓ Dúvidas?

- 💬 Abra uma [Discussion](https://github.com/seu-usuario/escrita-sincerta-llm-pro/discussions)
- 🐛 Reporte um [Issue](https://github.com/seu-usuario/escrita-sincerta-llm-pro/issues)
- 📧 Entre em contato: [seu-email@exemplo.com]

---

## 🏆 Reconhecimento

Todos os contribuidores são reconhecidos no README.md e releases.

---

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

---

**Obrigado por contribuir! 🚀**

**Desenvolvido com o Manifesto "Escrita Sincerta" - Direto, Técnico, Honesto.**
