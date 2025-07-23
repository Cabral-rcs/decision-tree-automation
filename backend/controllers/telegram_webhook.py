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
    timestamp = datetime.utcfromtimestamp(message.get('date')).isoformat() if message.get('date') else None
    resposta = message.get('text') or '[outro tipo de mensagem]'
    db = SessionLocal()
    try:
        alerta = db.query(Alerta).filter(Alerta.chat_id == str(user_id), Alerta.status == 'pendente').order_by(Alerta.criado_em.asc()).first()
        if alerta:
            # Validação do padrão 00:00 DD/MM/AAAA
            padrao = r'^(\d{2}):(\d{2}) (\d{2})/(\d{2})/(\d{4})$'
            match = re.match(padrao, resposta)
            if not match:
                # Pede novamente
                payload = {
                    'chat_id': user_id,
                    'text': 'Por favor, informe a previsão no formato 00:00 DD/MM/AAAA.'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
                return {"status": "erro", "msg": "Formato inválido"}
            # Converter para datetime (Brasília)
            hora, minuto, dia, mes, ano = match.groups()
            previsao_dt = datetime(int(ano), int(mes), int(dia), int(hora), int(minuto), tzinfo=pytz.timezone('America/Sao_Paulo'))
            alerta.previsao = resposta
            alerta.previsao_datetime = previsao_dt
            alerta.status = 'escalada'
            alerta.respondido_em = datetime.utcnow()
            alerta.nome_lider = nome_lider
            db.commit()
            print(f'Alerta {alerta.id} atualizado com previsão: {resposta} e nome: {nome_lider}')
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