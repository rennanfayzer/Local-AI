from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import os
import logging
import json

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Classe base para todos os agentes do sistema"""
    
    def __init__(self, name: str, default_model: str, capabilities: List[str]):
        self.name = name
        self.default_model = default_model
        self.capabilities = capabilities
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Retorna o prompt de sistema específico do agente"""
        pass
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processa uma mensagem e retorna a resposta"""
        pass
    
    async def call_ollama(self, model: str, messages: List[Dict[str, str]]) -> str:
        """Faz chamada para o Ollama"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 4096  # Adicionado para limitar o tamanho do contexto
                }
            }
            
            # Log detalhado do payload que será enviado
            logger.debug(f"Enviando payload para Ollama (modelo: {model}):\n{json.dumps(payload, indent=2)}")

            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("message", {}).get("content", "")
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Erro HTTP ao chamar Ollama: {http_err.response.status_code} - {http_err.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erro ao chamar Ollama: {e}")
            raise
    
    async def process(self, message: str, messages: List[Dict[str, str]], model: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Método principal de processamento"""
        if not model:
            model = self.default_model
        
        # Adiciona o system prompt específico do agente
        system_message = {"role": "system", "content": self.get_system_prompt()}
        
        # Combina mensagens
        full_messages = [system_message] + messages[1:]  # Remove system original e adiciona o específico
        
        # Processa mensagem específica do agente
        agent_context = context or {}
        agent_context.update({"agent": self.name, "model": model})
        agent_response = await self.process_message(message, agent_context)
        
        if agent_response:
            return agent_response
        
        # Fallback para chamada direta do Ollama
        return await self.call_ollama(model, full_messages)
    
    def load_prompt_file(self, filename: str) -> str:
        """Carrega arquivo de prompt do diretório prompts"""
        try:
            from pathlib import Path
            prompt_path = Path("prompts") / filename
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")
            else:
                logger.warning(f"Arquivo de prompt não encontrado: {filename}")
                return ""
        except Exception as e:
            logger.error(f"Erro ao carregar prompt {filename}: {e}")
            return ""


class SimpleAgent(BaseAgent):
    """Agente simples para casos básicos"""
    
    def __init__(self, name: str, system_prompt: str, model: str = None):
        super().__init__(
            name=name,
            default_model=model or os.getenv("GENERAL_MODEL", "qwen2.5:7b"),
            capabilities=["chat", "basic_tasks"]
        )
        self._system_prompt = system_prompt
    
    def get_system_prompt(self) -> str:
        return self._system_prompt
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        # Para agentes simples, retorna None para usar o fluxo padrão
        return None


# Registry de agentes
AGENT_REGISTRY = {}

def register_agent(agent_class, name: str = None):
    """Decorator para registrar agentes"""
    if not name:
        name = agent_class.__name__.lower().replace("agent", "")
    
    AGENT_REGISTRY[name] = agent_class
    return agent_class

def get_agent(name: str) -> Optional[BaseAgent]:
    """Obtém agente por nome"""
    agent_class = AGENT_REGISTRY.get(name)
    if agent_class:
        return agent_class()
    return None

def list_agents() -> List[str]:
    """Lista nomes de agentes disponíveis"""
    return list(AGENT_REGISTRY.keys())

# Função legacy para compatibilidade
def run_agent(name: str, message: str, history: List[Dict[str, str]]):
    """Função legacy para rodar agentes"""
    agent = get_agent(name)
    if not agent:
        return {"error": f"agente '{name}' não encontrado"}
    
    # Converte para formato assíncrono
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(agent.process(message, history))
