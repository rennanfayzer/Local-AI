import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Define um diretório base seguro para a geração de projetos
PROJECTS_BASE_DIR = Path('data/generated_projects')

def _get_safe_path(project_name: str, file_path: str = None) -> Path:
    """
    Constrói e valida um caminho para garantir que ele esteja dentro do diretório base.
    Previne ataques de Path Traversal.
    """
    _ensure_base_dir()
    
    project_path = PROJECTS_BASE_DIR.joinpath(project_name).resolve()
    
    # Garante que o caminho do projeto esteja dentro do diretório base
    if PROJECTS_BASE_DIR.resolve() not in project_path.parents:
        raise PermissionError("Tentativa de acesso fora do diretório de projetos permitido.")

    if file_path:
        full_path = project_path.joinpath(file_path).resolve()
        # Garante que o caminho do arquivo também esteja dentro do caminho do projeto
        if project_path not in full_path.parents:
             raise PermissionError("Tentativa de acesso fora do diretório do projeto permitido.")
        return full_path
        
    return project_path

def _ensure_base_dir():
    """Garante que o diretório base de projetos exista."""
    PROJECTS_BASE_DIR.mkdir(parents=True, exist_ok=True)

def create_project_file(project_name: str, file_path: str, content: str) -> str:
    """
    Cria um arquivo com conteúdo dentro de um projeto específico.
    Cria diretórios intermediários se necessário.

    Args:
        project_name: O nome do projeto (será o diretório principal).
        file_path: O caminho relativo do arquivo dentro do projeto (ex: 'src/app.js').
        content: O conteúdo a ser escrito no arquivo.

    Returns:
        O caminho absoluto do arquivo criado.
    """
    try:
        safe_path = _get_safe_path(project_name, file_path)
        
        # Cria o diretório pai do arquivo, se não existir
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escreve o conteúdo no arquivo
        safe_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Arquivo criado com sucesso: {safe_path}")
        return str(safe_path)
        
    except PermissionError as e:
        logger.error(f"Erro de segurança ao tentar criar arquivo: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar o arquivo '{file_path}' no projeto '{project_name}': {e}")
        raise

def read_project_file(project_name: str, file_path: str) -> str:
    """
    Lê o conteúdo de um arquivo de um projeto específico.

    Returns:
        O conteúdo do arquivo como string.
    """
    try:
        safe_path = _get_safe_path(project_name, file_path)
        if not safe_path.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        return safe_path.read_text(encoding='utf-8')
    except (PermissionError, FileNotFoundError) as e:
        logger.error(f"Erro ao ler o arquivo '{file_path}' no projeto '{project_name}': {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao ler o arquivo '{file_path}': {e}")
        raise

def get_generated_projects() -> list:
    """Lista todos os projetos que foram gerados."""
    _ensure_base_dir()
    return [d.name for d in PROJECTS_BASE_DIR.iterdir() if d.is_dir()]

def get_project_files(project_name: str) -> dict:
    """Lista todos os arquivos e pastas de um projeto gerado."""
    try:
        project_path = _get_safe_path(project_name)
        if not project_path.is_dir():
            return {"error": "Projeto não encontrado."}

        file_tree = {}
        for path in sorted(project_path.rglob('*')):
            # Adiciona o caminho relativo à estrutura
            parts = path.relative_to(project_path).parts
            current_level = file_tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {} if path.is_dir() else None
                current_level = current_level[part]
        
        return file_tree

    except PermissionError as e:
        logger.error(f"Erro de segurança ao listar arquivos: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Erro ao listar arquivos do projeto '{project_name}': {e}")
        return {"error": "Erro interno ao processar a estrutura de arquivos."}


def delete_generated_project(project_name: str) -> bool:
    """
    Deleta o diretório de um projeto gerado.
    """
    try:
        import shutil
        project_path = _get_safe_path(project_name)

        if not project_path.is_dir():
            logger.warning(f"Tentativa de deletar um projeto gerado que não existe: '{project_name}'")
            # Retorna True porque o estado desejado (projeto não existe) foi alcançado
            return True

        shutil.rmtree(project_path)
        logger.info(f"Projeto gerado '{project_name}' deletado com sucesso de {project_path}")
        return True
    except PermissionError as e:
        logger.error(f"Erro de segurança ao tentar deletar o projeto gerado '{project_name}': {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar o projeto gerado '{project_name}': {e}")
        return False
