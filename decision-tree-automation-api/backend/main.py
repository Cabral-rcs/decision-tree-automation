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
    return FileResponse(os.path.join(os.path.dirname(__file__), "../../decision-tree-automation-ui/index.html"))
    
# Ao iniciar o sistema, envie a primeira pergunta para todos os usuários
@app.on_event("startup")
def enviar_primeira_pergunta():
    for user_id in CHAT_IDS:
        enviar_pergunta_para_usuario(user_id)
    
    # Inicializa o scheduler de alertas automáticos
    from backend.services.auto_alert_scheduler import auto_alert_scheduler
    from backend.controllers.auto_alert_controller import ensure_rafael_cabral_exists
    
    # Garante que Rafael Cabral existe
    ensure_rafael_cabral_exists()
    
    # Inicia o scheduler
    auto_alert_scheduler.start()
    
    # Agenda com intervalo padrão (será atualizado se houver configuração)
    auto_alert_scheduler.schedule_auto_alert()

# Comentário: O backend segue o padrão MVC, separando models, views e controllers.
# O envio inicial de perguntas ocorre no evento de startup. 