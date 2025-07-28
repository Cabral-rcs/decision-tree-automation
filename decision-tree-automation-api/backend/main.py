# main.py - Inicialização do backend FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.views import api_router
from backend.controllers import telegram_scheduler  # Importa o scheduler para iniciar o agendamento
from backend.config import CHAT_IDS
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario
import os
import logging
from backend.controllers.alerta_controller import router as alerta_router
from backend.controllers.lider_controller import router as lider_router
from backend.controllers.auto_alert_controller import router as auto_alert_router

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Decision Tree Automation API", version="1.0.0")

# Adiciona o middleware de CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(api_router)
app.include_router(alerta_router)
app.include_router(lider_router)
app.include_router(auto_alert_router)

@app.get("/", response_class=HTMLResponse)
def get_frontend():
    """Serve o frontend HTML"""
    logger.info("Tentando servir o frontend...")
    
    # Lista de caminhos possíveis para o frontend
    possible_paths = [
        # Caminho para Render (produção)
        os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
        # Caminho alternativo para Render
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
        # Caminho para desenvolvimento local
        os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"),
        # Caminho absoluto para Render
        "/opt/render/project/src/decision-tree-automation-ui/index.html",
        # Caminho alternativo absoluto
        "/opt/render/project/src/decision-tree-automation/decision-tree-automation-ui/index.html"
    ]
    
    logger.info(f"Diretório atual: {os.getcwd()}")
    logger.info(f"Diretório do backend: {os.path.dirname(__file__)}")
    
    for i, path in enumerate(possible_paths):
        logger.info(f"Tentando caminho {i+1}: {path}")
        if os.path.exists(path):
            logger.info(f"✅ Frontend encontrado em: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"✅ Frontend carregado com sucesso ({len(content)} bytes)")
                return HTMLResponse(content=content, status_code=200)
            except Exception as e:
                logger.error(f"❌ Erro ao ler arquivo {path}: {e}")
                continue
    
    # Se não encontrar o arquivo, retorna uma página de erro informativa
    logger.error("❌ Frontend não encontrado em nenhum caminho")
    error_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Erro - Frontend não encontrado</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; background: #f5f5f5; }}
            .error-container {{ background: white; padding: 2em; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .error-title {{ color: #d32f2f; margin-bottom: 1em; }}
            .path-list {{ background: #f8f9fa; padding: 1em; border-radius: 4px; margin: 1em 0; }}
            .path-item {{ margin: 0.5em 0; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1 class="error-title">❌ Frontend não encontrado</h1>
            <p>O arquivo index.html não foi encontrado nos caminhos esperados.</p>
            
            <h3>Informações do ambiente:</h3>
            <ul>
                <li><strong>Diretório atual:</strong> {os.getcwd()}</li>
                <li><strong>Diretório do backend:</strong> {os.path.dirname(__file__)}</li>
            </ul>
            
            <h3>Caminhos testados:</h3>
            <div class="path-list">
                {''.join([f'<div class="path-item">{i+1}. {path}</div>' for i, path in enumerate(possible_paths)])}
            </div>
            
            <h3>Possíveis soluções:</h3>
            <ul>
                <li>Verifique se o frontend está incluído no deploy do Render</li>
                <li>Confirme se o render.yaml inclui decision-tree-automation-ui/**</li>
                <li>Verifique se o arquivo index.html existe na pasta correta</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=error_html, status_code=404)

@app.get("/health")
def health_check():
    """Endpoint de health check"""
    return {"status": "healthy", "message": "API funcionando corretamente"}

@app.get("/debug")
def debug_info():
    """Endpoint para debug do ambiente"""
    return {
        "current_directory": os.getcwd(),
        "backend_directory": os.path.dirname(__file__),
        "environment": os.environ.get("RENDER", "local"),
        "python_version": os.sys.version,
        "frontend_paths": [
            os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
            os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"),
        ]
    }
    
# Ao iniciar o sistema, envie a primeira pergunta para todos os usuários
@app.on_event("startup")
def enviar_primeira_pergunta():
    logger.info("🚀 Iniciando Decision Tree Automation...")
    try:
        for user_id in CHAT_IDS:
            enviar_pergunta_para_usuario(user_id)
        
        # Inicializa o scheduler de alertas automáticos
        from backend.services.auto_alert_scheduler import auto_alert_scheduler
        from backend.controllers.auto_alert_controller import ensure_rafael_cabral_exists
        
        # Garante que Rafael Cabral existe
        ensure_rafael_cabral_exists()
        
        # Inicia o scheduler
        auto_alert_scheduler.start()
        logger.info("✅ Sistema inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        # Continua mesmo se houver erro na inicialização

# Comentário: O backend segue o padrão MVC, separando models, views e controllers.
# O envio inicial de perguntas ocorre no evento de startup. 