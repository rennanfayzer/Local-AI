import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import asyncio
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"

class TaskType(Enum):
    IDEATION = "ideation"
    ARCHITECTURE = "architecture"
    CODING = "coding"
    DEBUGGING = "debugging"
    ANALYSIS = "analysis"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class ModelCapability(Enum):
    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    TECHNICAL = "technical"

class AdvancedRouter:
    """
    Sistema inteligente de roteamento de modelos
    
    Funcionalidades:
    - Análise automática de complexidade da tarefa
    - Seleção otimizada de modelo baseada no contexto
    - Load balancing entre modelos disponíveis
    - Fallback automático em caso de falha
    - Métricas de performance por modelo
    - Cache inteligente de decisões
    """
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Configuração de modelos disponíveis
        self.model_configs = {
            "phi3:3.8b": {
                "capabilities": [ModelCapability.GENERAL, ModelCapability.CODING],
                "max_complexity": TaskComplexity.MEDIUM,
                "strengths": ["fast", "efficient", "code_generation"],
                "weaknesses": ["limited_context", "simple_reasoning"],
                "performance_score": 7.5,
                "resource_usage": "low"
            },
            "qwen2.5:7b": {
                "capabilities": [ModelCapability.GENERAL, ModelCapability.REASONING, ModelCapability.TECHNICAL],
                "max_complexity": TaskComplexity.COMPLEX,
                "strengths": ["reasoning", "multilingual", "technical_knowledge"],
                "weaknesses": ["slower", "resource_intensive"],
                "performance_score": 8.5,
                "resource_usage": "medium"
            },
            "llama3.1:8b-instruct": {
                "capabilities": [ModelCapability.GENERAL, ModelCapability.CREATIVE, ModelCapability.ANALYTICAL],
                "max_complexity": TaskComplexity.EXPERT,
                "strengths": ["creative", "analytical", "instruction_following"],
                "weaknesses": ["resource_intensive", "slower_startup"],
                "performance_score": 9.0,
                "resource_usage": "high"
            },
            "codegemma:7b": {
                "capabilities": [ModelCapability.CODING, ModelCapability.TECHNICAL],
                "max_complexity": TaskComplexity.EXPERT,
                "strengths": ["code_generation", "debugging", "technical_accuracy"],
                "weaknesses": ["limited_general_knowledge", "narrow_focus"],
                "performance_score": 9.2,
                "resource_usage": "medium"
            }
        }
        
        # Mapeamento de tipos de tarefa para capabilities
        self.task_capability_mapping = {
            TaskType.IDEATION: [ModelCapability.CREATIVE, ModelCapability.GENERAL],
            TaskType.ARCHITECTURE: [ModelCapability.TECHNICAL, ModelCapability.REASONING],
            TaskType.CODING: [ModelCapability.CODING, ModelCapability.TECHNICAL],
            TaskType.DEBUGGING: [ModelCapability.CODING, ModelCapability.ANALYTICAL],
            TaskType.ANALYSIS: [ModelCapability.ANALYTICAL, ModelCapability.REASONING],
            TaskType.DOCUMENTATION: [ModelCapability.GENERAL, ModelCapability.TECHNICAL],
            TaskType.TESTING: [ModelCapability.CODING, ModelCapability.ANALYTICAL],
            TaskType.DEPLOYMENT: [ModelCapability.TECHNICAL, ModelCapability.GENERAL]
        }
        
        # Cache de decisões e métricas
        self.routing_cache = {}
        self.model_metrics = {model: {"success_rate": 1.0, "avg_response_time": 0, "total_requests": 0} 
                             for model in self.model_configs.keys()}
        
        # Keywords para detecção automática de tipo e complexidade
        self.complexity_keywords = {
            TaskComplexity.SIMPLE: [
                "simples", "básico", "rápido", "pequeno", "fácil", "direto",
                "simple", "basic", "quick", "small", "easy", "straightforward"
            ],
            TaskComplexity.MEDIUM: [
                "médio", "moderado", "padrão", "normal", "típico",
                "medium", "moderate", "standard", "normal", "typical", "regular"
            ],
            TaskComplexity.COMPLEX: [
                "complexo", "avançado", "detalhado", "completo", "robusto",
                "complex", "advanced", "detailed", "complete", "robust", "comprehensive"
            ],
            TaskComplexity.EXPERT: [
                "expert", "especialista", "enterprise", "profissional", "produção",
                "expert", "specialist", "enterprise", "professional", "production", "scalable"
            ]
        }
        
        self.task_type_keywords = {
            TaskType.IDEATION: [
                "ideia", "brainstorm", "criativo", "inovação", "conceito",
                "idea", "brainstorm", "creative", "innovation", "concept", "generate"
            ],
            TaskType.ARCHITECTURE: [
                "arquitetura", "design", "estrutura", "sistema", "padrão",
                "architecture", "design", "structure", "system", "pattern", "blueprint"
            ],
            TaskType.CODING: [
                "código", "programar", "implementar", "desenvolver", "build",
                "code", "program", "implement", "develop", "build", "create"
            ],
            TaskType.DEBUGGING: [
                "debug", "erro", "bug", "consertar", "corrigir", "problema",
                "debug", "error", "bug", "fix", "correct", "problem", "issue"
            ],
            TaskType.ANALYSIS: [
                "análise", "analisar", "revisar", "examinar", "avaliar",
                "analysis", "analyze", "review", "examine", "evaluate", "assess"
            ],
            TaskType.DOCUMENTATION: [
                "documentação", "documenta", "readme", "docs", "manual",
                "documentation", "document", "readme", "docs", "manual", "guide"
            ]
        }
    
    async def get_available_models(self) -> List[str]:
        """Obtém lista de modelos disponíveis no Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        available = [model["name"] for model in data.get("models", [])]
                        # Filter only configured models that are available
                        return [model for model in self.model_configs.keys() if model in available]
                    return list(self.model_configs.keys())  # Fallback
        except Exception as e:
            logger.warning(f"Could not fetch available models: {e}")
            return list(self.model_configs.keys())
    
    def analyze_task_complexity(self, message: str, context: Dict[str, Any] = None) -> TaskComplexity:
        """Analisa a complexidade da tarefa baseada no conteúdo"""
        message_lower = message.lower()
        
        # Score-based complexity detection
        complexity_scores = {complexity: 0 for complexity in TaskComplexity}
        
        for complexity, keywords in self.complexity_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    complexity_scores[complexity] += 1
        
        # Context-based complexity indicators
        if context:
            project_size = context.get("project_size", "medium")
            if project_size in ["enterprise", "large"]:
                complexity_scores[TaskComplexity.EXPERT] += 2
            elif project_size in ["startup", "medium"]:
                complexity_scores[TaskComplexity.COMPLEX] += 1
        
        # Length-based complexity (longer messages tend to be more complex)
        if len(message) > 500:
            complexity_scores[TaskComplexity.COMPLEX] += 1
        elif len(message) > 1000:
            complexity_scores[TaskComplexity.EXPERT] += 1
        
        # Technical indicators
        technical_indicators = [
            "microservices", "kubernetes", "docker", "ci/cd", "terraform",
            "scalability", "performance", "security", "enterprise", "production"
        ]
        for indicator in technical_indicators:
            if indicator in message_lower:
                complexity_scores[TaskComplexity.EXPERT] += 1
        
        # Return complexity with highest score
        return max(complexity_scores, key=complexity_scores.get) or TaskComplexity.MEDIUM
    
    def analyze_task_type(self, message: str, context: Dict[str, Any] = None) -> TaskType:
        """Analisa o tipo da tarefa baseada no conteúdo"""
        message_lower = message.lower()
        
        # Score-based task type detection
        type_scores = {task_type: 0 for task_type in TaskType}
        
        for task_type, keywords in self.task_type_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    type_scores[task_type] += 1
        
        # Context-based task type indicators
        if context:
            agent_name = context.get("agent", "")
            if agent_name == "ideator":
                type_scores[TaskType.IDEATION] += 3
            elif agent_name == "architect":
                type_scores[TaskType.ARCHITECTURE] += 3
            elif agent_name == "builder":
                type_scores[TaskType.CODING] += 3
            elif agent_name == "dev_fullstack":
                type_scores[TaskType.CODING] += 2
            elif agent_name == "reflexivo":
                type_scores[TaskType.ANALYSIS] += 3
        
        # Return task type with highest score
        return max(type_scores, key=type_scores.get) or TaskType.CODING
    
    def calculate_model_score(self, model: str, task_type: TaskType, complexity: TaskComplexity, context: Dict[str, Any] = None) -> float:
        """Calcula score do modelo para uma tarefa específica"""
        if model not in self.model_configs:
            return 0.0
        
        config = self.model_configs[model]
        score = 0.0
        
        # Base performance score (0-10)
        score += config["performance_score"]
        
        # Capability match bonus (0-5)
        required_capabilities = self.task_capability_mapping.get(task_type, [])
        capability_matches = len(set(config["capabilities"]) & set(required_capabilities))
        score += capability_matches * 2.5
        
        # Complexity handling (0-3)
        complexity_values = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MEDIUM: 2,
            TaskComplexity.COMPLEX: 3,
            TaskComplexity.EXPERT: 4
        }
        
        model_max_complexity = complexity_values[config["max_complexity"]]
        task_complexity = complexity_values[complexity]
        
        if model_max_complexity >= task_complexity:
            score += 3.0  # Can handle complexity
        else:
            score -= (task_complexity - model_max_complexity) * 2  # Penalty for insufficient capability
        
        # Historical performance bonus/penalty (-2 to +2)
        metrics = self.model_metrics[model]
        if metrics["total_requests"] > 0:
            # Success rate impact
            score += (metrics["success_rate"] - 0.8) * 10  # Bonus for >80% success rate
            
            # Response time impact (faster is better)
            if metrics["avg_response_time"] < 5.0:  # < 5 seconds is good
                score += 1.0
            elif metrics["avg_response_time"] > 15.0:  # > 15 seconds is slow
                score -= 1.0
        
        # Resource usage consideration
        if context and context.get("prefer_fast", False):
            if config["resource_usage"] == "low":
                score += 2.0
            elif config["resource_usage"] == "high":
                score -= 1.0
        
        return max(score, 0.0)
    
    async def select_optimal_model(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Seleciona o modelo otimizado para a tarefa"""
        
        # Analyze task characteristics
        task_complexity = self.analyze_task_complexity(message, context)
        task_type = self.analyze_task_type(message, context)
        
        # Get available models
        available_models = await self.get_available_models()
        
        if not available_models:
            # Fallback to default model
            default_model = os.getenv("GENERAL_MODEL", "qwen2.5:7b")
            logger.warning(f"No models available, using default: {default_model}")
            return default_model, {"reason": "fallback_default"}
        
        # Calculate scores for each available model
        model_scores = {}
        for model in available_models:
            score = self.calculate_model_score(model, task_type, task_complexity, context)
            model_scores[model] = score
        
        # Select best model
        best_model = max(model_scores, key=model_scores.get)
        best_score = model_scores[best_model]
        
        # Routing decision metadata
        routing_info = {
            "selected_model": best_model,
            "task_type": task_type.value,
            "task_complexity": task_complexity.value,
            "model_score": best_score,
            "all_scores": model_scores,
            "available_models": available_models,
            "timestamp": datetime.now().isoformat(),
            "reason": "optimal_selection"
        }
        
        logger.info(f"Router selected {best_model} (score: {best_score:.2f}) for {task_type.value}/{task_complexity.value} task")
        
        return best_model, routing_info
    
    async def route_request(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        """Rota uma requisição para o modelo apropriado com fallback"""
        try:
            # Check cache first (optional optimization)
            cache_key = hash(message + str(sorted((context or {}).items())))
            if cache_key in self.routing_cache:
                cached_result = self.routing_cache[cache_key]
                logger.debug(f"Using cached routing decision for model: {cached_result[0]}")
                return cached_result
            
            # Select optimal model
            selected_model, routing_info = await self.select_optimal_model(message, context)
            
            # Verify model availability
            if not await self.is_model_available(selected_model):
                # Fallback to next best available model
                logger.warning(f"Selected model {selected_model} not available, trying fallback")
                fallback_model = await self.get_fallback_model(selected_model)
                if fallback_model:
                    selected_model = fallback_model
                    routing_info["reason"] = "fallback_used"
                else:
                    # Use default fallback
                    selected_model = os.getenv("GENERAL_MODEL", "qwen2.5:7b")
                    routing_info["reason"] = "fallback_default"
            
            # Cache the decision (with some TTL logic if needed)
            self.routing_cache[cache_key] = (selected_model, routing_info)
            
            return selected_model, routing_info
            
        except Exception as e:
            logger.error(f"Error in routing request: {e}")
            # Emergency fallback
            fallback_model = os.getenv("GENERAL_MODEL", "qwen2.5:7b")
            return fallback_model, {"reason": "error_fallback", "error": str(e)}
    
    async def is_model_available(self, model: str) -> bool:
        """Verifica se um modelo está disponível"""
        try:
            async with aiohttp.ClientSession() as session:
                test_payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "test"}],
                    "stream": False
                }
                async with session.post(f"{self.ollama_url}/api/chat", 
                                       json=test_payload, 
                                       timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
    
    async def get_fallback_model(self, unavailable_model: str) -> Optional[str]:
        """Obtém modelo de fallback baseado nas capacidades"""
        if unavailable_model not in self.model_configs:
            return None
        
        unavailable_config = self.model_configs[unavailable_model]
        unavailable_capabilities = unavailable_config["capabilities"]
        
        # Find best fallback with similar capabilities
        best_fallback = None
        best_capability_overlap = 0
        
        available_models = await self.get_available_models()
        
        for model in available_models:
            if model == unavailable_model:
                continue
            
            model_capabilities = self.model_configs[model]["capabilities"]
            overlap = len(set(unavailable_capabilities) & set(model_capabilities))
            
            if overlap > best_capability_overlap:
                best_capability_overlap = overlap
                best_fallback = model
        
        return best_fallback
    
    def update_model_metrics(self, model: str, success: bool, response_time: float):
        """Atualiza métricas de performance do modelo"""
        if model not in self.model_metrics:
            self.model_metrics[model] = {"success_rate": 1.0, "avg_response_time": 0, "total_requests": 0}
        
        metrics = self.model_metrics[model]
        
        # Update success rate (exponential moving average)
        current_success_rate = metrics["success_rate"]
        new_success_rate = 0.9 * current_success_rate + 0.1 * (1.0 if success else 0.0)
        metrics["success_rate"] = new_success_rate
        
        # Update average response time
        current_avg = metrics["avg_response_time"]
        total_requests = metrics["total_requests"]
        new_avg = (current_avg * total_requests + response_time) / (total_requests + 1)
        metrics["avg_response_time"] = new_avg
        
        # Update request count
        metrics["total_requests"] += 1
        
        logger.debug(f"Updated metrics for {model}: success_rate={new_success_rate:.2f}, avg_time={new_avg:.2f}s")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de roteamento"""
        return {
            "model_metrics": self.model_metrics,
            "cache_size": len(self.routing_cache),
            "available_models": list(self.model_configs.keys()),
            "total_routes": sum(m["total_requests"] for m in self.model_metrics.values())
        }


# Singleton instance
_router_instance = None

def get_router() -> AdvancedRouter:
    """Obtém instância singleton do router"""
    global _router_instance
    if _router_instance is None:
        _router_instance = AdvancedRouter()
    return _router_instance