# Escrita Sincerta LLM

**Escrita Sincerta LLM** é um projeto de código aberto para executar um Large Language Model (LLM) localmente, com uma interface web, agentes dedicados e memória vetorial persistente. O projeto é projetado para ser 100% offline, garantindo privacidade e controle total sobre seus dados.

## ✨ Features

- **Execução Local de LLM**: Rode modelos de linguagem de ponta em sua própria máquina, sem depender de serviços em nuvem.
- **Interface Web Intuitiva**: Interaja com o LLM através de uma interface web amigável, baseada no Open WebUI.
- **Memória Vetorial Persistente**: Armazene e recupere informações de conversas anteriores, permitindo que o LLM aprenda e evolua com o tempo.
- **Agentes Dedicados**: Utilize agentes especializados para tarefas específicas, como desenvolvimento full-stack e escrita reflexiva.
- **Suporte a Múltiplos Modelos**: Alterne facilmente entre diferentes modelos de LLM, como `phi3`, `qwen2.5`, e `gpt-oss-20b`.
- **Ingestão de Documentos**: Enriqueça o conhecimento do LLM com seus próprios documentos, através de um sistema de RAG (Retrieval-Augmented Generation).

## 🛠️ Stack de Tecnologia

- **Ollama**: Orquestrador para execução local de LLMs.
- **Open WebUI**: Interface web para interação com o LLM.
- **Postgres + pgvector**: Banco de dados para armazenamento e busca de vetores.
- **FastAPI**: API Python para orquestração dos serviços.
- **Docker**: Containerização para facilitar a instalação e o deploy.

## 🚀 Começando

Para começar a usar o Escrita Sincerta LLM, siga os passos abaixo:

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/escrita-sincerta-llm.git
   cd escrita-sincerta-llm
   ```

2. **Configure o ambiente:**

   Copie o arquivo `.env.example` para `.env` e ajuste as variáveis de ambiente conforme necessário.

   ```bash
   cp .env.example .env
   ```

3. **Inicie os serviços:**

   Use o Docker Compose para iniciar todos os serviços.

   ```bash
   docker-compose up -d --build
   ```

4. **Baixe os modelos:**

   Execute o comando `make pull` para baixar os modelos de LLM pré-configurados.

   ```bash
   make pull
   ```

## Uso

Após a inicialização, acesse a interface web em `http://localhost:3000`. Você pode começar a conversar com o LLM, experimentar os diferentes agentes e fazer o upload de seus próprios documentos para ingestão.

## 📂 Estrutura do Projeto

```
escrita-sincerta-llm/
 ├─ .env.example
 ├─ docker-compose.yml
 ├─ Makefile
 ├─ README.md
 ├─ data/
 │   ├─ docs/
 │   └─ vectors/
 ├─ api/
 │   ├─ app.py
 │   ├─ agents/
 │   ├─ tools/
 │   ├─ prompts/
 │   └─ settings.py
 └─ scripts/
     ├─ pull-models.sh
     ├─ dev.ps1
     └─ dev.sh
```

## 🔧 Solução de Problemas

- **Interface não responde**: Verifique se o serviço do Ollama está em execução com `curl localhost:11434/api/tags`.
- **Modelo falha ao carregar**: Verifique os logs do Ollama e ajuste a quantização do modelo, se necessário.
- **Erro 500 na API**: Verifique os logs da API com `docker compose logs -f api`.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).