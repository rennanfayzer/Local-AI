import logging
from duckduckgo_search import DDGS
from typing import List, Dict

logger = logging.getLogger(__name__)

async def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Realiza uma busca na web usando DuckDuckGo e retorna os resultados.

    Args:
        query: O termo a ser buscado.
        max_results: O número máximo de resultados a serem retornados.

    Returns:
        Uma lista de dicionários, onde cada dicionário representa um resultado
        com 'title', 'href' (link), e 'body' (snippet).
    """
    logger.info(f"Realizando busca na web por: '{query}'")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            logger.warning("A busca na web não retornou resultados.")
            return []
            
        logger.info(f"Busca retornou {len(results)} resultados.")
        return results
        
    except Exception as e:
        logger.error(f"Erro durante a busca na web com DuckDuckGo: {e}")
        # Retorna o erro para que o agente possa lidar com ele
        raise

