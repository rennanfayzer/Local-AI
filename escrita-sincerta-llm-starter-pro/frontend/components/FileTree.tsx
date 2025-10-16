import React, { useState, useEffect } from 'react';

// Tipagem para a estrutura de arquivos que a API retorna
interface FileNode {
  [key: string]: FileNode | null;
}

interface FileTreeProps {
  projectName: string;
}

const FileTree: React.FC<FileTreeProps> = ({ projectName }) => {
  const [files, setFiles] = useState<FileNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!projectName) return;

    const fetchFileTree = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/generated-projects/${projectName}`);
        if (!response.ok) {
          if (response.status === 404) {
            setFiles(null); // Projeto existe, mas não tem arquivos
          } else {
            throw new Error(`Failed to fetch file tree: ${response.statusText}`);
          }
        } else {
            const data = await response.json();
            setFiles(data.files);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setFiles(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFileTree();
  }, [projectName]);

  // Componente recursivo para renderizar os nós da árvore
  const renderNode = (name: string, node: FileNode | null) => {
    const isDirectory = node !== null && typeof node === 'object';

    return (
      <div key={name} className="ml-4">
        <div className="flex items-center">
          <span className="mr-2">{isDirectory ? '📁' : '📄'}</span>
          <span>{name}</span>
        </div>
        {isDirectory && (
          <div className="pl-4 border-l border-zinc-700">
            {Object.entries(node).map(([childName, childNode]) =>
              renderNode(childName, childNode)
            )}
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return <div className="text-zinc-400">Loading file tree...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  if (!files) {
    return <div className="text-zinc-500">No files found for this project.</div>;
  }

  return (
    <div className="bg-zinc-900 text-zinc-50 p-4 rounded-lg font-mono text-sm">
      <h3 className="text-lg font-bold mb-2 border-b border-zinc-800 pb-2">{projectName}</h3>
      {Object.entries(files).map(([name, node]) => renderNode(name, node))}
    </div>
  );
};

export default FileTree;
