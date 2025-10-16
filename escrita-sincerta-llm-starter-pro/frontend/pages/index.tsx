import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { Send, Edit, PlusCircle, Bot, User, Loader2, Trash2 } from 'lucide-react';

import FileTree from '../components/FileTree';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';


// Tipagem para o plano de execução
interface PlanStep {
  step: number;
  agent: string;
  prompt: string;
  status?: 'pending' | 'in-progress' | 'completed' | 'failed';
}

interface ExecutionPlan {
  goal: string;
  plan: PlanStep[];
}

const HomePage: React.FC = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Olá! Sou seu assistente de IA. Como posso ajudar a construir algo incrível hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [projects, setProjects] = useState<string[]>([]);
  const [currentProjectName, setCurrentProjectName] = useState<string | null>(null);
  const [conversations, setConversations] = useState<string[]>([]);
  const [currentConversationName, setCurrentConversationName] = useState<string | null>(null);
  const [agents, setAgents] = useState<string[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>('orchestrator');
  const [executionPlan, setExecutionPlan] = useState<ExecutionPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.children[0].scrollTop = scrollAreaRef.current.children[0].scrollHeight;
    }
  };

  const handleCreateNewConversation = async () => {
    if (!currentProjectName) {
      alert("Por favor, selecione um projeto primeiro.");
      return;
    }
    const newConversationName = prompt("Digite o nome da nova conversa:");
    if (newConversationName && newConversationName.trim()) {
      try {
        const response = await fetch(`http://localhost:8000/projects/${currentProjectName}/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ conversation_name: newConversationName }),
        });
        if (response.ok) {
          await fetchConversations(currentProjectName);
          setCurrentConversationName(newConversationName);
        } else {
          const errorData = await response.json();
          alert(`Erro ao criar conversa: ${errorData.detail}`);
        }
      } catch (error: any) {
        alert(`Erro ao criar conversa: ${error.message}`);
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, executionPlan]);

  useEffect(() => {
    fetchProjects();
    fetchAgents();
  }, []);

  useEffect(() => {
    if (currentProjectName) {
      fetchConversations(currentProjectName);
    } else {
      setConversations([]);
      setCurrentConversationName(null);
    }
  }, [currentProjectName]);

  useEffect(() => {
    if (currentProjectName && currentConversationName) {
      fetchHistory(currentProjectName, currentConversationName);
    } else {
      setMessages([{ role: 'assistant', content: 'Selecione um projeto e uma conversa para começar.' }]);
    }
  }, [currentProjectName, currentConversationName]);

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/agents');
      if (!response.ok) throw new Error('Failed to fetch agents');
      const data = await response.json();
      const agentNames = data.map((agent: any) => agent.name);
      setAgents(agentNames);
      if (agentNames.length > 0) {
        setCurrentAgent(agentNames.includes('orchestrator') ? 'orchestrator' : agentNames[0]);
      }
    } catch (error) {
      console.error("Failed to fetch agents:", error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/projects');
      if (!response.ok) throw new Error('Failed to fetch projects');
      const data = await response.json();
      setProjects(data);
      if (data.length > 0 && !currentProjectName) {
        setCurrentProjectName(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    }
  };

  const fetchConversations = async (projectName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectName}/conversations`);
      if (!response.ok) throw new Error('Failed to fetch conversations');
      const data = await response.json();
      setConversations(data);
      if (data.length > 0) {
        setCurrentConversationName(data[0]);
      } else {
        setCurrentConversationName(null);
      }
    } catch (error) {
      console.error("Failed to fetch conversations:", error);
    }
  };

  const fetchHistory = async (projectName: string, conversationName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/history/${projectName}/${conversationName}`);
      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      if (data.length > 0) {
        setMessages(data);
      } else {
        setMessages([{ role: 'assistant', content: 'Nova conversa iniciada. Envie uma mensagem!' }]);
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  const handleCreateNewProject = async () => {
    const newProjectName = prompt("Digite o nome do novo projeto:");
    if (newProjectName && newProjectName.trim()) {
      try {
        const response = await fetch('http://localhost:8000/projects', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_name: newProjectName }),
        });
        if (response.ok) {
          await fetchProjects();
          setCurrentProjectName(newProjectName);
          setMessages([{ role: 'assistant', content: `Projeto '${newProjectName}' criado. Vamos começar!` }]);
        } else {
          const errorData = await response.json();
          alert(`Erro ao criar projeto: ${errorData.detail}`);
        }
      } catch (error: any) {
        console.error("Failed to create project:", error);
        alert(`Erro ao criar projeto: ${error.message}`);
      }
    }
  };

  const handleRenameProject = async (oldName: string) => {
    const newName = prompt(`Digite o novo nome para o projeto "${oldName}":`, oldName);
    if (newName && newName.trim() && newName !== oldName) {
      try {
        const response = await fetch(`http://localhost:8000/projects/${oldName}/rename`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ new_project_name: newName }),
        });
        if (response.ok) {
          await fetchProjects();
          setCurrentProjectName(newName);
        } else {
          const errorData = await response.json();
          alert(`Erro ao renomear projeto: ${errorData.detail}`);
        }
      } catch (error: any) {
        alert(`Erro ao renomear projeto: ${error.message}`);
      }
    }
  };

  const handleDeleteProject = async (projectName: string) => {
    if (window.confirm(`Tem certeza que deseja apagar o projeto "${projectName}"? Esta ação não pode ser desfeita.`)) {
      try {
        const response = await fetch(`http://localhost:8000/projects/${projectName}`, {
          method: 'DELETE',
        });
        if (response.ok) {
          await fetchProjects();
          if (currentProjectName === projectName) {
            setCurrentProjectName(null);
            setMessages([{ role: 'assistant', content: 'Projeto apagado. Selecione ou crie um novo projeto.' }]);
          }
        } else {
          const errorData = await response.json();
          alert(`Erro ao apagar projeto: ${errorData.detail}`);
        }
      } catch (error: any) {
        alert(`Erro ao apagar projeto: ${error.message}`);
      }
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !currentProjectName || !currentConversationName || isLoading) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    const currentInput = input;
    setInput('');
    setExecutionPlan(null);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: currentAgent,
          message: currentInput, // Corrigido: `message` no nível raiz
          history: newMessages.slice(-10),
          context: {
            project_name: currentProjectName,
            conversation_name: currentConversationName,
          }
        }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      const replyContent = data.reply;

      const finalMessages = [...newMessages, { role: 'assistant', content: replyContent }];
      setMessages(finalMessages);

    } catch (error: any) {
      console.error("Failed to send message:", error);
      setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: `Error: ${error.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const saveHistory = async () => {
      if (currentProjectName && currentConversationName && messages.length > 1) {
        try {
          await fetch(`http://localhost:8000/history/${currentProjectName}/${currentConversationName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messages),
          });
        } catch (error) {
          console.error("Failed to save history:", error);
        }
      }
    };
    saveHistory();
  }, [messages, currentProjectName, currentConversationName]);

  const handleExecuteStep = async (stepToExecute: PlanStep) => {
    if (!currentProjectName || !currentConversationName) return;

    // Atualiza o status do passo para 'in-progress'
    setExecutionPlan(prevPlan => {
      if (!prevPlan) return null;
      const newPlan = { ...prevPlan };
      newPlan.plan = newPlan.plan.map(step => 
        step.step === stepToExecute.step ? { ...step, status: 'in-progress' } : step
      );
      return newPlan;
    });

    try {
      const response = await fetch('http://localhost:8000/execute_task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: currentProjectName,
          conversation_name: currentConversationName,
          prompt: stepToExecute.prompt,
          agent: stepToExecute.agent,
          step: stepToExecute.step
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }

      // Adiciona a resposta da execução ao chat
      setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: data.reply }]);
      
      // Atualiza o status do passo para 'completed'
      setExecutionPlan(prevPlan => {
        if (!prevPlan) return null;
        const newPlan = { ...prevPlan };
        newPlan.plan = newPlan.plan.map(step => 
          step.step === stepToExecute.step ? { ...step, status: 'completed' } : step
        );
        return newPlan;
      });

    } catch (error: any) {
      console.error("Failed to execute step:", error);
      // Adiciona a mensagem de erro ao chat
      setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: `Erro ao executar passo ${stepToExecute.step}: ${error.message}` }]);
      
      // Atualiza o status do passo para 'failed'
      setExecutionPlan(prevPlan => {
        if (!prevPlan) return null;
        const newPlan = { ...prevPlan };
        newPlan.plan = newPlan.plan.map(step => 
          step.step === stepToExecute.step ? { ...step, status: 'failed' } : step
        );
        return newPlan;
      });
    }
  };

  const handleExecuteFullPlan = async () => {
    if (!executionPlan) return;

    for (const step of executionPlan.plan) {
      // Apenas executa passos pendentes
      if (step.status === 'pending') {
        await handleExecuteStep(step);
      }
    }
  };

  return (
    <>
      <Head>
        <title>Escrita Sincerta - Chat Profissional</title>
      </Head>
      <div className="grid grid-cols-[280px_1fr_320px] h-screen w-full bg-secondary text-foreground font-sans">
        {/* Sidebar */}
        <aside className="flex flex-col bg-background border-r p-4 space-y-4">
          <h1 className="text-xl font-semibold px-2">Projetos</h1>
          <ScrollArea className="flex-1 -mr-4 pr-4">
            <div className="flex flex-col space-y-1">
              {projects.map(project => (
                <div key={project} className="group flex items-center">
                  <Button
                    variant={project === currentProjectName ? 'secondary' : 'ghost'}
                    className="justify-start text-left flex-1 w-full truncate"
                    onClick={() => setCurrentProjectName(project)}
                  >
                    {project}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="ml-2 h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleRenameProject(project)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="ml-1 h-7 w-7 text-destructive opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleDeleteProject(project)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
          <Button variant="outline" className="mt-auto" onClick={handleCreateNewProject}>
            <PlusCircle className="mr-2 h-4 w-4" />
            Novo Projeto
          </Button>
        </aside>

        {/* ChatView */}
        <div className="flex flex-col bg-background">
          <header className="bg-background p-4 border-b flex justify-between items-center z-10 shadow-sm">
            <div className="flex items-center gap-4">
              <h2 className="text-lg font-semibold">{currentProjectName || "Selecione um Projeto"}</h2>
              {currentProjectName && (
                <select
                  value={currentConversationName || ''}
                  onChange={(e) => setCurrentConversationName(e.target.value)}
                  className="bg-background border rounded-md p-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  disabled={conversations.length === 0}
                >
                  {conversations.map(conv => <option key={conv} value={conv}>{conv}</option>)}
                </select>
              )}
              <Button variant="outline" size="sm" onClick={handleCreateNewConversation}>
                <PlusCircle className="mr-2 h-4 w-4" />
                Nova Conversa
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <label htmlFor="agent-selector" className="text-sm text-muted-foreground">Agente:</label>
              <select
                id="agent-selector"
                value={currentAgent}
                onChange={(e) => setCurrentAgent(e.target.value)}
                className="bg-background border rounded-md p-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {agents.map(agent => <option key={agent} value={agent}>{agent}</option>)}
              </select>
            </div>
          </header>
          <main className="flex-1 p-6 overflow-y-hidden">
            <ScrollArea className="h-full" ref={scrollAreaRef}>
              <div className="space-y-6 pr-4">
                {messages.map((msg, index) => (
                  <div key={index} className={`flex items-start gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                    {msg.role === 'assistant' && <Avatar className="w-8 h-8"><AvatarFallback><Bot size={20}/></AvatarFallback></Avatar>}
                    <div className={`rounded-lg p-3 max-w-2xl text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'}`}>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                    {msg.role === 'user' && <Avatar className="w-8 h-8"><AvatarFallback><User size={20}/></AvatarFallback></Avatar>}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-start gap-3">
                    <Avatar className="w-8 h-8"><AvatarFallback><Bot size={20}/></AvatarFallback></Avatar>
                    <div className="rounded-lg p-3 bg-secondary flex items-center space-x-2">
                       <Loader2 className="h-5 w-5 animate-spin" />
                       <span>Pensando...</span>
                    </div>
                  </div>
                )}
                {executionPlan && (
                  <Card className="bg-secondary border-border">
                    <CardHeader>
                      <CardTitle>Plano de Execução</CardTitle>
                      <CardDescription>{executionPlan.goal}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {executionPlan.plan.map((step) => (
                        <div key={step.step} className="p-3 rounded-md border bg-background/50">
                          <div className="flex justify-between items-center">
                            <div className="flex-1">
                              <p className="font-semibold">Passo {step.step}: <span className="font-mono text-primary/80">{step.agent}</span></p>
                              <p className="text-sm text-muted-foreground mt-1">{step.prompt}</p>
                            </div>
                            <Button variant="outline" size="sm" onClick={() => handleExecuteStep(step)}>
                              Executar
                            </Button>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </div>
            </ScrollArea>
          </main>
          <footer className="p-4 bg-background border-t">
            <div className="relative">
              <Input
                placeholder="Converse com o agente..."
                className="pr-12 h-12"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                disabled={isLoading}
              />
              <Button variant="ghost" size="icon" className="absolute right-3 top-1/2 -translate-y-1/2" onClick={handleSendMessage} disabled={isLoading}>
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </footer>
        </div>

        {/* File Explorer */}
        <aside className="bg-background border-l p-4">
          <h3 className="text-lg font-semibold mb-4">Explorador de Arquivos</h3>
          <ScrollArea className="h-full -mr-4 pr-4">
            {currentProjectName ? (
              <FileTree projectName={currentProjectName} />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">Selecione um projeto.</p>
              </div>
            )}
          </ScrollArea>
        </aside>
      </div>
    </>
  );
};

export default HomePage;