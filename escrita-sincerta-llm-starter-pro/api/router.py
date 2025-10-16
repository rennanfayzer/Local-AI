import os

# Regras simples de roteamento por complexidade/tipo de tarefa
def pick_model(task_type: str = "code", complexity: str = "normal") -> str:
    # Permite override via env
    override = os.getenv("MODEL_OVERRIDE")
    if override:
        return override

    task_type = (task_type or "code").lower()
    complexity = (complexity or "normal").lower()

    # Mapas
    small = os.getenv("SMALL_MODEL", "phi3:3.8b")
    general = os.getenv("GENERAL_MODEL", "qwen2.5:7b")
    heavy = os.getenv("HEAVY_MODEL", "gpt-oss-20b")

    if complexity in ("tiny", "low", "leve"):
        return small

    if complexity in ("hard", "heavy", "alta", "alta-complexidade"):
        return heavy

    # Específico por task
    if task_type in ("plan", "ideation", "pm"):
        return general
    if task_type in ("generate", "refactor", "test"):
        return general
    return general
