import os
import json
import logging
from typing import Dict, Any, List
from .base import BaseAgent, register_agent
from tools.project_writer import create_project_file, get_generated_projects

logger = logging.getLogger(__name__)

@register_agent
class BuilderAgent(BaseAgent):
    """
    Agente especializado em scaffolding e geração de projetos completos no disco.
    """
    
    def __init__(self):
        super().__init__(
            name="builder_web",
            default_model=os.getenv("BUILDER_MODEL", "codegemma:7b"), # Alterado para um modelo mais capaz
            capabilities=["project_scaffolding", "file_generation", "multi_file_projects"]
        )

    def get_system_prompt(self) -> str:
        """Prompt especializado para building e scaffolding."""
        return """
Você é o "Arcano", um agente de IA construtor de software. Sua especialidade é gerar projetos de código completos, com múltiplos arquivos e estruturas de pastas complexas.

**SUA MISSÃO:**
1. **Analisar a Solicitação**: Entender o tipo de projeto, a stack de tecnologia e os requisitos.
2. **Planejar a Estrutura**: Criar um plano detalhado de todos os arquivos e pastas necessários.
3. **Gerar Conteúdo**: Escrever o código para cada arquivo individualmente, garantindo que seja funcional e siga as melhores práticas.

**REGRAS CRÍTICAS:**

1.  **PLANEJAMENTO PRIMEIRO**: Antes de escrever qualquer código, você DEVE primeiro gerar um JSON que descreve a estrutura completa do projeto. Este JSON deve ser um objeto onde as chaves são os caminhos dos arquivos (ex: "src/index.js") e os valores são uma breve descrição do propósito do arquivo.
    
    **EXEMPLO DE JSON DE ESTRUTURA:**
    ```json
    {
      "project_name": "simple-react-app",
      "files": {
        "package.json": "Define as dependências e scripts do projeto.",
        "vite.config.js": "Configuração do Vite para o servidor de desenvolvimento.",
        "src/index.css": "Estilos globais da aplicação.",
        "src/main.jsx": "Ponto de entrada da aplicação React.",
        "src/App.jsx": "Componente principal da aplicação."
      }
    }
    ```

2.  **GERAÇÃO FOCADA**: Ao gerar o conteúdo de um arquivo, foque APENAS naquele arquivo. Não inclua nomes de arquivos ou outros metadados no conteúdo. O código deve ser puro e pronto para ser salvo.

3.  **SEMPRE FUNCIONAL**: O projeto final deve ser executável. Inclua todas as dependências, configurações e scripts necessários para que o usuário possa rodar o projeto com comandos padrão (ex: `npm install && npm run dev`).
"""

    async def _plan_project_structure(self, user_request: str, model: str) -> str:
        """
        Pede ao LLM para gerar um plano de estrutura de arquivos em formato JSON.
        """
        prompt = f"""
Baseado na seguinte solicitação do usuário, gere um plano de estrutura de arquivos em formato JSON.
O JSON deve conter 'project_name' e um objeto 'files' com os caminhos dos arquivos como chaves.

**Solicitação do Usuário:** "{user_request}"

**JSON de Estrutura:**
"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.call_ollama(model, messages)
        # Extrai o bloco JSON da resposta do modelo
        json_block = response[response.find('{'):response.rfind('}')+1]
        return json_block

    async def _generate_and_write_files(self, project_name: str, files: Dict[str, str], user_request: str, model: str):
        """
        Itera sobre o plano de arquivos, gera o conteúdo para cada um e o salva no disco.
        """
        logger.info(f"Iniciando a geração de {len(files)} arquivos para o projeto '{project_name}'...")
        
        for file_path, description in files.items():
            logger.info(f"Gerando conteúdo para: {file_path} ({description})")
            
            generation_prompt = f"""
**Solicitação Original do Projeto:** "{user_request}"

**Estrutura do Projeto (JSON):**
```json
{json.dumps(files, indent=2)}
```

**Tarefa Atual:**
Gere o conteúdo COMPLETO e FUNCIONAL para o seguinte arquivo:
- **Caminho do Arquivo:** `{file_path}`
- **Descrição:** `{description}`

**REGRAS:**
- Gere APENAS o conteúdo do arquivo.
- NÃO inclua o nome do arquivo, o caminho ou qualquer outra explicação no output.
- O código deve ser completo e pronto para ser salvo diretamente no arquivo.
"""
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": generation_prompt}
            ]
            
            logger.debug(f"Payload para o Ollama: {json.dumps(messages, indent=2)}")
            
            file_content = await self.call_ollama(model, messages)
            
            # Limpa o conteúdo para remover blocos de código markdown
            if file_content.startswith("```") and file_content.endswith("```"):
                file_content = '\n'.join(file_content.split('\n')[1:-1])

            create_project_file(project_name, file_path, file_content)

    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Implementa o método abstrato e orquestra o processo de build.
        """
        model = context.get("model", self.default_model)
        
        # Etapa 1: Planejar a estrutura do projeto
        try:
            plan_json_str = await self._plan_project_structure(message, model)
            plan = json.loads(plan_json_str)
            project_name = plan.get("project_name", "novo-projeto-gerado")
            files_to_create = plan.get("files", {})
        except (json.JSONDecodeError, TypeError):
            logger.error("Falha ao decodificar o plano JSON do LLM.")
            return "Desculpe, não consegui criar um plano de projeto válido. A resposta do modelo não era um JSON formatado corretamente."

        if not files_to_create:
            return "Não consegui determinar quais arquivos criar para este projeto. Tente ser mais específico."

        # Etapa 2: Gerar e escrever cada arquivo
        await self._generate_and_write_files(project_name, files_to_create, message, model)

        project_path = os.path.abspath(os.path.join('data', 'generated_projects', project_name))
        
        # Retorna uma string formatada especial que o frontend pode parsear
        return f"BUILD_SUCCESS|{project_name}|{project_path}"
