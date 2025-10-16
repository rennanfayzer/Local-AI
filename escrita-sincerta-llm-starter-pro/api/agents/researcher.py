import os
import json
import logging
from typing import Dict, Any, List
from .base import BaseAgent, register_agent
from tools.web_search import search_web  # Assumindo que teremos uma ferramenta de busca

logger = logging.getLogger(__name__)

@register_agent
class ResearcherAgent(BaseAgent):
    """
    Agente especializado em buscar informações atualizadas na internet.
    """
    
    def __init__(self):
        super().__init__(
            name="researcher",
            default_model=os.getenv("RESEARCHER_MODEL", "qwen2.5:7b"),
            capabilities=["web_search", "information_retrieval", "summarization"]
        )

    def get_system_prompt(self) -> str:
        """Prompt especializado para pesquisa na web."""
        return """
Você é um Agente de Pesquisa de IA. Sua missão é encontrar as informações mais relevantes e atualizadas na internet para responder às perguntas do usuário.

**PROCESSO DE PESQUISA:**

1.  **Analisar a Pergunta**: Identifique as palavras-chave e a intenção principal da pergunta do usuário.
2.  **Formular a Query**: Crie uma query de busca concisa e eficaz.
3.  **Executar a Busca**: Use a ferramenta de busca na web para obter os resultados.
4.  **Analisar os Resultados**: Leia e compreenda o conteúdo das páginas encontradas.
5.  **Sintetizar a Resposta**: Combine as informações de múltiplas fontes para criar uma resposta completa, precisa e fácil de entender.

**REGRAS:**

-   **Cite suas Fontes**: Sempre inclua os links das fontes que você usou no final da sua resposta.
-   **Seja Objetivo**: Apresente os fatos e dados encontrados.
-   **Indique a Data**: Se a informação for sensível ao tempo (notícias, versões de software), mencione a data da informação.
-   **Se não encontrar, admita**: Se não conseguir encontrar uma resposta confiável, informe ao usuário que a busca não retornou resultados claros.
"""

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Orquestra o processo de pesquisa na web.
        """
        logger.info(f"Agente Pesquisador recebendo a pergunta: {message}")

        # Etapa 1: Pedir ao LLM para formular uma query de busca
        query_formulation_prompt = f"""
Baseado na pergunta do usuário, qual seria a melhor e mais curta query de busca para o Google?
Responda apenas com a query.

Pergunta: "{message}"
Query de Busca:"""
        
        messages = [{"role": "user", "content": query_formulation_prompt}]
        search_query = await self.call_ollama(self.default_model, messages)
        search_query = search_query.strip().strip('"')
        
        logger.info(f"Query de busca formulada: {search_query}")

        # Etapa 2: Executar a busca na web
        try:
            search_results = await search_web(search_query)
            if not search_results:
                return "Desculpe, a busca na web não retornou nenhum resultado para essa consulta."
        except Exception as e:
            logger.error(f"Erro ao executar a busca na web: {e}")
            return f"Ocorreu um erro ao tentar acessar a internet: {e}"

        # Etapa 3: Pedir ao LLM para sintetizar os resultados
        synthesis_prompt = f"""
**Pergunta Original do Usuário:**
"{message}"

**Resultados da Busca na Web:**
```json
{json.dumps(search_results, indent=2, ensure_ascii=False)}
```

**Sua Tarefa:**
Com base nos resultados da busca, escreva uma resposta completa e bem estruturada para a pergunta original do usuário.
Lembre-se de citar as fontes (links) no final da sua resposta.
"""
        
        synthesis_messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        final_response = await self.call_ollama(self.default_model, synthesis_messages)
        
        return final_response
