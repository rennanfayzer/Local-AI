import os
import json
import logging
import shutil
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

PROJECTS_BASE_DIR = 'data/projects'

def _get_project_path(project_name: str) -> str:
    """Retorna o caminho para o diretório de um projeto."""
    return os.path.join(PROJECTS_BASE_DIR, project_name)

def _get_conversations_dir(project_name: str) -> str:
    """Retorna o caminho para o diretório de conversas de um projeto."""
    return os.path.join(_get_project_path(project_name), 'conversations')

def _ensure_project_structure(project_name: str):
    """Garante que a estrutura de diretórios de um projeto exista."""
    project_path = _get_project_path(project_name)
    os.makedirs(os.path.join(project_path, 'files'), exist_ok=True)
    os.makedirs(os.path.join(project_path, 'conversations'), exist_ok=True)

def get_projects() -> List[str]:
    """Lista todos os projetos."""
    if not os.path.exists(PROJECTS_BASE_DIR):
        return []
    return [d for d in os.listdir(PROJECTS_BASE_DIR) if os.path.isdir(os.path.join(PROJECTS_BASE_DIR, d))]

def create_project(project_name: str) -> bool:
    """Cria um novo projeto com uma conversa inicial 'default'."""
    project_path = _get_project_path(project_name)
    if os.path.exists(project_path):
        logger.warning(f"Tentativa de criar um projeto que já existe: '{project_name}'")
        return False

    _ensure_project_structure(project_name)
    # Cria uma conversa inicial
    save_conversation_history(project_name, 'default', [])
    logger.info(f"Projeto '{project_name}' criado com sucesso.")
    return True

def rename_project(old_project_name: str, new_project_name: str) -> bool:
    """Renomeia um projeto."""
    old_path = _get_project_path(old_project_name)
    new_path = _get_project_path(new_project_name)

    if not os.path.exists(old_path):
        logger.warning(f"Tentativa de renomear um projeto que não existe: '{old_project_name}'")
        return False
    if os.path.exists(new_path):
        logger.warning(f"Tentativa de renomear para um projeto que já existe: '{new_project_name}'")
        return False

    try:
        os.rename(old_path, new_path)
        logger.info(f"Projeto '{old_project_name}' renomeado para '{new_project_name}'.")
        return True
    except OSError as e:
        logger.error(f"Erro ao renomear o projeto '{old_project_name}': {e}")
        return False

def delete_project(project_name: str) -> bool:
    """Deleta um projeto, incluindo todos os seus arquivos e conversas."""
    project_path = _get_project_path(project_name)
    
    if not os.path.abspath(project_path).startswith(os.path.abspath(PROJECTS_BASE_DIR)):
        logger.error(f"Tentativa de deletar projeto fora do diretório permitido: '{project_name}'")
        return False

    if os.path.exists(project_path):
        try:
            shutil.rmtree(project_path)
            logger.info(f"Projeto '{project_name}' deletado com sucesso.")
            return True
        except OSError as e:
            logger.error(f"Erro ao deletar o projeto '{project_name}': {e}")
            return False
    else:
        logger.warning(f"Tentativa de deletar um projeto que não existe: '{project_name}'")
        return False

# --- Funções de Conversa ---

def list_conversations(project_name: str) -> List[str]:
    """Lista todas as conversas de um projeto."""
    conversations_dir = _get_conversations_dir(project_name)
    if not os.path.exists(conversations_dir):
        return []
    return [f.replace('.json', '') for f in os.listdir(conversations_dir) if f.endswith('.json')]

def get_conversation_history(project_name: str, conversation_name: str) -> List[Dict[str, Any]]:
    """Carrega o histórico de uma conversa específica de um projeto."""
    history_file = os.path.join(_get_conversations_dir(project_name), f"{conversation_name}.json")
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erro ao carregar histórico '{conversation_name}' para o projeto '{project_name}': {e}")
        return []

def save_conversation_history(project_name: str, conversation_name: str, history: List[Dict[str, Any]]) -> bool:
    """Salva o histórico de uma conversa específica de um projeto."""
    _ensure_project_structure(project_name) # Garante que a estrutura exista
    history_file = os.path.join(_get_conversations_dir(project_name), f"{conversation_name}.json")
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Erro ao salvar histórico '{conversation_name}' para o projeto '{project_name}': {e}")
        return False