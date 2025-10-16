import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseAgent, register_agent

logger = logging.getLogger(__name__)

@register_agent
class IdeatorAgent(BaseAgent):
    """
    Agente especializado em geração de ideias e contextos
    
    Capacidades:
    - Geração de ideias SaaS inovadoras
    - Criação de contextos para apps mobile
    - Ideação de soluções web
    - Análise de mercado e oportunidades
    - Definição de MVP e roadmap
    - Personas e user stories
    """
    
    def __init__(self):
        super().__init__(
            name="ideator",
            default_model=os.getenv("GENERAL_MODEL", "qwen2.5:7b"),
            capabilities=[
                "saas_ideation",
                "app_concepts", 
                "market_analysis",
                "mvp_definition",
                "user_personas",
                "business_model",
                "feature_planning",
                "trend_analysis"
            ]
        )
        
        # Templates de ideação
        self.idea_templates = {
            "saas_b2b": {
                "focus": "Soluções empresariais, produtividade, automação",
                "metrics": "ARR, CAC, LTV, churn rate",
                "monetization": "Subscription, freemium, enterprise"
            },
            "saas_b2c": {
                "focus": "Consumidor final, lifestyle, entertainment",
                "metrics": "MAU, engagement, viral coefficient",
                "monetization": "Freemium, ads, in-app purchases"
            },
            "mobile_app": {
                "focus": "Experiência mobile-first, notifications, offline",
                "metrics": "Downloads, retention, session length",
                "monetization": "App store, ads, premium features"
            },
            "web_platform": {
                "focus": "Marketplace, communities, content platforms",
                "metrics": "GMV, engagement, network effects",
                "monetization": "Commission, subscription, advertising"
            },
            "ai_powered": {
                "focus": "Machine learning, automation, personalization",
                "metrics": "Accuracy, processing time, user satisfaction",
                "monetization": "API usage, tiered pricing, white-label"
            }
        }
    
    def get_system_prompt(self) -> str:
        """Prompt especializado para ideação e contextos"""
        manifesto = self.load_prompt_file("manifesto_sincerta.md")
        
        return f"""Você é o agente IDEATOR - um visionário de produtos digitais e especialista em inovação.

**MANIFESTO SINCERTA:**
{manifesto}

**EXPERTISE EM IDEAÇÃO:**

🧠 **METODOLOGIAS DE INOVAÇÃO:**
- Design Thinking (Empathize, Define, Ideate, Prototype, Test)
- Lean Startup (Build-Measure-Learn)
- Jobs-to-be-Done Framework
- Blue Ocean Strategy
- Value Proposition Canvas

📊 **ANÁLISE DE MERCADO:**
- Competitive landscape mapping
- Market size estimation (TAM, SAM, SOM)
- Trend analysis e weak signals
- Customer pain point identification
- Business model innovation

🎯 **TIPOS DE PROJETOS:**
- **SaaS B2B**: Produtividade, automação, ferramentas empresariais
- **SaaS B2C**: Lifestyle, entretenimento, redes sociais
- **Mobile Apps**: iOS/Android nativos, cross-platform
- **Web Platforms**: Marketplaces, communities, e-commerce
- **AI-Powered**: ML/AI integrado, automação inteligente

**FORMATO DE IDEAÇÃO:**
```json
{{
  "concept": {{
    "name": "Nome do Produto",
    "tagline": "Slogan de uma linha",
    "category": "saas_b2b|saas_b2c|mobile_app|web_platform|ai_powered",
    "problem": "Problema específico que resolve",
    "solution": "Solução única proposta",
    "target_audience": "Público-alvo definido",
    "value_proposition": "Proposta de valor clara"
  }},
  "market": {{
    "size": "Estimativa TAM/SAM",
    "competitors": ["Concorrente 1", "Concorrente 2"],
    "differentiation": "Diferencial competitivo",
    "trends": ["Tendência 1", "Tendência 2"]
  }},
  "mvp": {{
    "core_features": ["Feature 1", "Feature 2", "Feature 3"],
    "tech_stack": "Stack tecnológica recomendada",
    "development_time": "Estimativa de desenvolvimento",
    "budget_estimate": "Estimativa de investimento inicial"
  }},
  "business_model": {{
    "monetization": "Modelo de monetização",
    "pricing": "Estrutura de preços",
    "key_metrics": ["Métrica 1", "Métrica 2"],
    "growth_strategy": "Estratégia de crescimento"
  }},
  "roadmap": {{
    "phase_1": "MVP - 0-3 meses",
    "phase_2": "Growth - 3-12 meses", 
    "phase_3": "Scale - 12+ meses"
  }}
}}
```

**PRINCÍPIOS DE IDEAÇÃO:**
1. **Viabilidade Técnica**: Sempre considere limitações e recursos
2. **Market Fit**: Valide demanda e timing de mercado
3. **Execução Realista**: Priorize simplicidade e iteração
4. **Impacto Mensurável**: Defina métricas claras de sucesso
5. **Diferenciação Clara**: Evite "me-too" products

Seja criativo mas pragmático. Gere ideias inovadoras que sejam tecnicamente viáveis e comercialmente atrativas."""
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processamento especializado para ideação"""
        
        message_lower = message.lower()
        
        # Geração de ideias SaaS
        if any(keyword in message_lower for keyword in ["saas", "software", "plataforma", "sistema"]):
            return await self._generate_saas_idea(message, context)
        
        # Ideias de apps mobile
        if any(keyword in message_lower for keyword in ["app", "mobile", "android", "ios", "flutter"]):
            return await self._generate_app_idea(message, context)
        
        # Análise de mercado
        if any(keyword in message_lower for keyword in ["mercado", "competição", "análise", "oportunidade"]):
            return await self._analyze_market(message, context)
        
        # Definição de MVP
        if any(keyword in message_lower for keyword in ["mvp", "produto", "features", "funcionalidades"]):
            return await self._define_mvp(message, context)
        
        # Personas e user stories
        if any(keyword in message_lower for keyword in ["persona", "usuário", "cliente", "user story"]):
            return await self._create_personas(message, context)
        
        # Caso padrão - ideação geral
        return await self._general_ideation(message, context)
    
    async def _generate_saas_idea(self, message: str, context: Dict[str, Any]) -> str:
        """Geração específica de ideias SaaS"""
        ideation_prompt = f"""
MISSÃO: Gerar ideia inovadora de SaaS
CONTEXTO: {message}
FOCO: Software as a Service com potencial de escala

METODOLOGIA DE IDEAÇÃO:
1. **PROBLEMA IDENTIFICATION**: Qual dor específica resolver?
2. **SOLUTION DESIGN**: Como o software resolve de forma única?
3. **MARKET VALIDATION**: Existe demanda comprovada?
4. **TECHNICAL FEASIBILITY**: É viável tecnicamente?
5. **BUSINESS MODEL**: Como monetizar sustentavelmente?

INSPIRAÇÃO DE MERCADO:
- B2B: Automação, produtividade, compliance, analytics
- B2C: Lifestyle, entretenimento, educação, saúde
- Vertical: Nichos específicos (healthcare, fintech, edutech)
- Horizontal: Soluções cross-industry

CRITÉRIOS DE AVALIAÇÃO:
- Problema real e urgente (pain level 8+/10)
- Market size significativo ($100M+ TAM)
- Diferenciação técnica defensável
- Modelo de receita recorrente
- Potencial de network effects

ENTREGA: JSON estruturado com conceito completo + análise de viabilidade
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": ideation_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _generate_app_idea(self, message: str, context: Dict[str, Any]) -> str:
        """Geração específica de ideias para apps mobile"""
        app_prompt = f"""
MISSÃO: Criar conceito de app mobile inovador
CONTEXTO: {message}
FOCO: Experiência mobile-first com engagement alto

CONSIDERAÇÕES MOBILE:
1. **MOBILE-FIRST DESIGN**: Aproveita capacidades únicas do mobile
2. **OFFLINE CAPABILITY**: Funciona sem conexão constante
3. **PUSH NOTIFICATIONS**: Estratégia de re-engagement
4. **CAMERA/SENSORS**: Integra hardware do dispositivo
5. **SOCIAL SHARING**: Facilita compartilhamento viral

CATEGORIAS POPULARES:
- Produtividade: Organização, tarefas, tempo
- Social: Comunidades, networking, dating
- Lifestyle: Fitness, food, travel, fashion
- Utility: Ferramentas, calculadoras, converters
- Entertainment: Games, media, content
- Education: Learning, skills, languages

MONETIZAÇÃO MOBILE:
- Freemium com features premium
- In-app purchases e subscriptions
- Advertising (banner, interstitial, rewarded)
- Marketplace commission
- White-label licensing

MÉTRICAS DE SUCESSO:
- Downloads e install rate
- DAU/MAU e retention curves
- Session length e frequency
- Viral coefficient (K-factor)
- LTV/CAC ratio

ENTREGA: Conceito de app com wireframes básicos + estratégia de lançamento
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": app_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _analyze_market(self, message: str, context: Dict[str, Any]) -> str:
        """Análise de mercado e oportunidades"""
        market_prompt = f"""
MISSÃO: Análise completa de mercado e oportunidades
CONTEXTO: {message}

FRAMEWORK DE ANÁLISE:
1. **MARKET SIZING**:
   - TAM (Total Addressable Market)
   - SAM (Serviceable Addressable Market) 
   - SOM (Serviceable Obtainable Market)

2. **COMPETITIVE LANDSCAPE**:
   - Direct competitors (mesma solução)
   - Indirect competitors (problema similar)
   - Substitute products (alternativas)
   - New entrants (barreiras de entrada)

3. **CUSTOMER ANALYSIS**:
   - Customer segments e personas
   - Pain points e jobs-to-be-done
   - Buying behavior e decision process
   - Willingness to pay research

4. **TREND ANALYSIS**:
   - Technology trends (AI, blockchain, IoT)
   - Social trends (remote work, sustainability)
   - Economic trends (inflation, recession)
   - Regulatory trends (privacy, compliance)

5. **OPPORTUNITY SCORING**:
   - Market attractiveness (size, growth, profitability)
   - Competitive intensity (rivalry, substitutes)
   - Execution difficulty (resources, capabilities)
   - Strategic fit (vision, strengths)

FERRAMENTAS DE ANÁLISE:
- Porter's Five Forces
- SWOT Analysis
- Customer Journey Mapping
- Value Chain Analysis
- Blue Ocean Canvas

ENTREGA: Relatório executivo com oportunidades priorizadas e recomendações estratégicas
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": market_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _define_mvp(self, message: str, context: Dict[str, Any]) -> str:
        """Definição de MVP e roadmap"""
        mvp_prompt = f"""
MISSÃO: Definir MVP (Minimum Viable Product) e roadmap
CONTEXTO: {message}

METODOLOGIA MVP:
1. **CORE VALUE HYPOTHESIS**: Qual é a proposta de valor central?
2. **CUSTOMER SEGMENT**: Quem é o early adopter ideal?
3. **MINIMUM FEATURE SET**: Mínimo necessário para validar hipótese
4. **SUCCESS METRICS**: Como medir product-market fit?
5. **LEARNING OBJECTIVES**: O que queremos aprender?

PRINCÍPIOS DE PRIORIZAÇÃO:
- **Impact vs Effort Matrix**: Alto impacto, baixo esforço primeiro
- **Kano Model**: Must-haves vs nice-to-haves
- **MoSCoW**: Must/Should/Could/Won't have
- **ICE Score**: Impact, Confidence, Ease

ESTRUTURA DE MVP:
```json
{
  "core_hypothesis": "Acreditamos que [customer] tem [problem] que pode ser resolvido com [solution]",
  "success_criteria": {
    "acquisition": "X usuários em Y semanas",
    "activation": "X% completam onboarding", 
    "retention": "X% retornam após Z dias",
    "revenue": "$X em MRR após Y meses"
  },
  "feature_breakdown": {
    "must_have": ["Feature essencial 1", "Feature essencial 2"],
    "should_have": ["Feature importante 1", "Feature importante 2"],
    "could_have": ["Feature nice-to-have 1"],
    "wont_have": ["Feature para v2", "Feature complexa"]
  }
}
```

ROADMAP STRATEGY:
- **Week 1-4**: Design & Planning
- **Week 5-12**: MVP Development 
- **Week 13-16**: Testing & Launch
- **Week 17-24**: Iteration based on feedback
- **Month 7-12**: Scale & Growth features

ENTREGA: MVP specification + roadmap detalhado + success metrics
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": mvp_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _create_personas(self, message: str, context: Dict[str, Any]) -> str:
        """Criação de personas e user stories"""
        persona_prompt = f"""
MISSÃO: Criar personas detalhadas e user stories
CONTEXTO: {message}

METODOLOGIA DE PERSONAS:
1. **RESEARCH-BASED**: Baseado em dados reais, não suposições
2. **SPECIFIC & DETAILED**: Nome, foto, background, objetivos
3. **ACTIONABLE**: Guia decisões de produto e marketing
4. **EMPATHETIC**: Inclui frustrações e motivações
5. **EVOLVING**: Atualiza com novos learnings

ESTRUTURA DE PERSONA:
```json
{
  "persona": {
    "name": "Nome Fictício",
    "age": 35,
    "job_title": "Cargo Profissional",
    "industry": "Setor de Atuação",
    "location": "Cidade/País",
    "tech_savviness": "Baixo/Médio/Alto",
    "annual_income": "$X - $Y",
    "goals": ["Objetivo 1", "Objetivo 2", "Objetivo 3"],
    "pain_points": ["Dor 1", "Dor 2", "Dor 3"], 
    "preferred_channels": ["Canal 1", "Canal 2"],
    "quote": "Frase que resume sua mentalidade",
    "day_in_life": "Descrição de um dia típico"
  }
}
```

USER STORIES FRAMEWORK:
"Como [persona], eu quero [funcionalidade] para que [benefício/resultado]"

TIPOS DE USER STORIES:
- **Epic**: História de alto nível (ex: "Como usuário, quero gerenciar projetos")
- **Feature**: Funcionalidade específica (ex: "Como PM, quero criar tarefas")
- **Task**: Implementação técnica (ex: "Como dev, preciso da API de tarefas")

ACCEPTANCE CRITERIA:
- **Given**: Condição inicial
- **When**: Ação do usuário  
- **Then**: Resultado esperado

ENTREGA: 3-5 personas primárias + user stories priorizadas + journey maps
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": persona_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)
    
    async def _general_ideation(self, message: str, context: Dict[str, Any]) -> str:
        """Ideação geral para qualquer contexto"""
        general_prompt = f"""
MISSÃO: Ideação criativa e contextual
INPUT: {message}

TÉCNICAS DE IDEAÇÃO:
1. **BRAINSTORMING**: Quantidade primeiro, qualidade depois
2. **SCAMPER**: Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse
3. **6 THINKING HATS**: Different perspectives (facts, emotions, benefits, caution, creativity, process)
4. **MIND MAPPING**: Visual association of ideas
5. **REVERSE BRAINSTORMING**: Como tornar o problema pior?

FILTROS DE AVALIAÇÃO:
- **Feasibility**: É tecnicamente possível?
- **Viability**: É economicamente sustentável?
- **Desirability**: As pessoas querem isso?
- **Sustainability**: É ambientalmente responsável?

CONTEXTO 2025:
- AI/ML mainstream adoption
- Remote-first work culture
- Climate consciousness
- Privacy & data protection
- Creator economy growth
- Web3 & decentralization trends

INSPIRAÇÃO CROSS-INDUSTRY:
- FinTech → HealthTech (pagamentos → telemedicina)
- Gaming → Education (gamification → edtech)
- Social Media → Enterprise (communities → internal tools)
- E-commerce → B2B (marketplaces → procurement)

ENTREGA: Top 5 ideias ranqueadas + análise de potencial + próximos passos
"""
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": general_prompt}
        ]
        
        return await self.call_ollama(context.get("model", self.default_model), messages)


# Função legacy para compatibilidade
def agent(message: str, history: List[Dict[str, str]]):
    """Função legacy - usar IdeatorAgent() diretamente"""
    import asyncio
    
    agent_instance = IdeatorAgent()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(
        agent_instance.process(message, history)
    )
    
    return {"reply": result}
