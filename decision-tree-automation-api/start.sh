#!/bin/bash
# Script de inicialização para o Render

# Define variáveis de ambiente padrão se não estiverem definidas
export PORT=${PORT:-8000}
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "=== Iniciando Decision Tree Automation ==="

# Executa migração do banco se necessário
echo "Verificando estrutura do banco de dados..."
python migrate_database.py

# Executa o servidor
echo "Iniciando servidor na porta $PORT..."
uvicorn backend.main:app --host 0.0.0.0 --port $PORT