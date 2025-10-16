import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# O diretório base unificado para todos os projetos.
# A gestão da criação deste diretório é feita pelo módulo `history`.
PROJECTS_BASE_DIR = Path('data/projects')

def _get_safe_project_files_path(project_name: str, file_path: str = None) -> Path:
    """
    Constrói e valida um caminho para um arquivo dentro do subdiretório 'files' de um projeto.
    Previne ataques de Path Traversal.
    """
    project_path = PROJECTS_BASE_DIR.joinpath(project_name).resolve()
    files_dir = project_path.joinpath('files').resolve()

    # Validação de segurança: o caminho do projeto deve estar sob o diretório base.
    if PROJECTS_BASE_DIR.resolve() not in project_path.parents:
        raise PermissionError("Acesso negado: tentativa de sair do diretório de projetos.")

    if file_path:
        # Resolve o caminho do arquivo para evitar '..' e outros truques
        full_path = files_dir.joinpath(file_path).resolve()

        # Garante que o caminho final do arquivo permaneça dentro do diretório 'files'
        if files_dir != full_path.parent and not str(full_path).startswith(str(files_dir)):
             raise PermissionError("Acesso negado: tentativa de acessar arquivo fora do diretório 'files'.")
        return full_path
        
    return files_dir

def create_project_file(project_name: str, file_path: str, content: str) -> str:
    """
    Cria ou atualiza um arquivo com conteúdo dentro do subdiretório 'files' de um projeto.
    """
    try:
        safe_path = _get_safe_project_files_path(project_name, file_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        safe_path.write_text(content, encoding='utf-8')
        logger.info(f"Arquivo salvo com sucesso: {safe_path}")
        return str(safe_path)
    except PermissionError as e:
        logger.error(f"Erro de segurança ao criar arquivo: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar o arquivo '{file_path}' no projeto '{project_name}': {e}")
        raise

def read_project_file(project_name: str, file_path: str) -> str:
    """
    Lê o conteúdo de um arquivo do subdiretório 'files' de um projeto.
    """
    try:
        safe_path = _get_safe_project_files_path(project_name, file_path)
        if not safe_path.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        return safe_path.read_text(encoding='utf-8')
    except (PermissionError, FileNotFoundError) as e:
        logger.error(f"Erro ao ler o arquivo '{file_path}' no projeto '{project_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao ler o arquivo '{file_path}': {e}")
        raise

def get_project_files(project_name: str) -> dict:
    """
    Lista a árvore de arquivos e pastas do subdiretório 'files' de um projeto.
    """
    try:
        files_dir = _get_safe_project_files_path(project_name)
        if not files_dir.is_dir():
            return {}

        file_tree = {}
        for path in sorted(files_dir.rglob('*')):
            relative_path = path.relative_to(files_dir)
            parts = relative_path.parts
            current_level = file_tree
            for i, part in enumerate(parts):
                if i < len(parts) - 1:
                    current_level = current_level.setdefault(part, {})
                else:
                    current_level[part] = {} if path.is_dir() else None
        
        return file_tree
    except PermissionError as e:
        logger.error(f"Erro de segurança ao listar arquivos: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do projeto '{project_name}': {e}")
        return {"error": "Erro interno ao processar a estrutura de arquivos."}