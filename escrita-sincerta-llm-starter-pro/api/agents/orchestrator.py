import os
import json
import logging
from typing import Dict, Any, List
from .base import BaseAgent, register_agent

logger = logging.getLogger(__name__)

@register_agent
class OrchestratorAgent(BaseAgent):
    """
    Agente Orquestrador que analisa objetivos complexos, cria um plano de ação
    e delega tarefas para outros agentes especializados.
    """
    
    def __init__(self):
        super().__init__(
            name="orchestrator",
            default_model=os.getenv("ORCHESTRATOR_MODEL", "llama3.1:8b-instruct"), # Requer um modelo mais poderoso
            capabilities=["planning", "delegation", "workflow_management"]
        )
        # No futuro, isso poderia ser carregado dinamicamente
        self.available_agents = ["builder_web", "editor", "researcher", "dev_fullstack"]

    def get_system_prompt(self) -> str:
        """Prompt especializado para planejamento e orquestração."""
        return f"""
Você é o "Maestro", um Agente Orquestrador de IA. Sua função é atuar como um gerente de projetos de software autônomo.

**SUA MISSÃO:**
Receber um objetivo abstrato do usuário e transformá-lo em um plano de ação concreto, passo a passo, que pode ser executado por outros agentes de IA.

**AGENTES DISPONÍVEIS PARA DELEGAÇÃO:**
- **builder_web**: Para criar a estrutura inicial de um projeto completo (múltiplos arquivos).
- **editor**: Para modificar um arquivo de código existente em um projeto.
- **researcher**: Para buscar informações na web (ex: "qual a melhor biblioteca para gráficos em React?").
- **dev_fullstack**: Para criar ou refatorar trechos de código ou um único arquivo.

**PROCESSO DE ORQUESTRAÇÃO:**

1.  **Analisar o Objetivo**: Decomponha a solicitação do usuário em tarefas menores e lógicas.
2.  **Criar o Plano**: Gere um plano de ação em formato JSON. Cada passo do plano deve ser uma chamada para um dos agentes disponíveis.
3.  **Formato do Plano**: O JSON deve ser uma lista de objetos, onde cada objeto representa uma tarefa com "agent", "action" (uma descrição clara da tarefa) e "details" (parâmetros específicos como nome do projeto ou arquivo).

**EXEMPLO DE PLANO JSON:**

Se o usuário pedir: "Crie um app React simples e depois adicione um botão azul no componente principal."

Seu output DEVE ser o seguinte JSON:
```json
{{
  "plan": [
    {{
      "step": 1,
      "agent": "builder_web",
      "action": "Criar a estrutura inicial de um projeto React com TypeScript e Vite.",
      "details": {{
        "prompt": "Crie um app React simples com TypeScript e Vite chamado 'meu-app-react'"
      }}
    }},
    {{
      "step": 2,
      "agent": "editor",
      "action": "Modificar o componente principal para adicionar um botão azul.",
      "details": {{
        "prompt": "No projeto 'meu-app-react', modifique o arquivo 'src/App.jsx' para adicionar um botão azul com o texto 'Clique Aqui'."
      }}
    }}
  ]
}}
```

**REGRAS CRÍTICAS:**
-   Sua única saída DEVE ser o JSON do plano. Não adicione nenhuma outra explicação ou texto.
-   Escolha o agente mais apropriado para cada tarefa.
-   As tarefas devem ser sequenciais e lógicas.
"""

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Gera o plano de ação em JSON. A execução real será feita pela camada da API.
        """
        logger.info(f"Agente Orquestrador criando plano para: {message}")

        # O Orquestrador apenas cria o plano. A execução é responsabilidade do chamador.
        plan_prompt = f"""
Crie um plano de ação em JSON para a seguinte solicitação do usuário:

"{message}"
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": plan_prompt}
        ]
        
        response = await self.call_ollama(self.default_model, messages)
        
        # Extrai e valida o JSON da resposta
        try:
            json_block = response[response.find('{'):response.rfind('}')+1]
            plan = json.loads(json_block)
            if "plan" in plan and isinstance(plan["plan"], list):
                logger.info(f"Plano gerado com sucesso com {len(plan['plan'])} passos.")
                # Retorna o JSON como uma string para ser processado pela API
                return json.dumps(plan)
            else:
                raise ValueError("O JSON não contém a chave 'plan' ou não é uma lista.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Falha ao gerar ou validar o plano JSON: {e}")
            logger.debug(f"Resposta recebida do LLM: {response}")
            return json.dumps({"error": "Não foi possível criar um plano de ação válido.", "details": str(e)})
