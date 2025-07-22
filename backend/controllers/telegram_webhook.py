# telegram_webhook.py - Controller para integração com o bot do Telegram
from fastapi import Request
from backend.models.responses_model import add_response
from datetime import datetime
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario

# Função para processar webhooks do Telegram
async def telegram_webhook(request: Request):
    data = await request.json()
    print('Recebido do Telegram:', data)  # LOG para depuração
    # Extrai informações relevantes do update do Telegram
    message = data.get('message', {})
    user_id = message.get('from', {}).get('id')
    timestamp = datetime.utcfromtimestamp(message.get('date')).isoformat() if message.get('date') else None
    pergunta = 'Pergunta automática'  # Pode ser customizada se necessário

    # Tenta capturar qualquer tipo de resposta textual ou mídia
    if 'text' in message:
        resposta = message['text']
    elif 'sticker' in message:
        resposta = f"[sticker] {message['sticker'].get('emoji', '')}"
    elif 'photo' in message:
        resposta = '[foto]'
    elif 'voice' in message:
        resposta = '[áudio]'
    elif 'document' in message:
        resposta = '[documento]'
    else:
        resposta = '[outro tipo de mensagem]'

    # Armazena a resposta no banco
    if user_id and resposta and timestamp:
        add_response({
            'user_id': str(user_id),
            'pergunta': pergunta,
            'resposta': resposta,
            'timestamp': timestamp
        })
        print('Resposta armazenada com sucesso!')  # LOG para depuração
        # Envia a próxima pergunta imediatamente
        enviar_pergunta_para_usuario(user_id)
        return {"status": "ok", "msg": "Resposta armazenada"}
    else:
        print('Dados insuficientes para armazenar resposta.')  # LOG para depuração
        return {"status": "erro", "msg": "Dados insuficientes"} 