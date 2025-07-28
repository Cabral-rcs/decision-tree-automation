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
app.include_router(auto_alert_router)

@app.get("/", response_class=HTMLResponse)
def get_frontend(force_reload: bool = False):
    """Serve o frontend HTML"""
    logger.info("Tentando servir o frontend...")
    
    # Lista de caminhos possíveis para o frontend
    possible_paths = [
        # Caminho para Render (produção) - mais específico
        "/opt/render/project/src/decision-tree-automation-ui/index.html",
        # Caminho alternativo para Render
        "/opt/render/project/src/decision-tree-automation/decision-tree-automation-ui/index.html",
        # Caminho relativo para Render
        os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
        # Caminho alternativo relativo para Render
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
        # Caminho para desenvolvimento local
        os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"),
        # Caminho absoluto alternativo
        "/app/decision-tree-automation-ui/index.html",
        # Caminho do workspace atual
        os.path.join(os.getcwd(), "decision-tree-automation-ui/index.html")
    ]
    
    logger.info(f"Diretório atual: {os.getcwd()}")
    logger.info(f"Diretório do backend: {os.path.dirname(__file__)}")
    logger.info(f"Ambiente: {os.environ.get('RENDER', 'local')}")
    logger.info(f"Força reload: {force_reload}")
    
    for i, path in enumerate(possible_paths):
        logger.info(f"Tentando caminho {i+1}: {path}")
        if os.path.exists(path):
            logger.info(f"✅ Frontend encontrado em: {path}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"✅ Frontend carregado com sucesso ({len(content)} bytes)")
                
                # Adiciona timestamp único para forçar refresh
                import datetime
                timestamp = datetime.datetime.now().isoformat()
                
                # Adiciona headers para evitar cache de forma mais agressiva
                headers = {
                    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0, private",
                    "Pragma": "no-cache",
                    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
                    "Content-Type": "text/html; charset=utf-8",
                    "X-Frontend-Timestamp": timestamp,
                    "X-Frontend-Path": path,
                    "X-Force-Reload": str(force_reload),
                    "X-Cache-Control": "no-cache"
                }
                
                # Se force_reload for True, adiciona um script para forçar reload
                if force_reload:
                    reload_script = """
                    <script>
                        console.log('🔄 Forçando reload do frontend...');
                        setTimeout(() => {
                            window.location.reload(true);
                        }, 100);
                    </script>
                    """
                    # Insere o script no head do HTML
                    content = content.replace('</head>', f'{reload_script}</head>')
                
                return HTMLResponse(content=content, status_code=200, headers=headers)
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
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; background: #f5f5f5; }}
            .error-container {{ background: white; padding: 2em; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .error-title {{ color: #d32f2f; margin-bottom: 1em; }}
            .path-list {{ background: #f8f9fa; padding: 1em; border-radius: 4px; margin: 1em 0; }}
            .path-item {{ margin: 0.5em 0; font-family: monospace; }}
            .timestamp {{ color: #666; font-size: 0.9em; margin-top: 2em; }}
            .refresh-btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 10px 0; }}
            .refresh-btn:hover {{ background: #0056b3; }}
        </style>
        <script>
            // Auto-refresh a cada 5 segundos
            setTimeout(() => {{
                location.reload(true);
            }}, 5000);
        </script>
    </head>
    <body>
        <div class="error-container">
            <h1 class="error-title">❌ Frontend não encontrado</h1>
            <p>O arquivo index.html não foi encontrado nos caminhos esperados.</p>
            <p><strong>Auto-refresh ativo:</strong> A página será recarregada automaticamente a cada 5 segundos.</p>
            
            <button class="refresh-btn" onclick="location.reload(true)">🔄 Recarregar Agora</button>
            
            <h3>Informações do ambiente:</h3>
            <ul>
                <li><strong>Diretório atual:</strong> {os.getcwd()}</li>
                <li><strong>Diretório do backend:</strong> {os.path.dirname(__file__)}</li>
                <li><strong>Ambiente:</strong> {os.environ.get('RENDER', 'local')}</li>
                <li><strong>Timestamp:</strong> {__import__('datetime').datetime.now().isoformat()}</li>
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
                <li>Faça um novo deploy no Render</li>
                <li>Use Ctrl+F5 para forçar refresh do navegador</li>
                <li>Acesse /?force_reload=true para forçar reload</li>
            </ul>
            
            <div class="timestamp">
                <p>Última verificação: {__import__('datetime').datetime.now().isoformat()}</p>
            </div>
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

@app.get("/force-refresh")
def force_refresh():
    """Endpoint para forçar refresh do frontend"""
    return {
        "message": "Use Ctrl+F5 ou Cmd+Shift+R para forçar refresh do navegador",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "cache_headers": {
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "Thu, 01 Jan 1970 00:00:00 GMT"
        }
    }

@app.get("/frontend-status")
def frontend_status():
    """Endpoint para verificar o status do frontend"""
    import datetime
    
    # Lista de caminhos possíveis para o frontend
    possible_paths = [
        "/opt/render/project/src/decision-tree-automation-ui/index.html",
        "/opt/render/project/src/decision-tree-automation/decision-tree-automation-ui/index.html",
        os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
        os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"),
        "/app/decision-tree-automation-ui/index.html",
        os.path.join(os.getcwd(), "decision-tree-automation-ui/index.html")
    ]
    
    status = {
        "current_directory": os.getcwd(),
        "backend_directory": os.path.dirname(__file__),
        "environment": os.environ.get('RENDER', 'local'),
        "timestamp": datetime.datetime.now().isoformat(),
        "paths_checked": [],
        "frontend_found": False,
        "frontend_path": None,
        "frontend_size": None,
        "frontend_content_preview": None
    }
    
    for path in possible_paths:
        exists = os.path.exists(path)
        size = None
        content_preview = None
        if exists:
            try:
                size = os.path.getsize(path)
                if not status["frontend_found"]:
                    status["frontend_found"] = True
                    status["frontend_path"] = path
                    status["frontend_size"] = size
                    
                    # Lê uma amostra do conteúdo para verificar a versão
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Procura pela versão no conteúdo
                        import re
                        version_match = re.search(r'content="([^"]*version[^"]*)"', content)
                        if version_match:
                            status["frontend_content_preview"] = version_match.group(1)
                        else:
                            status["frontend_content_preview"] = "Versão não encontrada"
            except Exception as e:
                size = f"Erro ao ler: {e}"
        
        status["paths_checked"].append({
            "path": path,
            "exists": exists,
            "size": size
        })
    
    return status

@app.get("/reload-frontend")
def reload_frontend():
    """Endpoint para forçar reload do frontend"""
    import datetime
    
    # Força o reload retornando headers específicos
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
        "X-Frontend-Reload": "forced",
        "X-Reload-Timestamp": datetime.datetime.now().isoformat()
    }
    
    return {
        "message": "Frontend reload forçado",
        "timestamp": datetime.datetime.now().isoformat(),
        "instructions": [
            "1. Use Ctrl+F5 para forçar refresh do navegador",
            "2. Ou acesse / para carregar a versão mais recente",
            "3. Verifique /frontend-status para debug",
            "4. Acesse /?force_reload=true para forçar reload automático"
        ]
    }

@app.get("/check-frontend-version")
def check_frontend_version():
    """Endpoint para verificar a versão atual do frontend"""
    import datetime
    import re
    
    # Lista de caminhos possíveis para o frontend
    possible_paths = [
        "/opt/render/project/src/decision-tree-automation-ui/index.html",
        "/opt/render/project/src/decision-tree-automation/decision-tree-automation-ui/index.html",
        os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
        os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"),
        "/app/decision-tree-automation-ui/index.html",
        os.path.join(os.getcwd(), "decision-tree-automation-ui/index.html")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrai a versão do conteúdo
                version_match = re.search(r'content="([^"]*version[^"]*)"', content)
                timestamp_match = re.search(r'Timestamp: ([^-]+)', content)
                
                return {
                    "frontend_found": True,
                    "path": path,
                    "size": len(content),
                    "version": version_match.group(1) if version_match else "Não encontrada",
                    "timestamp": timestamp_match.group(1).strip() if timestamp_match else "Não encontrado",
                    "check_time": datetime.datetime.now().isoformat(),
                    "cache_busting_url": f"/?v={datetime.datetime.now().timestamp()}"
                }
            except Exception as e:
                continue
    
    return {
        "frontend_found": False,
        "error": "Frontend não encontrado",
        "check_time": datetime.datetime.now().isoformat()
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
        from backend.models.responses_model import SessionLocal
        from backend.models.auto_alert_config_model import AutoAlertConfig
        
        # Garante que Rafael Cabral existe
        ensure_rafael_cabral_exists()
        
        # Verifica e carrega configuração do banco de dados
        db = SessionLocal()
        try:
            config = db.query(AutoAlertConfig).first()
            if not config:
                # Cria configuração padrão
                config = AutoAlertConfig(is_active=False, interval_minutes=3)
                db.add(config)
                db.commit()
                db.refresh(config)
                logger.info("Configuração padrão de alertas automáticos criada (desativada)")
            else:
                logger.info(f"Configuração carregada: ativo={config.is_active}, intervalo={config.interval_minutes}min")
            
            # Atualiza o scheduler com a configuração do banco
            auto_alert_scheduler.interval_minutes = config.interval_minutes
            
            # Inicia o scheduler se estiver ativo
            if config.is_active:
                auto_alert_scheduler.start()
                logger.info(f"✅ Scheduler iniciado com intervalo de {config.interval_minutes} minutos")
            else:
                logger.info("✅ Scheduler não iniciado (desativado na configuração)")
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            # Inicia com configuração padrão
            auto_alert_scheduler.start()
            logger.info("✅ Scheduler iniciado com configuração padrão")
        finally:
            db.close()
        
        logger.info("✅ Sistema inicializado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        # Continua mesmo se houver erro na inicialização

# Comentário: O backend segue o padrão MVC, separando models, views e controllers.
# O envio inicial de perguntas ocorre no evento de startup. 