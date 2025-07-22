# telegram_webhook.py - Controller para integração com o bot do Telegram
from fastapi import Request
from backend.models.responses_model import add_response, SessionLocal
from backend.models.alerta_model import Alerta
from datetime import datetime
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario

# Função para processar webhooks do Telegram
async def telegram_webhook(request: Request):
    data = await request.json()
    print('Recebido do Telegram:', data)  # LOG para depuração
    message = data.get('message', {})
    user_id = message.get('from', {}).get('id')
    timestamp = datetime.utcfromtimestamp(message.get('date')).isoformat() if message.get('date') else None
    resposta = message.get('text') or '[outro tipo de mensagem]'
    # Tenta associar resposta a um alerta pendente desse chat
    db = SessionLocal()
    try:
        alerta = db.query(Alerta).filter(Alerta.chat_id == str(user_id), Alerta.status == 'pendente').order_by(Alerta.criado_em.asc()).first()
        if alerta:
            alerta.previsao = resposta
            alerta.status = 'escalada'
            alerta.respondido_em = datetime.utcnow()
            db.commit()
            print(f'Alerta {alerta.id} atualizado com previsão: {resposta}')
        # Armazena também como resposta geral (opcional)
        if user_id and resposta and timestamp:
            add_response({
                'user_id': str(user_id),
                'pergunta': alerta.problema if alerta else 'Pergunta automática',
                'resposta': resposta,
                'timestamp': timestamp
            })
        return {"status": "ok", "msg": "Resposta armazenada"}
    finally:
        db.close() 