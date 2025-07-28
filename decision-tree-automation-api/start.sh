#!/bin/bash
# Script de inicialização para o Render

# Define variáveis de ambiente padrão se não estiverem definidas
export PORT=${PORT:-8000}
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Executa o servidor
echo "Iniciando servidor na porta $PORT..."
uvicorn backend.main:app --host 0.0.0.0 --port $PORT