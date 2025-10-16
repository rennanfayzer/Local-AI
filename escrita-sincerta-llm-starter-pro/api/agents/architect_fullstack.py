import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, register_agent

logger = logging.getLogger(__name__)

@register_agent
class ArchitectFullstackAgent(BaseAgent):
    """
    Agente especializado em arquitetura fullstack
    
    Capacidades:
    - Arquitetura de sistemas distribuídos
    - Design patterns e best practices
    - Stack technology selection
    - Infrastructure as Code
    - Microservices e monolith decisions
    - Performance e scalability
    """
    
    def __init__(self):
        super().__init__(
            name="architect",
            default_model=os.getenv("ARCHITECT_MODEL", "qwen2.5:7b"),
            capabilities=[
                "system_architecture",
                "technology_selection", 
                "database_design",
                "api_design",
                "infrastructure_planning",
                "performance_optimization",
                "security_architecture",
                "deployment_strategy"
            ]
        )
        
        # Technology stacks pré-definidos
        self.tech_stacks = {
            "modern_web": {
                "frontend": ["React", "Next.js", "TypeScript", "Tailwind CSS"],
                "backend": ["Node.js", "Express", "Fastify", "TypeScript"],
                "database": ["PostgreSQL", "MongoDB", "Redis"],
                "deployment": ["Docker", "Vercel", "Railway", "AWS"],
                "features": ["SSR/SSG", "API routes", "Real-time", "PWA"]
            },
            "python_fullstack": {
                "frontend": ["React", "Vue.js", "Svelte"],
                "backend": ["FastAPI", "Django", "Flask"],
                "database": ["PostgreSQL", "SQLite", "Redis"],
                "deployment": ["Docker", "Heroku", "DigitalOcean", "AWS"],
                "features": ["REST API", "GraphQL", "Async processing", "AI/ML integration"]
            },
            "mobile_first": {
                "mobile": ["Flutter", "React Native", "Expo"],
                "backend": ["Node.js", "Python", "Go"],
                "database": ["Firebase", "Supabase", "PostgreSQL"],
                "deployment": ["Firebase", "App Store", "Play Store"],
                "features": ["Cross-platform", "Offline-first", "Push notifications", "Native performance"]
            },
            "enterprise_saas": {
                "frontend": ["React", "Angular", "TypeScript"],
                "backend": ["Java Spring", "Node.js", ".NET Core"],
                "database": ["PostgreSQL", "MySQL", "Redis", "Elasticsearch"],
                "deployment": ["Kubernetes", "AWS", "Azure", "Docker"],
                "features": ["Multi-tenancy", "RBAC", "Enterprise SSO", "High availability"]
            },
            "startup_mvp": {
                "frontend": ["Next.js", "Vercel"],
                "backend": ["Supabase", "Vercel Functions"],
                "database": ["Supabase PostgreSQL"],
                "deployment": ["Vercel", "One-click deploy"],
                "features": ["Rapid development", "Built-in auth", "Real-time", "Cost-effective"]
            }
        }
    
    def get_system_prompt(self) -> str:
        """Prompt especializado para arquitetura fullstack"""
        manifesto = self.load_prompt_file("manifesto_sincerta.md")
        
        return f"""Você é o agente ARCHITECT - um arquiteto de software sênior especializado em sistemas fullstack modernos.

**MANIFESTO SINCERTA:**
{manifesto}

**EXPERTISE EM ARQUITETURA:**

🏗️ **DESIGN PRINCIPLES:**
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **Separation of Concerns**: Clear boundaries between layers

📊 **ARCHITECTURE STYLES:**
- **Layered Architecture**: Presentation → Business → Data Access → Database
- **Hexagonal Architecture**: Ports and Adapters pattern
- **Clean Architecture**: Dependency inversion, testable core
- **Event-Driven**: Pub/Sub, CQRS, Event Sourcing
- **Microservices**: Distributed, domain-driven boundaries

🛠️ **TECHNOLOGY SELECTION CRITERIA:**
1. **Team Expertise**: Current skills and learning curve
2. **Project Requirements**: Performance, scalability, features
3. **Time to Market**: Development speed vs long-term maintenance
4. **Ecosystem Maturity**: Libraries, tools, community support
5. **Operational Complexity**: Deployment, monitoring, debugging

**FORMATO DE ARQUITETURA:**
```json
{{
  "project_context": {{
    "type": "web_app|mobile_app|api|platform",
    "scale": "mvp|startup|enterprise",
    "team_size": "1-2|3-10|10+",
    "timeline": "weeks|months|quarters"
  }},
  "architecture": {{
    "pattern": "monolith|modular_monolith|microservices|jamstack",
    "reasoning": "Por que esta escolha arquitetural",
    "trade_offs": "Benefícios vs limitações"
  }},
  "tech_stack": {{
    "frontend": {{
      "framework": "React|Vue|Angular|Svelte",
      "language": "JavaScript|TypeScript",
      "styling": "CSS|Sass|Tailwind|Styled-components"
    }},
    "backend": {{
      "framework": "Express|Fastify|FastAPI|Django|Spring",
      "language": "Node.js|Python|Java|C#|Go",
      "api_style": "REST|GraphQL|tRPC"
    }},
    "database": {{
      "primary": "PostgreSQL|MySQL|MongoDB",
      "cache": "Redis|Memcached"
    }},
    "infrastructure": {{
      "hosting": "Vercel|Railway|AWS|GCP|Azure",
      "containers": "Docker|Kubernetes"
    }}
  }},
  "security": {{
    "authentication": "JWT|OAuth|Auth0",
    "authorization": "RBAC|ABAC",
    "data_protection": "Encryption, validation"
  }},
  "deployment": {{
    "strategy": "Blue-green|Rolling|Canary",
    "environments": "dev → staging → production"
  }}
}}
```

Sempre justifique suas decisões arquiteturais com reasoning técnico sólido."""
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processamento especializado para arquitetura"""
        
        message_lower = message.lower()
        
        # Seleção de tecnologia
        if any(keyword in message_lower for keyword in ["stack", "tecnologia", "framework"]):
            return await self._recommend_tech_stack(message, context)
        
        # Design de arquitetura
        if any(keyword in message_lower for keyword in ["arquitetura", "design", "estrutura"]):
            return await self._design_architecture(message, context)
        
        # Design de banco de dados
        if any(keyword in message_lower for keyword in ["banco", "database", "modelo"]):
            return await self._design_database(message, context)
        
        # Design de APIs
        if any(keyword in message_lower for keyword in ["api", "endpoint", "rest"]):
            return await self._design_api(message, context)
        
        # Caso padrão - arquitetura geral
        return await self._general_architecture(message, context)
    
    async def _recommend_tech_stack(self, message: str, context: Dict[str, Any]) -> str:
        """Recomendação de stack tecnológica"""
        stack_prompt = f"""
MISSÃO: Recomendar stack tecnológica otimizada
CONTEXTO: {message}

CRITÉRIOS DE SELEÇÃO:
1. **PROJECT TYPE**: Web app, mobile app, API, platform
2. **TEAM EXPERTISE**: Current skills, learning willingness
3. **TIMELINE**: MVP speed vs long-term maintainability
4. **SCALE REQUIREMENTS**: Users, data, geographic distribution

STACKS RECOMENDADAS:
- **Modern Web**: React/Next.js + Node.js/TypeScript + PostgreSQL
- **Python Fullstack**: React/Vue + FastAPI/Django + PostgreSQL
- **Mobile-First**: Flutter + Firebase/Supabase
- **Enterprise**: React + Java Spring/Node.js + PostgreSQL + Kubernetes
- **Startup MVP**: Next.js + Supabase/Railway

ENTREGA: Stack recomendada + justificativa + roadmap de implementação
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": stack_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _design_architecture(self, message: str, context: Dict[str, Any]) -> str:
        """Design de arquitetura de sistema"""
        architecture_prompt = f"""
MISSÃO: Projetar arquitetura de sistema robusta
CONTEXTO: {message}

PROCESSO DE DESIGN:
1. **REQUIREMENTS ANALYSIS**: Functional, non-functional, constraints
2. **ARCHITECTURE DECISION**: Monolith vs Microservices
3. **COMPONENT DESIGN**: Frontend, backend, database, integrations
4. **COMMUNICATION PATTERNS**: REST, GraphQL, WebSocket, queues

PADRÕES ARQUITETURAIS:
- **Layered Architecture**: Clear separation of concerns
- **Hexagonal Architecture**: Testable, adaptable core
- **Event-Driven Architecture**: Loose coupling, scalability

ENTREGA: Diagrama arquitetural + componentes + decisões técnicas
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": architecture_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _design_database(self, message: str, context: Dict[str, Any]) -> str:
        """Design de banco de dados"""
        database_prompt = f"""
MISSÃO: Projetar esquema de banco de dados otimizado
CONTEXTO: {message}

METODOLOGIA:
1. **CONCEPTUAL MODEL**: Entities, relationships, attributes
2. **LOGICAL MODEL**: Tables, normalization, indexes
3. **PHYSICAL MODEL**: Storage optimization, performance

DATABASE SELECTION:
- **PostgreSQL**: ACID compliance, JSON support, extensibility
- **MongoDB**: Document model, horizontal scaling
- **Redis**: In-memory, caching, real-time features

ENTREGA: Esquema completo + índices + procedures
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": database_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _design_api(self, message: str, context: Dict[str, Any]) -> str:
        """Design de APIs"""
        api_prompt = f"""
MISSÃO: Projetar API robusta e escalável
CONTEXTO: {message}

API DESIGN PRINCIPLES:
1. **RESTful Design**: Resource-based URLs, HTTP methods, status codes
2. **GraphQL Alternative**: Flexible queries, type system
3. **Authentication**: JWT, OAuth, API keys
4. **Performance**: Pagination, caching, rate limiting

ENTREGA: Especificação OpenAPI + auth flow + performance strategy
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": api_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _general_architecture(self, message: str, context: Dict[str, Any]) -> str:
        """Arquitetura geral"""
        general_prompt = f"""
MISSÃO: Arquitetura de software contextual
INPUT: {message}

ANÁLISE ARQUITETURAL:
1. **REQUIREMENT ELICITATION**: Functional, non-functional, constraints
2. **ARCHITECTURE EVALUATION**: Trade-offs, risks, costs
3. **DECISION DOCUMENTATION**: ADRs, rationale, evolution

ENTREGA: Arquitetura completa + justificativas + roadmap
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": general_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)


# Função legacy para compatibilidade
def agent(message: str, history: List[Dict[str, str]]):
    """Função legacy - usar ArchitectFullstackAgent() diretamente"""
    import asyncio
    
    agent_instance = ArchitectFullstackAgent()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(
        agent_instance.process(message, history)
    )
    
    return {"reply": result}
