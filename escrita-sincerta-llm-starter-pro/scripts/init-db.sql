-- ==========================================
-- ESCRITA SINCERTA LLM - INICIALIZAÇÃO DB
-- ==========================================

-- Habilita extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela para armazenar documentos
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para chunks de documentos com embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024), -- Ajustar dimensão conforme modelo
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para histórico de conversas
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) DEFAULT 'anonymous',
    agent_name VARCHAR(50) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela para mensagens das conversas
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- Índice vetorial para busca por similaridade
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON document_chunks(chunk_index);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at DESC);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para busca por similaridade vetorial
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1024),
    similarity_threshold float DEFAULT 0.7,
    max_results int DEFAULT 5
)
RETURNS TABLE (
    chunk_id uuid,
    document_id uuid,
    content text,
    similarity float,
    filename varchar,
    chunk_index int
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id as chunk_id,
        dc.document_id,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity,
        d.filename,
        dc.chunk_index
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE dc.embedding IS NOT NULL
    AND 1 - (dc.embedding <=> query_embedding) > similarity_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Função para estatísticas do sistema
CREATE OR REPLACE FUNCTION get_system_stats()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'documents_count', (SELECT COUNT(*) FROM documents),
        'chunks_count', (SELECT COUNT(*) FROM document_chunks),
        'conversations_count', (SELECT COUNT(*) FROM conversations),
        'messages_count', (SELECT COUNT(*) FROM messages),
        'latest_document', (SELECT filename FROM documents ORDER BY created_at DESC LIMIT 1),
        'latest_conversation', (SELECT created_at FROM conversations ORDER BY created_at DESC LIMIT 1)
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Inserção inicial de dados de exemplo (opcional)
INSERT INTO documents (filename, content, metadata) VALUES 
('manifesto_sincerta.md', 'Direto, técnico, honesto. Nunca minta. Formato: Contexto → Solução → Exemplo/Código → Checklist.', '{"type": "manifesto", "version": "1.0"}')
ON CONFLICT DO NOTHING;

-- Logs de inicialização
DO $$
BEGIN
    RAISE NOTICE 'Escrita Sincerta LLM - Database inicializado com sucesso';
    RAISE NOTICE 'Tabelas: documents, document_chunks, conversations, messages';
    RAISE NOTICE 'Extensões: vector, uuid-ossp';
    RAISE NOTICE 'Funções: search_similar_chunks, get_system_stats';
END $$;