import os
import logging
from typing import Dict, Any, List
from .base import BaseAgent, register_agent

logger = logging.getLogger(__name__)

@register_agent
class ReflexivoAgent(BaseAgent):
    """
    Agente especializado em análise reflexiva e planejamento
    
    Capacidades:
    - Análise de problemas complexos
    - Decomposição de tarefas 
    - Planejamento estratégico
    - Auto-reflexão e meta-cognição
    - Identificação de riscos e oportunidades
    - Facilitação de tomada de decisão
    """
    
    def __init__(self):
        super().__init__(
            name="reflexivo",
            default_model=os.getenv("REFLEX_MODEL", "phi3:3.8b"),
            capabilities=[
                "analysis",
                "planning", 
                "reflection",
                "risk_assessment",
                "decision_support",
                "problem_decomposition",
                "strategic_thinking"
            ]
        )
    
    def get_system_prompt(self) -> str:
        """Prompt especializado para análise reflexiva"""
        manifesto = self.load_prompt_file("manifesto_sincerta.md")
        
        return f"""Você é o agente REFLEXIVO - um facilitador de pensamento estratégico e análise profunda.

**MANIFESTO SINCERTA:**
{manifesto}

**METODOLOGIA REFLEXIVA:**

1. **ESCUTA ATIVA**: Identifique o problema real por trás da pergunta
2. **ANÁLISE SISTÊMICA**: Explore conexões, dependências e impactos
3. **MÚLTIPLAS PERSPECTIVAS**: Considere diferentes ângulos e stakeholders
4. **PENSAMENTO CRÍTICO**: Questione premissas e identifique vieses
5. **SÍNTESE CONSTRUTIVA**: Transforme insights em ações práticas

**FORMATO DE RESPOSTA:**
```
🎯 PROBLEMA IDENTIFICADO
[Reformulação clara do desafio central]

🔍 ANÁLISE PROFUNDA  
[Fatores, causas raiz, contexto]

⚖️ TRADE-OFFS E RISCOS
[Consequências, limitações, oportunidades]

🚀 PLANO DE AÇÃO
[Passos concretos, priorizados e mensuráveis]

✅ CHECKLIST DE VALIDAÇÃO
[Critérios de sucesso e pontos de verificação]
```

**PRINCÍPIOS:**
- Honestidade brutal com empatia genuína
- Perguntas que provocam insights profundos  
- Foco em soluções práticas e acionáveis
- Reconheça limitações e incertezas
- Stimule auto-reflexão no usuário

Seja um espelho inteligente que revela clareza onde há confusão."""
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processamento especializado para análise reflexiva"""
        
        message_lower = message.lower()
        
        # Análise de problemas
        if any(keyword in message_lower for keyword in ["problema", "dificuldade", "desafio", "bloqueio", "stuck"]):
            return await self._handle_problem_analysis(message, context)
        
        # Planejamento e estratégia
        if any(keyword in message_lower for keyword in ["plano", "estratégia", "como", "passos", "roadmap"]):
            return await self._handle_strategic_planning(message, context)
        
        # Tomada de decisão
        if any(keyword in message_lower for keyword in ["decisão", "escolha", "opção", "dilema", "vs", "ou"]):
            return await self._handle_decision_support(message, context)
        
        # Auto-reflexão
        if any(keyword in message_lower for keyword in ["reflexão", "pensar", "analisar", "entender", "porque"]):
            return await self._handle_self_reflection(message, context)
        
        # Caso padrão
        return None
    
    async def _handle_problem_analysis(self, message: str, context: Dict[str, Any]) -> str:
        """Análise profunda de problemas"""
        analysis_prompt = f"""
MISSÃO: Análise sistêmica de problema
CONTEXTO DO USUÁRIO: {message}

FRAMEWORK DE ANÁLISE:
1. **ROOT CAUSE ANALYSIS**: Vá além dos sintomas
2. **5 WHYS**: Descasque as camadas do problema  
3. **STAKEHOLDER MAPPING**: Quem é impactado e como?
4. **CONSTRAINT THEORY**: Qual é o gargalo real?
5. **SYSTEMS THINKING**: Como as partes se conectam?

PERGUNTAS REFLEXIVAS:
- O que você realmente quer alcançar?
- Que premissas podem estar erradas?  
- Qual é o custo de NÃO resolver isso?
- Onde você já teve sucesso com problemas similares?

ENTREGA: Reformulação do problema + análise de causas + plano inicial
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": analysis_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_strategic_planning(self, message: str, context: Dict[str, Any]) -> str:
        """Planejamento estratégico e roadmaps"""
        planning_prompt = f"""
MISSÃO: Planejamento estratégico e execução
CONTEXTO: {message}

METODOLOGIA ESTRATÉGICA:
1. **VISÃO CLARA**: Onde queremos chegar?
2. **SITUAÇÃO ATUAL**: Onde estamos agora? (gap analysis)
3. **RECURSOS**: Tempo, pessoas, budget, conhecimento
4. **RISCOS**: O que pode dar errado? Planos B/C
5. **MILESTONES**: Marcos mensuráveis e deadlines
6. **SUCCESS METRICS**: Como medir progresso?

FRAMEWORK DE PRIORIZAÇÃO:
- IMPACT vs EFFORT matrix
- MoSCoW (Must/Should/Could/Won't)
- ICE Score (Impact, Confidence, Ease)

TÉCNICAS DE EXECUÇÃO:
- Timeboxing e sprints
- Feedback loops rápidos  
- Fail fast, learn faster
- Progressive disclosure

ENTREGA: Roadmap detalhado + critérios de sucesso + plano de contingência
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": planning_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_decision_support(self, message: str, context: Dict[str, Any]) -> str:
        """Suporte à tomada de decisão"""
        decision_prompt = f"""
MISSÃO: Facilitação de tomada de decisão
DILEMA: {message}

FRAMEWORK DE DECISÃO:
1. **CLARIFICAÇÃO**: Qual decisão precisa ser tomada? Por quando?
2. **CRITÉRIOS**: Que fatores são importantes? (peso relativo)
3. **ALTERNATIVAS**: Quais são todas as opções? (incluindo não-óbvias)
4. **CONSEQUÊNCIAS**: Cenários otimista/realista/pessimista
5. **REVERSIBILIDADE**: Decisions are 1-way or 2-way doors?
6. **STAKEHOLDERS**: Quem precisa comprar a ideia?

TÉCNICAS ANALÍTICAS:
- Pros/Cons weighted matrix
- Decision trees para cenários complexos  
- Regret minimization framework
- 10-10-10 rule (10 min/months/years impact)

VIESES COGNITIVOS A EVITAR:
- Anchoring bias (primeira opção)
- Confirmation bias (só dados favoráveis)
- Sunk cost fallacy (investimento passado)
- Analysis paralysis (perfection over progress)

ENTREGA: Matriz de decisão + recomendação fundamentada + plano de implementação
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": decision_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _handle_self_reflection(self, message: str, context: Dict[str, Any]) -> str:
        """Facilitação de auto-reflexão"""
        reflection_prompt = f"""
MISSÃO: Facilitação de auto-reflexão e insight
TÓPICO: {message}

PERGUNTAS SOCRÁTICAS:
- O que você realmente sabe vs assume sobre isso?
- Que evidências sustentam sua perspectiva?
- Como alguém com visão oposta argumentaria?
- Que padrões você reconhece em situações similares?
- O que você aprendeu da última vez que enfrentou isso?

METACOGNIÇÃO:
- Como você está pensando sobre esse problema?
- Que emoções estão influenciando sua análise?
- Onde você pode estar sendo seu pior inimigo?
- Que recursos internos você já possui mas não está usando?

FRAMEWORK DE GROWTH MINDSET:
- Desafios → Oportunidades de crescimento
- Obstáculos → Feedback para ajustar estratégia  
- Esforço → Caminho para maestria
- Críticas → Fonte de insights valiosos
- Sucesso dos outros → Inspiração e aprendizado

ENTREGA: Insights profundos + blind spots revelados + plano de desenvolvimento pessoal
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": reflection_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)


# Função legacy para compatibilidade
def agent(message: str, history: List[Dict[str, str]]):
    """Função legacy - usar ReflexivoAgent() diretamente"""
    import asyncio
    
    agent_instance = ReflexivoAgent()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(
        agent_instance.process(message, history)
    )
    
    return {"reply": result}
