import os
import logging
from typing import Dict, Any, List
from .base import BaseAgent, register_agent

logger = logging.getLogger(__name__)

@register_agent
class DevFullstackAgent(BaseAgent):
    """
    Agente especializado em desenvolvimento full-stack
    
    Capacidades:
    - Geração de código Python, JavaScript, TypeScript
    - Arquitetura de aplicações web
    - APIs REST e GraphQL  
    - Debugging e otimização
    - Testes unitários e integração
    - DevOps e deployment
    """
    
    def __init__(self):
        super().__init__(
            name="dev_fullstack",
            default_model=os.getenv("DEV_MODEL", "qwen2.5:7b"),
            capabilities=[
                "code_generation",
                "debugging", 
                "architecture",
                "testing",
                "api_design",
                "database_design",
                "deployment",
                "optimization"
            ]
        )
    
    def get_system_prompt(self) -> str:
        """Prompt especializado para desenvolvimento full-stack"""
        manifesto = self.load_prompt_file("manifesto_sincerta.md")
        
        return f"""Você é a 'chegada' - desenvolvedor full-stack sênior especializado em:

**STACK PRINCIPAL:**
- Backend: Python (FastAPI, Django, Flask), Node.js, PostgreSQL
- Frontend: React, Vue.js, TypeScript, HTML/CSS
- DevOps: Docker, Kubernetes, CI/CD, AWS/Azure
- Ferramentas: Git, pytest, Jest, Swagger

**MANIFESTO SINCERTA:**
{manifesto}

**FORMATO OBRIGATÓRIO:**
Contexto → Solução → Exemplo/Código → Checklist

**REGRAS TÉCNICAS:**
1. **CÓDIGO SEMPRE EM MARKDOWN**: Use ```<linguagem> para blocos de código.
2. Código pronto para produção (tipagem, testes, documentação)
3. Segurança por design (validação, sanitização, autenticação)
4. Performance otimizada (queries eficientes, cache, lazy loading)
5. Escalabilidade (microserviços, load balancing, async)
6. Monitoramento (logs estruturados, métricas, alertas)

**PADRÕES DE RESPOSTA:**
- Problemas ambíguos: assuma requisitos sensatos e implemente
- Escolhas técnicas: justifique com trade-offs
- Código sempre com tipos, docstrings e tratamento de erros
- Incluir comandos de teste e validação

Seja técnico, direto e entregue soluções funcionais."""
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processamento específico para desenvolvimento"""
        
        # Identifica tipo de tarefa
        message_lower = message.lower()
        
        # Análise de código
        if any(keyword in message_lower for keyword in ["debug", "erro", "bug", "falha", "não funciona"]):
            return await self._handle_debugging(message, context)
        
        # Geração de código
        if any(keyword in message_lower for keyword in ["criar", "implementar", "gerar", "desenvolver", "código"]):
            return await self._handle_code_generation(message, context)
        
        # Arquitetura
        if any(keyword in message_lower for keyword in ["arquitetura", "estrutura", "design", "modelar"]):
            return await self._handle_architecture(message, context)
        
        # Review de código
        if any(keyword in message_lower for keyword in ["revisar", "analisar", "melhorar", "otimizar"]):
            return await self._handle_code_review(message, context)
        
        # Caso padrão - delega para Ollama
        return None
    
    async def _handle_debugging(self, message: str, context: Dict[str, Any]) -> str:
        """Processamento especializado para debugging"""
        debug_prompt = f"""
CONTEXTO: Debugging e resolução de problemas
TAREFA: {message}

METODOLOGIA DE DEBUG:
1. Identificar sintomas e reproduzir erro
2. Analisar logs e stack traces  
3. Isolar componente problemático
4. Propor fix com teste de validação

Forneça diagnóstico completo e solução testável.
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": debug_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_code_generation(self, message: str, context: Dict[str, Any]) -> str:
        """Processamento para geração de código"""
        code_prompt = f"""
CONTEXTO: Geração de código production-ready
TAREFA: {message}

REQUISITOS TÉCNICOS:
- Tipagem completa (Python: type hints, TS: strict mode)
- Tratamento de erros e validação de entrada
- Testes unitários incluídos
- Documentação (docstrings/JSDoc)
- Logs estruturados para debugging
- Segurança (input sanitization, SQL injection protection)

ENTREGA: Código completo + testes + instruções de uso
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": code_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_architecture(self, message: str, context: Dict[str, Any]) -> str:
        """Processamento para questões de arquitetura"""
        arch_prompt = f"""
CONTEXTO: Design de arquitetura de software
TAREFA: {message}

CONSIDERAÇÕES ARQUITETURAIS:
- Escalabilidade horizontal e vertical
- Separação de responsabilidades (SoC)
- Padrões: MVC, Repository, Factory, Observer
- Microserviços vs Monolito (trade-offs)
- Database design (normalização, índices, sharding)
- Caching strategy (Redis, CDN, browser cache)
- Security (OAuth, RBAC, encryption)
- Monitoring (APM, logs, metrics, alerts)

ENTREGA: Diagrama conceitual + decisões técnicas justificadas + implementação inicial
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": arch_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_code_review(self, message: str, context: Dict[str, Any]) -> str:
        """Processamento para review de código"""
        review_prompt = f"""
CONTEXTO: Code review e otimização
TAREFA: {message}

CHECKLIST DE REVIEW:
- [ ] Segurança: injection, XSS, CSRF, auth
- [ ] Performance: O(n) complexity, DB queries, memory leaks
- [ ] Manutenibilidade: DRY, SOLID, clean code
- [ ] Testabilidade: cobertura, mocks, integration tests
- [ ] Documentação: README, API docs, inline comments
- [ ] Standards: linting, formatting, naming conventions

ENTREGA: Análise detalhada + refactor sugerido + justificativas técnicas
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": review_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)


# Função legacy para compatibilidade
def agent(message: str, history: List[Dict[str, str]]):
    """Função legacy - usar DevFullstackAgent() diretamente"""
    import asyncio
    
    agent_instance = DevFullstackAgent()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(
        agent_instance.process(message, history)
    )
    
    return {"reply": result}
