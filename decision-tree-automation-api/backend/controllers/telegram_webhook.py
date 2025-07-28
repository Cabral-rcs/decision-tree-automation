# telegram_webhook.py - Controller para integração com o bot do Telegram
from fastapi import Request
from backend.models.responses_model import add_response, SessionLocal
from backend.models.alerta_model import Alerta
from datetime import datetime
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario
import pytz
import re
from backend.config import TELEGRAM_API_URL
import requests

# Função para processar webhooks do Telegram
async def telegram_webhook(request: Request):
    data = await request.json()
    print('Recebido do Telegram:', data)  # LOG para depuração
    message = data.get('message', {})
    user_id = message.get('from', {}).get('id')
    nome_lider = message.get('from', {}).get('first_name', '')
    if message.get('from', {}).get('last_name'):
        nome_lider += ' ' + message['from']['last_name']
    # Data da mensagem em UTC
    msg_utc = datetime.utcfromtimestamp(message.get('date')) if message.get('date') else None
    # Converter para horário de Brasília
    tz_br = pytz.timezone('America/Sao_Paulo')
    msg_br = msg_utc.replace(tzinfo=pytz.utc).astimezone(tz_br) if msg_utc else None
    resposta = message.get('text') or '[outro tipo de mensagem]'
    db = SessionLocal()
    try:
        # Busca alerta pendente (sem prazo) para o líder Rafael Cabral
        alerta = db.query(Alerta).filter(
            Alerta.nome_lider == 'Rafael Cabral', 
            Alerta.prazo.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if alerta:
            # Validação do padrão HH:MM
            padrao = r'^(\d{2}):(\d{2})$'
            match = re.match(padrao, resposta)
            if not match:
                # Pede novamente
                payload = {
                    'chat_id': user_id,
                    'text': 'Por favor, informe a previsão apenas no formato HH:MM (ex: 15:30).'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
                return {"status": "erro", "msg": "Formato inválido"}
            
            # Montar datetime da previsão para o mesmo dia da resposta
            hora, minuto = match.groups()
            previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
            
            # Atualiza o alerta com a previsão e prazo
            alerta.previsao = resposta
            alerta.previsao_datetime = previsao_dt
            alerta.prazo = previsao_dt  # Campo prazo preenchido pelo líder
            alerta.respondido_em = datetime.utcnow()
            alerta.nome_lider = nome_lider
            
            db.commit()
            print(f'Alerta {alerta.id} atualizado com previsão: {resposta} e prazo: {previsao_dt}')
            
            # Confirmação para o líder
            payload = {
                'chat_id': user_id,
                'text': f'Prazo registrado: {resposta}. O alerta será monitorado até este horário.'
            }
            requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
            
        # Armazena também como resposta geral (opcional)
        if user_id and resposta and msg_utc:
            add_response({
                'user_id': str(user_id),
                'pergunta': alerta.problema if alerta else 'Pergunta automática',
                'resposta': resposta,
                'timestamp': msg_utc.isoformat()
            })
        return {"status": "ok", "msg": "Resposta armazenada"}
    finally:
        db.close() 