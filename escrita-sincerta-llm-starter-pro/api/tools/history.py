import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CONVERSATIONS_DIR = os.path.join('data', 'conversations')

def _ensure_dir():
    """Garante que o diretório de conversas exista."""
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

def get_projects() -> List[str]:
    """Lista todos os projetos (diretórios) de conversas."""
    _ensure_dir()
    try:
        return [d for d in os.listdir(CONVERSATIONS_DIR) if os.path.isdir(os.path.join(CONVERSATIONS_DIR, d))]
    except FileNotFoundError:
        return []

def create_project(project_name: str) -> bool:
    """Cria um novo projeto (diretório)."""
    _ensure_dir()
    project_path = os.path.join(CONVERSATIONS_DIR, project_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        # Cria um arquivo de histórico inicial vazio
        save_conversation_history(project_name, [])
        logger.info(f"Projeto '{project_name}' criado em {project_path}")
        return True
    logger.warning(f"Tentativa de criar projeto que já existe: '{project_name}'")
    return False

def get_conversation_history(project_name: str) -> List[Dict[str, Any]]:
    """Carrega o histórico de conversas de um projeto."""
    _ensure_dir()
    history_file = os.path.join(CONVERSATIONS_DIR, project_name, 'history.json')
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Erro ao carregar histórico para '{project_name}': {e}")
        return []

def delete_project(project_name: str) -> bool:
    """Deleta um projeto de conversa, incluindo seu diretório e histórico."""
    _ensure_dir()
    project_path = os.path.join(CONVERSATIONS_DIR, project_name)
    
    # Validação de segurança para evitar Path Traversal
    if not os.path.abspath(project_path).startswith(os.path.abspath(CONVERSATIONS_DIR)):
        logger.error(f"Tentativa de deletar projeto fora do diretório permitido: '{project_name}'")
        return False

    if os.path.exists(project_path) and os.path.isdir(project_path):
        try:
            import shutil
            shutil.rmtree(project_path)
            logger.info(f"Projeto '{project_name}' deletado com sucesso.")
            return True
        except OSError as e:
            logger.error(f"Erro ao deletar o diretório do projeto '{project_name}': {e}")
            return False
    else:
        logger.warning(f"Tentativa de deletar um projeto que não existe: '{project_name}'")
        return False

def save_conversation_history(project_name: str, history: List[Dict[str, Any]]) -> bool:
    """Salva o histórico de conversas de um projeto."""
    _ensure_dir()
    project_path = os.path.join(CONVERSATIONS_DIR, project_name)
    if not os.path.exists(project_path):
        create_project(project_name)
        
    history_file = os.path.join(project_path, 'history.json')
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error(f"Erro ao salvar histórico para '{project_name}': {e}")
        return False

