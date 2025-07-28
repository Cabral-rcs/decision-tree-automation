# main.py - Inicialização do backend FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.views import api_router
from backend.controllers import telegram_scheduler  # Importa o scheduler para iniciar o agendamento
from backend.config import CHAT_IDS
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario
from fastapi.responses import FileResponse
import os
from backend.controllers.alerta_controller import router as alerta_router
from backend.controllers.lider_controller import router as lider_router
from backend.controllers.auto_alert_controller import router as auto_alert_router
app = FastAPI()

# Adiciona o middleware de CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
# Inclui as rotas da view (API)
app.include_router(alerta_router)
app.include_router(lider_router)
app.include_router(auto_alert_router)


@app.get("/")
def get_frontend():
    # Caminhos otimizados baseados no teste
    possible_paths = [
        # Caminho que funciona localmente e no Render
        os.path.join(os.getcwd(), "../decision-tree-automation-ui/index.html"),
        # Caminho alternativo
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "decision-tree-automation-ui/index.html"),
        # Caminho para desenvolvimento local
        os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return FileResponse(path)
    
    # Se não encontrar o arquivo, retorna uma página de erro informativa
    return {
        "error": "Frontend não encontrado",
        "message": "O arquivo index.html não foi encontrado nos caminhos esperados",
        "possible_paths": possible_paths,
        "current_directory": os.getcwd(),
        "backend_directory": os.path.dirname(__file__)
    }
    
# Ao iniciar o sistema, envie a primeira pergunta para todos os usuários
@app.on_event("startup")
def enviar_primeira_pergunta():
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
    except Exception as e:
        print(f"Erro na inicialização: {e}")
        # Continua mesmo se houver erro na inicialização

# Comentário: O backend segue o padrão MVC, separando models, views e controllers.
# O envio inicial de perguntas ocorre no evento de startup. 