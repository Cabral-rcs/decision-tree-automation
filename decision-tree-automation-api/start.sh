#!/bin/bash
# Script de inicialização para o Render

# Define variáveis de ambiente padrão se não estiverem definidas
export PORT=${PORT:-8000}
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src/decision-tree-automation-api"

echo "=== Iniciando Decision Tree Automation ==="
echo "Diretório atual: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Porta: $PORT"
echo "Repositório: decision-tree-automation"

# Verifica a estrutura do projeto
echo "=== Verificando Estrutura do Projeto ==="
echo "Conteúdo do diretório atual:"
ls -la

echo "Verificando estrutura do repositório:"
ls -la /opt/render/project/src/ 2>/dev/null || echo "❌ Diretório /opt/render/project/src não encontrado"

echo "Verificando frontend em caminhos relativos:"
ls -la ../decision-tree-automation-ui/ 2>/dev/null || echo "❌ Frontend não encontrado em ../decision-tree-automation-ui/"

echo "Verificando frontend em caminhos absolutos:"
find /opt/render/project/src -name "index.html" 2>/dev/null || echo "❌ index.html não encontrado em /opt/render/project/src"

echo "Verificando estrutura completa:"
find /opt/render/project/src -type f -name "*.html" 2>/dev/null || echo "❌ Nenhum arquivo HTML encontrado"

# Verifica se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ ERRO: requirements.txt não encontrado no diretório atual"
    echo "Tentando navegar para o diretório correto..."
    cd /opt/render/project/src/decision-tree-automation-api 2>/dev/null || {
        echo "❌ ERRO: Não foi possível encontrar o diretório decision-tree-automation-api"
        exit 1
    }
    echo "✅ Navegado para: $(pwd)"
fi

# Executa migração do banco se necessário
echo "=== Verificando Banco de Dados ==="
echo "Verificando estrutura do banco de dados..."
python migrate_database.py

# Verifica se o frontend existe antes de iniciar
echo "=== Verificação Final do Frontend ==="
FRONTEND_PATHS=(
    "/opt/render/project/src/decision-tree-automation-ui/index.html"
    "/opt/render/project/src/decision-tree-automation/decision-tree-automation-ui/index.html"
    "$(pwd)/../decision-tree-automation-ui/index.html"
    "$(pwd)/decision-tree-automation-ui/index.html"
    "/opt/render/project/src/decision-tree-automation-ui/index.html"
)

FRONTEND_FOUND=false
for path in "${FRONTEND_PATHS[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ Frontend encontrado em: $path"
        echo "   Tamanho: $(wc -c < "$path") bytes"
        echo "   Última modificação: $(stat -c %y "$path")"
        FRONTEND_FOUND=true
        break
    else
        echo "❌ Frontend não encontrado em: $path"
    fi
done

if [ "$FRONTEND_FOUND" = false ]; then
    echo "⚠️  AVISO: Frontend não encontrado em nenhum caminho!"
    echo "   O sistema continuará funcionando, mas o frontend pode não carregar corretamente."
    echo "   Verificando se o repositório foi clonado corretamente..."
    echo "   Estrutura completa:"
    find /opt/render/project/src -type d 2>/dev/null | head -10
fi

# Executa o servidor
echo "=== Iniciando Servidor ==="
echo "Iniciando servidor na porta $PORT..."
echo "URL: http://0.0.0.0:$PORT"
echo "Frontend URL: https://decision-tree-automation.onrender.com"
uvicorn backend.main:app --host 0.0.0.0 --port $PORT