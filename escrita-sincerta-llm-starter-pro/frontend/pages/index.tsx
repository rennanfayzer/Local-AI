import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import FileTree from '../components/FileTree';
import Button from '../components/Button';
import Heading from '../components/Heading';

const SendIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 14L21 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M21 3L14.5 21L10 14L3 9.5L21 3Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);


const HomePage: React.FC = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Olá! Como posso ajudar você hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [projects, setProjects] = useState<string[]>([]);
  const [currentProjectName, setCurrentProjectName] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch('http://localhost:8000/projects');
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const data = await response.json();
      setProjects(data);
      if (data.length > 0 && !currentProjectName) {
        setCurrentProjectName(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    }
  };

  const handleCreateNewProject = async () => {
    const newProjectName = prompt("Digite o nome do novo projeto:");
    if (newProjectName) {
      try {
        const response = await fetch('http://localhost:8000/projects', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ project_name: newProjectName }),
        });
        if (response.ok) {
          fetchProjects();
          setCurrentProjectName(newProjectName);
          setMessages([{ role: 'assistant', content: `Projeto '${newProjectName}' criado. Você pode começar a trabalhar nele agora.` }]);
        } else {
          const errorData = await response.json();
          alert(`Erro ao criar projeto: ${errorData.detail}`);
        }
      } catch (error) {
        console.error("Failed to create project:", error);
        alert(`Erro ao criar projeto: ${error.message}`);
      }
    }
  };
  
  const handleSendMessage = async () => {
    if (!input.trim() || !currentProjectName) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    const currentInput = input;
    setInput('');

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent: 'dev_fullstack', // Hardcoded for now, will be dynamic later
          message: currentInput,
          history: newMessages.slice(-10), // Send last 10 messages for context
          project_name: currentProjectName,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages(prevMessages => [...prevMessages, { role: 'assistant', content: `Error: ${error.message}` }]);
    }
  };

  return (
    <>
      <Head>
        <title>Escrita Sincerta - Chat</title>
      </Head>
      <div className="flex h-screen w-full bg-zinc-950 text-zinc-50 font-sans">
        {/* Coluna da Esquerda (Sidebar) */}
        <aside className="w-1/4 max-w-xs bg-zinc-900 p-4 border-r border-zinc-800 flex flex-col">
          <Heading as="h1" className="text-lg mb-4">Projetos</Heading>
          <div className="flex-1 overflow-y-auto">
            <div className="flex flex-col space-y-2">
              {projects.map(project => (
                <Button 
                  key={project}
                  variant={project === currentProjectName ? 'default' : 'ghost'} 
                  className="justify-start text-left"
                  onClick={() => setCurrentProjectName(project)}
                >
                  {project}
                </Button>
              ))}
            </div>
          </div>
           <Button variant="outline" onClick={handleCreateNewProject}>Novo Projeto</Button>
        </aside>

        {/* Coluna do Meio (ChatView) */}
        <div className="flex-1 flex flex-col bg-zinc-900">
          <header className="bg-zinc-950 p-4 border-b border-zinc-800 flex justify-between items-center">
            <Heading as="h2" className="border-b-0 pb-0">{currentProjectName || "Nenhum projeto selecionado"}</Heading>
          </header>
          <main className="flex-1 p-6 overflow-y-auto space-y-6">
            {messages.map((msg, index) => (
              <div key={index} className={`flex items-start space-x-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                {msg.role === 'assistant' && <span className="text-2xl">🤖</span>}
                <div className={`rounded-lg p-3 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-zinc-800'}`}>
                  <p>{msg.content}</p>
                </div>
                {msg.role === 'user' && <span className="text-2xl">👤</span>}
              </div>
            ))}
          </main>
          <footer className="p-4 bg-zinc-950 border-t border-zinc-800">
            <div className="relative">
              <input
                type="text"
                placeholder="Digite sua mensagem..."
                className="w-full p-3 pr-12 rounded-lg bg-zinc-800 border border-zinc-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
              />
              <Button variant="ghost" size="sm" className="absolute right-2 top-1/2 -translate-y-1/2" onClick={handleSendMessage}>
                <SendIcon />
              </Button>
            </div>
          </footer>
        </div>

        {/* Coluna da Direita (File Explorer) */}
        <aside className="w-1/3 max-w-md bg-zinc-950 p-4 border-l border-zinc-800 overflow-y-auto">
          <Heading as="h3" className="mb-4 border-b-0 pb-0">Explorador de Arquivos</Heading>
          {currentProjectName ? (
            <FileTree projectName={currentProjectName} />
          ) : (
            <div className="flex items-center justify-center h-full">
              <p className="text-zinc-500">Nenhum projeto selecionado.</p>
            </div>
          )}
        </aside>
      </div>
    </>
  );
};

export default HomePage;
