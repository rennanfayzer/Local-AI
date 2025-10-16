# Multi-stage build para otimização de tamanho
FROM python:3.11-slim as builder

# Instalar dependências de build
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Preparar ambiente Python
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Imagem final
FROM python:3.11-slim

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash sincerta

# Instalar runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configurar ambiente
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/sincerta/.local/bin:$PATH

# Copiar dependências Python do builder
COPY --from=builder /root/.local /home/sincerta/.local

# Copiar código da aplicação
COPY --chown=sincerta:sincerta . .

# Criar diretórios necessários
RUN mkdir -p /app/data/docs /app/logs \
    && chown -R sincerta:sincerta /app

# Trocar para usuário não-root
USER sincerta

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
