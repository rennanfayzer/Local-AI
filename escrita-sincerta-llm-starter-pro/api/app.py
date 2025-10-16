from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import os, requests, json, glob, logging, asyncio, time
from pathlib import Path
from typing import List, Optional, Dict, Any
from advanced_router import get_router, TaskType, TaskComplexity
from tools.history import (
    get_projects as get_projects_from_history,
    create_project as create_project_in_history,
    delete_project as delete_project_from_history,
    get_conversation_history,
    save_conversation_history,
)
from tools.project_writer import get_generated_projects, get_project_files

# Sistema de voz removido para economizar espaço
VOICE_ENABLED = False

# Configuração de logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Escrita Sincerta API",
    description="API Orquestradora para LLM Local com Agentes Especializados",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lógica de Execução de Agente (Refatorada) ---

async def execute_agent_task(agent_name: str, message: str, history: List[Dict[str, str]], context: Dict[str, Any]) -> str:
    """
    Função centralizada para selecionar, instanciar e executar um agente.
    """
    router = get_router()
    selected_model, routing_info = await router.route_request(message, {"agent": agent_name})
    logger.info(f"Router selected '{selected_model}' for agent '{agent_name}' - {routing_info.get('reason', 'unknown')}")

    # Constrói as mensagens para o agente
    prompts = load_prompts()
    system_content = f"{prompts['system_base']}\n\n{prompts['manifesto']}"
    messages = [{"role": "system", "content": system_content}] + history + [{"role": "user", "content": message}]

    try:
        agent_map = {
            "ideator_saas": "agents.ideator_saas.IdeatorAgent",
            "architect_fullstack": "agents.architect_fullstack.ArchitectFullstackAgent",
            "builder_web": "agents.builder_web.BuilderAgent",
            "editor": "agents.editor.EditorAgent",
            "researcher": "agents.researcher.ResearcherAgent",
            "dev_fullstack": "agents.dev_fullstack.DevFullstackAgent",
            "orchestrator": "agents.orchestrator.OrchestratorAgent",
        }
        
        if agent_name not in agent_map:
            logger.warning(f"Agente '{agent_name}' desconhecido. Usando chat direto.")
            return await ollama_chat(selected_model, messages)

        # Importa e instancia o agente dinamicamente
        module_path, class_name = agent_map[agent_name].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        AgentClass = getattr(module, class_name)
        agent_instance = AgentClass()
        
        return await agent_instance.process(message=message, messages=messages, model=selected_model, context=context)

    except Exception as agent_error:
        logger.error(f"Erro ao processar com o agente '{agent_name}': {agent_error}", exc_info=True)
        # Fallback para chat direto em caso de erro no agente
        return await ollama_chat(selected_model, messages)


# Configurações
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEV_MODEL = os.getenv("DEV_MODEL", "qwen2.5:7b")
REFLEX_MODEL = os.getenv("REFLEX_MODEL", "phi3:3.8b")
DATA_DIR = Path("/app/data")

# Modelos Pydantic
class ChatRequest(BaseModel):
    agent: str = "dev_fullstack"
    message: str
    history: List[Dict[str, str]] = []
    task_type: Optional[str] = None
    complexity: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    reply: str
    model_used: str
    agent: str
    metadata: Dict[str, Any] = {}
    model_config = ConfigDict(protected_namespaces=())

class IngestRequest(BaseModel):
    path: str = "data/docs"
    file_types: List[str] = [".md", ".txt", ".html", ".pdf"]

class ModelInfo(BaseModel):
    name: str
    size: str
    modified_at: str
    digest: str

class AgentInfo(BaseModel):
    name: str
    description: str
    default_model: str
    capabilities: List[str]

class ProjectRequest(BaseModel):
    project_name: str

# Utilitários para Ollama com roteamento inteligente
async def ollama_chat_with_routing(model: str, messages: List[Dict[str, str]], stream: bool = False, 
                                  routing_context: Dict[str, Any] = None) -> tuple[str, Dict[str, Any]]:
    """Envia mensagens para o Ollama com sistema de roteamento avançado"""
    start_time = time.time()
    success = False
    router = get_router()
    
    try:
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        response = requests.post(
            f"{OLLAMA_URL}/api/chat", 
            json=payload, 
            timeout=120
        )
        response.raise_for_status()
        
        data = response.json()
        content = data.get("message", {}).get("content", "")
        success = True
        
        return content, {"model_used": model, "success": True}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao comunicar com Ollama: {e}")
        raise HTTPException(status_code=503, detail=f"Ollama indisponível: {str(e)}")
    
    finally:
        # Update model performance metrics
        response_time = time.time() - start_time
        router.update_model_metrics(model, success, response_time)

async def ollama_chat(model: str, messages: List[Dict[str, str]], stream: bool = False) -> str:
    """Backward compatibility wrapper"""
    content, _ = await ollama_chat_with_routing(model, messages, stream)
    return content

def load_prompts() -> Dict[str, str]:
    """Carrega prompts do diretório"""
    prompts = {}
    prompts_dir = Path("prompts")
    
    try:
        # Manifesto Sincerta
        manifesto_path = prompts_dir / "manifesto_sincerta.md"
        if manifesto_path.exists():
            prompts["manifesto"] = manifesto_path.read_text(encoding="utf-8")
        else:
            prompts["manifesto"] = "Seja direto, técnico e honesto."
        
        # System base
        system_path = prompts_dir / "system_base.md"
        if system_path.exists():
            prompts["system_base"] = system_path.read_text(encoding="utf-8")
        else:
            prompts["system_base"] = "Você é um assistente técnico especializado."
            
        # Styles
        styles_path = prompts_dir / "styles.json"
        if styles_path.exists():
            styles_content = styles_path.read_text(encoding="utf-8")
            prompts["styles"] = json.loads(styles_content)
        else:
            prompts["styles"] = {}
            
    except Exception as e:
        logger.warning(f"Erro ao carregar prompts: {e}")
        prompts.setdefault("manifesto", "Seja direto e técnico.")
        prompts.setdefault("system_base", "Você é um assistente especializado.")
        prompts.setdefault("styles", {})
    
    return prompts

# Endpoints para gerenciamento de histórico e projetos
@app.get("/projects", response_model=List[str])
async def list_projects():
    """Lista todos os projetos de conversa."""
    return get_projects_from_history()

@app.post("/projects")
async def create_project(request: ProjectRequest):
    """Cria um novo projeto de conversa."""
    success = create_project_in_history(request.project_name)
    if not success:
        raise HTTPException(status_code=400, detail="Projeto já existe.")
    return {"status": "success", "project_name": request.project_name}

@app.delete("/projects/{project_name}")
async def delete_project(project_name: str):
    """Deleta um projeto de conversa."""
    success = delete_project_from_history(project_name)
    if not success:
        raise HTTPException(status_code=404, detail="Projeto não encontrado ou falha ao deletar.")
    return {"status": "success", "project_name": project_name}

@app.get("/history/{project_name}", response_model=List[Dict[str, Any]])
async def get_history(project_name: str):
    """Obtém o histórico de conversa de um projeto."""
    return get_conversation_history(project_name)

@app.post("/history/{project_name}")
async def save_history(project_name: str, history: List[Dict[str, Any]] = Body(...)):
    """Salva o histórico de conversa de um projeto."""
    success = save_conversation_history(project_name, history)
    if not success:
        raise HTTPException(status_code=500, detail="Falha ao salvar o histórico.")
    return {"status": "success"}

# Endpoints para projetos gerados pelo Builder
@app.get("/generated-projects", response_model=List[str])
async def list_generated_projects():
    """Lista todos os projetos gerados pelo Agente Builder."""
    return get_generated_projects()

@app.get("/generated-projects/{project_name}")
async def get_generated_project_details(project_name: str):
    """Retorna a estrutura de arquivos de um projeto gerado."""
    files = get_project_files(project_name)
    if "error" in files:
        raise HTTPException(status_code=404, detail=files["error"])
    return {"project_name": project_name, "files": files}


# Endpoints principais
@app.get("/health")
async def health_check():
    """Verifica saúde da API e conectividade com Ollama"""
    try:
        # Teste conectividade Ollama
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_status = "ok" if response.status_code == 200 else "error"
        models_count = len(response.json().get("models", [])) if ollama_status == "ok" else 0
        
        return {
            "api_status": "ok",
            "ollama_status": ollama_status,
            "models_available": models_count,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "api_status": "ok",
            "ollama_status": "error",
            "models_available": 0,
            "error": str(e)
        }

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """Lista modelos disponíveis no Ollama"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        response.raise_for_status()
        
        models = response.json().get("models", [])
        return [
            ModelInfo(
                name=model["name"],
                size=model.get("size", "unknown"),
                modified_at=model.get("modified_at", ""),
                digest=model.get("digest", "")
            )
            for model in models
        ]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro ao listar modelos: {str(e)}")

@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    """Lista agentes disponíveis"""
    agents = [
        AgentInfo(
            name="ideator",
            description="Especialista em ideação de SaaS, análise de mercado e definição de MVPs",
            default_model="qwen2.5:7b",
            capabilities=["saas_ideation", "market_analysis", "mvp_definition", "personas", "design_thinking"]
        ),
        AgentInfo(
            name="architect",
            description="Arquiteto de sistemas fullstack, especialista em design de arquitetura e seleção de tecnologias",
            default_model="llama3.1:8b-instruct",
            capabilities=["system_architecture", "tech_stack_selection", "database_design", "api_design", "scalability"]
        ),
        AgentInfo(
            name="builder",
            description="Construtor de projetos multi-framework (React, FastAPI, Flutter, Vue, Node.js)",
            default_model="codegemma:7b",
            capabilities=["project_scaffolding", "code_generation", "framework_templates", "boilerplate", "multi_stack"]
        ),
        AgentInfo(
            name="dev_fullstack",
            description="Desenvolvedor full-stack especializado em Python, FastAPI, React",
            default_model=DEV_MODEL,
            capabilities=["code_generation", "debugging", "architecture", "testing"]
        ),
        AgentInfo(
            name="reflexivo",
            description="Agente reflexivo para análise, planejamento e otimização",
            default_model=REFLEX_MODEL,
            capabilities=["analysis", "planning", "review", "optimization", "strategic_thinking"]
        )
    ]
    return agents

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal para chat com agentes - com roteamento inteligente"""
    try:
        if request.agent == "auto":
            # O modo "Auto" agora invoca o Orquestrador para criar um plano
            from agents.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            plan_json = await orchestrator.process_message(request.message, request.context)
            
            # Por enquanto, apenas retornamos o plano para o frontend
            # A execução passo a passo será a próxima etapa
            return ChatResponse(
                reply=f"ORCHESTRATOR_PLAN|{plan_json}",
                model_used=orchestrator.default_model,
                agent="orchestrator",
                metadata={"plan": json.loads(plan_json)}
            )
        else:
            # Execução de agente único (como antes, mas usando a função refatorada)
            reply = await execute_agent_task(
                agent_name=request.agent,
                message=request.message,
                history=request.history,
                context=request.context or {}
            )
            return ChatResponse(
                reply=reply,
                model_used="varied", # O roteador decide
                agent=request.agent,
                metadata={}
            )
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

class TaskRequest(BaseModel):
    agent: str
    prompt: str
    project_name: str # Para dar contexto ao agente

@app.post("/execute_task")
async def execute_task_endpoint(request: TaskRequest):
    """Executa uma única tarefa de um plano usando um agente específico."""
    try:
        # O histórico é construído a partir do projeto atual para dar contexto
        history = get_conversation_history(request.project_name)
        
        # O 'message' aqui é o prompt detalhado do passo do plano
        reply = await execute_agent_task(
            agent_name=request.agent,
            message=request.prompt,
            history=history,
            context={"project_name": request.project_name}
        )
        
        # Salva o resultado da execução no histórico do projeto
        history.append({"role": "user", "content": f"Executando tarefa: {request.prompt}"})
        history.append({"role": "assistant", "content": reply})
        save_conversation_history(request.project_name, history)

        return {"status": "success", "reply": reply}
    except Exception as e:
        logger.error(f"Erro ao executar tarefa: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao executar tarefa: {str(e)}")


@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """Ingestão de documentos para RAG"""
    try:
        from tools.rag import ingest_path
        
        # Verifica se o diretório existe
        path = Path(request.path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Diretório não encontrado: {request.path}")
        
        # Processa ingestão
        file_count = ingest_path(str(path), request.file_types)
        
        return {
            "status": "success",
            "path": request.path,
            "files_processed": file_count,
            "file_types": request.file_types
        }
        
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na ingestão: {str(e)}")

@app.post("/query")
async def query_knowledge(query: str = Body(...), top_k: int = Body(5)):
    """Query na base de conhecimento RAG"""
    try:
        from tools.rag import query_vectors
        
        results = query_vectors(query, top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Erro na query: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na query: {str(e)}")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload de arquivo para processamento"""
    try:
        # Cria diretório se não existir
        upload_dir = DATA_DIR / "docs"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva arquivo
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "path": str(file_path)
        }
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@app.get("/files")
async def list_files():
    """Lista arquivos disponíveis"""
    try:
        docs_dir = DATA_DIR / "docs"
        if not docs_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in docs_dir.rglob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(docs_dir)),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        
        return {"files": files}
        
    except Exception as e:
        logger.error(f"Erro ao listar arquivos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos: {str(e)}")

# Endpoints do Sistema de Roteamento Avançado

@app.get("/routing/stats")
async def get_routing_stats():
    """Obtém estatísticas do sistema de roteamento"""
    try:
        router = get_router()
        stats = router.get_routing_stats()
        
        # Add available models check
        available_models = await router.get_available_models()
        stats["available_models_status"] = {
            "available": available_models,
            "total_configured": len(router.model_configs)
        }
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de roteamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/routing/analyze")
async def analyze_routing_request(
    message: str = Body(...), 
    context: Dict[str, Any] = Body(default=None)
):
    """Analisa uma mensagem e retorna a decisão de roteamento sem executar"""
    try:
        router = get_router()
        selected_model, routing_info = await router.route_request(message, context)
        
        # Add task analysis details
        task_complexity = router.analyze_task_complexity(message, context)
        task_type = router.analyze_task_type(message, context)
        
        return {
            "message": message,
            "selected_model": selected_model,
            "task_type": task_type.value,
            "task_complexity": task_complexity.value,
            "routing_decision": routing_info,
            "analysis": {
                "message_length": len(message),
                "context_provided": context is not None,
                "complexity_factors": router.complexity_keywords,
                "type_factors": router.task_type_keywords
            }
        }
    except Exception as e:
        logger.error(f"Erro na análise de roteamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/routing/models")
async def get_model_configurations():
    """Retorna configurações dos modelos disponíveis"""
    try:
        router = get_router()
        
        # Get available models and their configs
        available_models = await router.get_available_models()
        
        model_info = {}
        for model_name in router.model_configs:
            config = router.model_configs[model_name]
            metrics = router.model_metrics.get(model_name, {})
            
            model_info[model_name] = {
                "config": {
                    "capabilities": [cap.value for cap in config["capabilities"]],
                    "max_complexity": config["max_complexity"].value,
                    "strengths": config["strengths"],
                    "weaknesses": config["weaknesses"],
                    "performance_score": config["performance_score"],
                    "resource_usage": config["resource_usage"]
                },
                "metrics": metrics,
                "available": model_name in available_models,
                "status": "online" if model_name in available_models else "offline"
            }
        
        return {
            "models": model_info,
            "available_count": len(available_models),
            "total_configured": len(router.model_configs)
        }
    except Exception as e:
        logger.error(f"Erro ao obter configurações dos modelos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/routing/test")
async def test_model_routing(
    message: str = Body(...),
    agent: str = Body("dev_fullstack"),
    context: Dict[str, Any] = Body(default=None)
):
    """Testa o sistema de roteamento com uma mensagem específica"""
    try:
        router = get_router()
        
        # Create routing context
        routing_context = {
            "agent": agent,
            "test_mode": True,
            **(context or {})
        }
        
        # Get routing decision
        selected_model, routing_info = await router.route_request(message, routing_context)
        
        # Test model availability
        model_available = await router.is_model_available(selected_model)
        
        # Get fallback if needed
        fallback_model = None
        if not model_available:
            fallback_model = await router.get_fallback_model(selected_model)
        
        return {
            "test_message": message,
            "agent": agent,
            "routing_result": {
                "selected_model": selected_model,
                "model_available": model_available,
                "fallback_model": fallback_model,
                "routing_info": routing_info
            },
            "analysis": {
                "task_type": router.analyze_task_type(message, routing_context).value,
                "task_complexity": router.analyze_task_complexity(message, routing_context).value
            }
        }
    except Exception as e:
        logger.error(f"Erro no teste de roteamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.post("/routing/benchmark")
async def benchmark_models(
    test_messages: List[str] = Body(...),
    iterations: int = Body(1)
):
    """Executa benchmark dos modelos com mensagens de teste"""
    try:
        router = get_router()
        available_models = await router.get_available_models()
        
        if not available_models:
            raise HTTPException(status_code=503, detail="Nenhum modelo disponível para benchmark")
        
        results = {}
        
        for model in available_models:
            model_results = {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "avg_response_time": 0.0,
                "response_times": [],
                "errors": []
            }
            
            for iteration in range(iterations):
                for message in test_messages:
                    try:
                        start_time = time.time()
                        
                        # Simple test message
                        test_payload = {
                            "model": model,
                            "messages": [{"role": "user", "content": message[:100]}],  # Limit message size
                            "stream": False
                        }
                        
                        response = requests.post(
                            f"{OLLAMA_URL}/api/chat",
                            json=test_payload,
                            timeout=30  # Shorter timeout for benchmarking
                        )
                        
                        response_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            model_results["successful_tests"] += 1
                            model_results["response_times"].append(response_time)
                        else:
                            model_results["failed_tests"] += 1
                            model_results["errors"].append(f"HTTP {response.status_code}")
                        
                        model_results["total_tests"] += 1
                        
                    except Exception as e:
                        model_results["failed_tests"] += 1
                        model_results["total_tests"] += 1
                        model_results["errors"].append(str(e))
            
            # Calculate averages
            if model_results["response_times"]:
                model_results["avg_response_time"] = sum(model_results["response_times"]) / len(model_results["response_times"])
                model_results["min_response_time"] = min(model_results["response_times"])
                model_results["max_response_time"] = max(model_results["response_times"])
            
            model_results["success_rate"] = (
                model_results["successful_tests"] / model_results["total_tests"] 
                if model_results["total_tests"] > 0 else 0
            )
            
            results[model] = model_results
        
        return {
            "benchmark_results": results,
            "test_config": {
                "messages_count": len(test_messages),
                "iterations": iterations,
                "total_tests_per_model": len(test_messages) * iterations
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/routing/examples")
async def get_routing_examples():
    """Retorna exemplos de roteamento para diferentes tipos de tarefa"""
    examples = [
        {
            "category": "Ideação de SaaS",
            "messages": [
                "Preciso de uma ideia para um SaaS de gestão de projetos para startups",
                "Quero criar um app que resolva problemas de comunicação em equipes remotas",
                "Gere uma ideia inovadora para marketplace de serviços digitais"
            ],
            "expected_agent": "ideator",
            "expected_complexity": "medium",
            "expected_models": ["qwen2.5:7b", "llama3.1:8b-instruct"]
        },
        {
            "category": "Arquitetura de Sistema",
            "messages": [
                "Design a arquitetura para um sistema de e-commerce enterprise com microservices",
                "Preciso de uma arquitetura escalável para uma plataforma de streaming",
                "Como estruturar um sistema de chat em tempo real com alta disponibilidade"
            ],
            "expected_agent": "architect",
            "expected_complexity": "expert",
            "expected_models": ["llama3.1:8b-instruct", "qwen2.5:7b"]
        },
        {
            "category": "Desenvolvimento de Código",
            "messages": [
                "Crie um projeto React com TypeScript e setup completo",
                "Gere o scaffolding para uma API FastAPI com autenticação JWT",
                "Build um app Flutter com navegação e gerenciamento de estado"
            ],
            "expected_agent": "builder",
            "expected_complexity": "complex",
            "expected_models": ["codegemma:7b", "llama3.1:8b-instruct"]
        },
        {
            "category": "Desenvolvimento Simples",
            "messages": [
                "Crie uma função Python para calcular fibonacci",
                "Faça um componente React básico de botão",
                "Escreva um endpoint FastAPI simples para health check"
            ],
            "expected_agent": "dev_fullstack",
            "expected_complexity": "simple",
            "expected_models": ["phi3:3.8b", "qwen2.5:7b"]
        },
        {
            "category": "Análise e Planejamento",
            "messages": [
                "Analise os prós e contras de usar microservices vs monolito",
                "Revise esta arquitetura e sugira melhorias de performance",
                "Faça uma análise estratégica deste plano de produto"
            ],
            "expected_agent": "reflexivo",
            "expected_complexity": "complex",
            "expected_models": ["llama3.1:8b-instruct", "qwen2.5:7b"]
        }
    ]
    
    return {
        "routing_examples": examples,
        "usage": "Use esses exemplos para testar o sistema de roteamento em /routing/test",
        "note": "O sistema escolhe automaticamente o modelo baseado na complexidade e tipo da tarefa"
    }

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    features_list = [
        "🤖 Sistema de Roteamento Automático de Modelos",
        "🎯 Agentes Especializados (Ideator, Architect, Builder, Dev, Reflexivo)",
        "📊 Métricas de Performance em Tempo Real",
        "🔄 Fallback Automático e Load Balancing",
        "🛠️ Scaffolding Multi-Framework (React, FastAPI, Flutter, Vue, Node.js)",
        "💡 Ideação de SaaS com Metodologias Avançadas",
        "🏗️ Design de Arquitetura Enterprise",
        "📚 Sistema RAG para Base de Conhecimento"
    ]
    
    endpoints_dict = {
        "chat": "/chat - Chat principal com agentes",
        "agents": "/agents - Lista agentes disponíveis",
        "models": "/models - Lista modelos Ollama",
        "routing_stats": "/routing/stats - Estatísticas do roteamento",
        "routing_examples": "/routing/examples - Exemplos de uso",
        "health": "/health - Status da API"
    }
    
    return {
        "name": "Escrita Sincerta LLM Pro",
        "version": "2.0.0",
        "description": "API Orquestradora com Sistema de Roteamento Inteligente e Agentes Especializados",
        "features": features_list,
        "endpoints": endpoints_dict,
        "agents": [
            "ideator - Ideação de SaaS e análise de mercado",
            "architect - Arquitetura de sistemas e tecnologias",
            "builder - Scaffolding e templates multi-framework",
            "dev_fullstack - Desenvolvimento geral",
            "reflexivo - Análise e planejamento estratégico"
        ],
        "capabilities": {
            "voice_processing": False,
            "rag_system": True,
            "intelligent_routing": True,
            "specialized_agents": 5
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
