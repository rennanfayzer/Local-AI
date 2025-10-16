import os
import json
import logging
from typing import Dict, Any
from .base import BaseAgent, register_agent
from tools.project_writer import read_project_file, create_project_file

logger = logging.getLogger(__name__)

@register_agent
class EditorAgent(BaseAgent):
    """
    Agente especializado em ler, analisar e modificar arquivos de código existentes.
    """
    
    def __init__(self):
        super().__init__(
            name="editor",
            default_model=os.getenv("EDITOR_MODEL", "codegemma:7b"),
            capabilities=["file_reading", "file_writing", "code_modification", "refactoring"]
        )

    def get_system_prompt(self) -> str:
        """Prompt especializado para edição de código."""
        return """
Você é um Engenheiro de Software de IA especialista em refatoração e edição de código. Sua tarefa é modificar arquivos de código existentes com base nas solicitações do usuário.

**PROCESSO DE EDIÇÃO:**

1.  **Analisar a Solicitação**: Entenda qual arquivo precisa ser modificado e qual é a mudança exata solicitada.
2.  **Ler o Código Original**: Analise o conteúdo completo do arquivo original para entender o contexto.
3.  **Aplicar a Modificação**: Re-escreva o código, aplicando a mudança solicitada. Mantenha o restante do código intacto.
4.  **Gerar o Código Completo**: Sua resposta final deve ser o **conteúdo completo** do arquivo modificado. Não use trechos ou explique as mudanças, apenas forneça o código final.

**REGRAS CRÍTICAS:**

-   **SAÍDA É CÓDIGO PURO**: Sua resposta final deve ser apenas o código do arquivo modificado, pronto para ser salvo. Não inclua explicações, comentários sobre as mudanças ou blocos de markdown.
-   **MODIFICAÇÕES PRECISAS**: Altere apenas o que foi solicitado. Preserve a estrutura, estilo e lógica do restante do arquivo.
-   **CONTEXTO É REI**: Use o código original como contexto principal para garantir que sua modificação seja consistente e funcional.
"""

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Orquestra o processo de leitura, modificação e escrita de um arquivo.
        """
        model = context.get("model", self.default_model)
        
        # Etapa 1: Extrair o nome do projeto e o caminho do arquivo da mensagem do usuário
        # Esta é uma simplificação. Uma versão mais robusta usaria o LLM para extrair isso.
        try:
            # Exemplo de formato esperado: "No projeto 'meu-app', modifique 'src/App.js' para..."
            parts = message.split("'")
            project_name = parts[1]
            file_path = parts[3]
            user_request = message.split(f"'{file_path}'")[1].strip()
        except IndexError:
            return "Formato da solicitação inválido. Por favor, use: \"No projeto '[nome_do_projeto]', modifique '[caminho_do_arquivo]' para [sua_modificação]\"."

        logger.info(f"Solicitação de edição para o arquivo '{file_path}' no projeto '{project_name}'.")

        # Etapa 2: Ler o conteúdo original do arquivo
        try:
            original_content = read_project_file(project_name, file_path)
        except FileNotFoundError:
            return f"Erro: O arquivo '{file_path}' não foi encontrado no projeto '{project_name}'."
        except Exception as e:
            return f"Erro ao ler o arquivo: {e}"

        # Etapa 3: Pedir ao LLM para gerar o conteúdo modificado
        edit_prompt = f"""
**PROJETO:** {project_name}
**ARQUIVO A SER MODIFICADO:** {file_path}

**CONTEÚDO ORIGINAL DO ARQUIVO:**
```
{original_content}
```

**TAREFA DE MODIFICAÇÃO:**
{user_request}

**INSTRUÇÃO FINAL:**
Agora, gere o conteúdo COMPLETO e ATUALIZADO do arquivo `{file_path}` após aplicar a modificação solicitada. Sua resposta deve ser apenas o código.
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": edit_prompt}
        ]
        
        modified_content = await self.call_ollama(model, messages)

        # Etapa 4: Salvar (sobrescrever) o arquivo com o novo conteúdo
        try:
            create_project_file(project_name, file_path, modified_content)
            logger.info(f"Arquivo '{file_path}' no projeto '{project_name}' foi modificado com sucesso.")
            return f"O arquivo '{file_path}' no projeto '{project_name}' foi modificado com sucesso."
        except Exception as e:
            logger.error(f"Falha ao salvar o arquivo modificado: {e}")
            return f"Erro ao salvar o arquivo modificado: {e}"
