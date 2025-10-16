"""
Sistema RAG (Retrieval-Augmented Generation) com pgvector
Responsável por ingestão de documentos, geração de embeddings e busca por similaridade
"""

import os
import glob
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import json

# Configuração de logging
logger = logging.getLogger(__name__)

# Configurações
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'sincerta_memory'),
    'user': os.getenv('DB_USER', 'sincerta'),
    'password': os.getenv('DB_PASSWORD', 'escrita_segura_2024')
}

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'bge-m3')
EMBEDDING_DIM = int(os.getenv('EMBEDDING_DIMENSION', '1024'))
CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '200'))
TOP_K = int(os.getenv('RAG_TOP_K', '5'))

class EmbeddingGenerator:
    """Gerador de embeddings usando Ollama ou Sentence Transformers"""
    
    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model = None
        
        if not use_ollama:
            try:
                # Fallback para sentence-transformers local
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Carregado modelo sentence-transformers local")
            except Exception as e:
                logger.error(f"Erro ao carregar sentence-transformers: {e}")
                self.use_ollama = True
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Gera embedding para texto"""
        try:
            if self.use_ollama:
                return self._ollama_embedding(text)
            else:
                return self._local_embedding(text)
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return None
    
    def _ollama_embedding(self, text: str) -> Optional[List[float]]:
        """Gera embedding via Ollama"""
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('embedding', [])
            else:
                logger.warning(f"Ollama embedding falhou: {response.status_code}")
                return self._local_embedding(text)
                
        except Exception as e:
            logger.warning(f"Erro Ollama embedding, usando local: {e}")
            return self._local_embedding(text)
    
    def _local_embedding(self, text: str) -> Optional[List[float]]:
        """Gera embedding local com sentence-transformers"""
        if self.model is None:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.error(f"Não foi possível carregar modelo local: {e}")
                return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erro ao gerar embedding local: {e}")
            return None

class DocumentProcessor:
    """Processador de documentos para chunking e limpeza"""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Divide texto em chunks com sobreposição"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Tenta quebrar em final de frase
            if end < len(text):
                # Procura por ponto final nos últimos 100 caracteres
                sentence_end = text.rfind('.', start + chunk_size - 100, end)
                if sentence_end != -1 and sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < len(text) else len(text)
        
        return chunks
    
    @staticmethod
    def extract_text_from_file(file_path: Path) -> Tuple[str, Dict[str, Any]]:
        """Extrai texto e metadados de arquivo"""
        metadata = {
            'file_type': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size,
            'modified_time': file_path.stat().st_mtime
        }
        
        try:
            if file_path.suffix.lower() == '.md':
                content = file_path.read_text(encoding='utf-8')
                metadata['type'] = 'markdown'
                
            elif file_path.suffix.lower() == '.txt':
                content = file_path.read_text(encoding='utf-8')
                metadata['type'] = 'text'
                
            elif file_path.suffix.lower() == '.html':
                from bs4 import BeautifulSoup
                html_content = file_path.read_text(encoding='utf-8')
                soup = BeautifulSoup(html_content, 'html.parser')
                content = soup.get_text()
                metadata['type'] = 'html'
                
            elif file_path.suffix.lower() == '.pdf':
                # Placeholder - implementar PyPDF2/pdfplumber
                content = f"PDF: {file_path.name} (processamento futuro)"
                metadata['type'] = 'pdf'
                
            else:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                metadata['type'] = 'unknown'
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {e}")
            content = f"Erro ao processar arquivo: {str(e)}"
            metadata['error'] = str(e)
        
        return content, metadata

class RAGDatabase:
    """Interface para operações de banco de dados do RAG"""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
    
    def get_connection(self):
        """Cria conexão com PostgreSQL"""
        try:
            return psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            logger.error(f"Erro ao conectar com PostgreSQL: {e}")
            raise
    
    def insert_document(self, filename: str, content: str, metadata: Dict[str, Any]) -> str:
        """Insere documento na base"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                doc_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO documents (id, filename, content, metadata)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (filename) 
                    DO UPDATE SET content = EXCLUDED.content, 
                                  metadata = EXCLUDED.metadata,
                                  updated_at = NOW()
                    RETURNING id
                    """,
                    (doc_id, filename, content, json.dumps(metadata))
                )
                result = cur.fetchone()
                return result['id'] if result else doc_id
    
    def insert_chunk(self, document_id: str, chunk_index: int, content: str, 
                     embedding: Optional[List[float]], metadata: Dict[str, Any] = None):
        """Insere chunk com embedding"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO document_chunks (document_id, chunk_index, content, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (document_id, chunk_index, content, embedding, json.dumps(metadata or {}))
                )
    
    def search_similar_chunks(self, query_embedding: List[float], 
                             threshold: float = 0.7, limit: int = TOP_K) -> List[Dict[str, Any]]:
        """Busca chunks similares usando função PostgreSQL"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM search_similar_chunks(%s, %s, %s)",
                    (query_embedding, threshold, limit)
                )
                return cur.fetchall()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT get_system_stats()")
                result = cur.fetchone()
                return result[0] if result else {}

# Interface pública
def ingest_path(path: str, file_types: List[str] = None) -> int:
    """
    Ingestão de documentos de um diretório
    
    Args:
        path: Caminho do diretório
        file_types: Lista de extensões a processar (padrão: ['.md', '.txt', '.html'])
    
    Returns:
        Número de arquivos processados
    """
    if file_types is None:
        file_types = ['.md', '.txt', '.html', '.pdf']
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            logger.error(f"Diretório não encontrado: {path}")
            return 0
        
        # Encontra arquivos
        files = []
        for file_type in file_types:
            pattern = f"**/*{file_type}"
            files.extend(path_obj.glob(pattern))
        
        if not files:
            logger.warning(f"Nenhum arquivo encontrado em {path}")
            return 0
        
        db = RAGDatabase()
        processor = DocumentProcessor()
        processed_count = 0
        
        for file_path in files:
            try:
                logger.info(f"Processando: {file_path}")
                
                # Extrai conteúdo
                content, metadata = processor.extract_text_from_file(file_path)
                
                # Insere documento
                doc_id = db.insert_document(
                    filename=str(file_path.relative_to(path_obj)),
                    content=content,
                    metadata=metadata
                )
                
                # Cria chunks e embeddings
                chunks = processor.chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    embedding = db.embedding_generator.generate_embedding(chunk)
                    db.insert_chunk(
                        document_id=doc_id,
                        chunk_index=i,
                        content=chunk,
                        embedding=embedding,
                        metadata={'chunk_size': len(chunk)}
                    )
                
                processed_count += 1
                logger.info(f"✓ {file_path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {e}")
        
        logger.info(f"Ingestão concluída: {processed_count}/{len(files)} arquivos")
        return processed_count
        
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}")
        return 0

def query_vectors(query: str, k: int = TOP_K, threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Busca por similaridade vetorial
    
    Args:
        query: Texto da busca
        k: Número máximo de resultados
        threshold: Threshold de similaridade (0.0 a 1.0)
    
    Returns:
        Lista de chunks similares com metadata
    """
    try:
        db = RAGDatabase()
        
        # Gera embedding da query
        query_embedding = db.embedding_generator.generate_embedding(query)
        if not query_embedding:
            logger.error("Não foi possível gerar embedding para a query")
            return []
        
        # Busca chunks similares
        results = db.search_similar_chunks(query_embedding, threshold, k)
        
        # Formata resultados
        formatted_results = []
        for result in results:
            formatted_results.append({
                'content': result['content'],
                'similarity': float(result['similarity']),
                'filename': result['filename'],
                'chunk_index': result['chunk_index'],
                'document_id': str(result['document_id']),
                'metadata': {
                    'similarity_score': float(result['similarity']),
                    'chunk_position': result['chunk_index']
                }
            })
        
        logger.info(f"Query RAG: {len(formatted_results)} resultados para '{query[:50]}...'")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Erro na busca vetorial: {e}")
        return []

def get_rag_stats() -> Dict[str, Any]:
    """Obtém estatísticas do sistema RAG"""
    try:
        db = RAGDatabase()
        return db.get_stats()
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}

