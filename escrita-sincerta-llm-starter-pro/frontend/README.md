# 🎨 Frontend - Interface Web Chat

Interface visual tipo ChatGPT/Gemini para interagir com a API Escrita Sincerta.

## 🚀 Como Usar

### Método 1: Abrir Diretamente no Navegador
```powershell
# Opção A: Abrir com PowerShell
Start-Process "frontend\index.html"

# Opção B: Abrir com comando direto
.\frontend\index.html
```

### Método 2: Servidor HTTP Local (Recomendado)
```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Iniciar servidor HTTP simples
cd frontend
python -m http.server 3000

# Acessar: http://localhost:3000
```

## ✨ Funcionalidades

### 🤖 Seleção de Agentes
- **Auto (Recomendado)**: Roteamento inteligente automático
- **Ideator**: Geração de ideias SaaS
- **Architect**: Design de arquitetura de sistemas
- **Builder**: Scaffolding e estrutura de projetos
- **Dev Fullstack**: Código completo e implementação
- **Reflexivo**: Análise profunda e revisão

### 💬 Interface de Chat
- Design moderno inspirado em ChatGPT/Gemini
- Mensagens com avatares e timestamps
- Indicadores de modelo usado e tempo de resposta
- Animações suaves
- Scroll automático
- Loading indicators

### 🎯 Sugestões Rápidas
Clique nas sugestões prontas para começar:
- 💡 Ideia de SaaS
- 🏗️ Arquitetura de sistema
- 🧠 Análise de práticas
- 💻 Geração de código

### ⚡ Atalhos de Teclado
- **Enter**: Enviar mensagem
- **Shift+Enter**: Nova linha (futuro)

## 🔧 Requisitos

### Para funcionar, você precisa:
1. **API rodando**: `.\run_local.ps1`
2. **Navegador moderno**: Chrome, Firefox, Edge
3. **API na porta 8000**: http://localhost:8000

## 📊 Status da API

A interface verifica automaticamente se a API está rodando e exibe erros se não conseguir conectar.

### Se ver erro de conexão:
```powershell
# 1. Certifique-se que a API está rodando
.\run_local.ps1

# 2. Verifique o health check
Invoke-RestMethod -Uri http://localhost:8000/health

# 3. Recarregue o frontend (F5)
```

## 🎨 Personalização

### Cores do Tema
Edite as variáveis CSS em `index.html`:

```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cor dos botões */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Avatares
Substitua os emojis no JavaScript:

```javascript
avatar.textContent = type === 'user' ? '👤' : '🤖';
```

## 📱 Responsivo

A interface é 100% responsiva e funciona em:
- 💻 Desktop (recomendado)
- 📱 Tablet
- 📱 Mobile (vertical)

## 🐛 Troubleshooting

### Problema: "Não foi possível conectar à API"
**Solução**:
```powershell
# Verifique se a API está rodando
.\run_local.ps1

# Confirme na porta correta
netstat -ano | findstr :8000
```

### Problema: "CORS error"
**Solução**: A API já está configurada com CORS habilitado no `app.py`. Se ver esse erro, verifique se está usando o mesmo host (localhost vs 127.0.0.1).

### Problema: Interface não carrega
**Solução**:
```powershell
# Use um servidor HTTP local
cd frontend
python -m http.server 3000
# Acesse: http://localhost:3000
```

### Problema: Respostas lentas
**Possíveis causas**:
- Modelo Ollama pesado (troque para phi3:3.8b)
- Muitos processos rodando
- Primeira inferência (sempre mais lenta)

## 🚀 Próximas Melhorias

- [ ] Histórico de conversas (localStorage)
- [ ] Exportar chat para TXT/MD
- [ ] Upload de documentos via interface
- [ ] Suporte a markdown nas respostas
- [ ] Modo escuro/claro
- [ ] Streaming de respostas (Server-Sent Events)
- [ ] Copy-to-clipboard para código
- [ ] Syntax highlighting para code blocks

## 📄 Arquitetura

```
frontend/
├── index.html          # Arquivo único (HTML + CSS + JS)
└── README.md           # Esta documentação

Comunicação:
┌─────────────┐         HTTP/JSON          ┌─────────────┐
│   Browser   │  ←→  localhost:8000  ←→   │  FastAPI    │
│ (Frontend)  │                            │  (Backend)  │
└─────────────┘                            └─────────────┘
```

## 🎯 Vantagens vs Docker Open WebUI

| Característica | Frontend Local | Open WebUI (Docker) |
|----------------|----------------|---------------------|
| **Tamanho** | ~25KB | ~300MB |
| **Inicialização** | Instantâneo | ~10-15s |
| **Customização** | Total | Limitada |
| **Dependências** | Nenhuma | Docker |
| **Manutenção** | Simples | Complexa |
| **Visual** | Customizável | Fixo |

## 💡 Dicas de Uso

1. **Deixe no modo Auto**: O roteamento inteligente escolhe o melhor agente
2. **Use sugestões**: Clique nos cards de exemplo para começar rápido
3. **Teste diferentes agentes**: Cada um tem especialidade
4. **Monitore o tempo**: Respostas aparecem com tempo de geração
5. **Veja o modelo usado**: Badge mostra qual modelo Ollama respondeu

## 📞 Suporte

Se encontrar problemas:
1. Verifique se a API está rodando: `.\run_local.ps1`
2. Teste o health check: http://localhost:8000/health
3. Veja os logs da API no terminal
4. Abra o DevTools do navegador (F12) para erros JS

---

**Criado**: 12/10/2025  
**Versão**: 1.0.0  
**Compatível com**: API v2.0.2+
