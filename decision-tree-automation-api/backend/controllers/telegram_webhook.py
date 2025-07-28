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
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Função para processar webhooks do Telegram
async def telegram_webhook(request: Request):
    """Processa webhooks do Telegram"""
    try:
        data = await request.json()
        logger.info(f'Webhook recebido: {data}')
        print(f'🔔 WEBHOOK RECEBIDO: {data}')  # Log para debug
        
        # Verifica se é uma mensagem válida
        if 'message' not in data:
            logger.warning('Webhook não contém mensagem')
            return {"status": "ignored", "msg": "Não é uma mensagem"}
        
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
        
        logger.info(f'Processando mensagem de {nome_lider} (ID: {user_id}): {resposta}')
        print(f'📱 Processando: {nome_lider} ({user_id}) -> {resposta}')
        
        # Verifica se é o Rafael Cabral
        if 'Rafael' not in nome_lider and 'Cabral' not in nome_lider:
            logger.info(f'Mensagem ignorada - não é do Rafael Cabral: {nome_lider}')
            return {"status": "ignored", "msg": "Não é do líder autorizado"}
        
        db = SessionLocal()
        try:
            # Busca alerta pendente (sem prazo) - mais flexível
            alerta = db.query(Alerta).filter(
                Alerta.prazo.is_(None)
            ).order_by(Alerta.criado_em.asc()).first()
            
            if not alerta:
                logger.warning('Nenhum alerta pendente encontrado')
                print('⚠️  Nenhum alerta pendente encontrado')
                
                # Verifica se há alertas no sistema
                total_alertas = db.query(Alerta).count()
                logger.info(f'Total de alertas no sistema: {total_alertas}')
                print(f'📊 Total de alertas no sistema: {total_alertas}')
                
                # Envia mensagem informando que não há alertas pendentes
                payload = {
                    'chat_id': user_id,
                    'text': 'Não há alertas pendentes aguardando prazo no momento.'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
                return {"status": "no_pending", "msg": "Nenhum alerta pendente"}
            
            logger.info(f'Alerta encontrado: ID {alerta.id}, Problema: {alerta.problema[:50]}...')
            print(f'🎯 Alerta encontrado: ID {alerta.id}')
            
            # Validação do padrão HH:MM
            padrao = r'^(\d{2}):(\d{2})$'
            match = re.match(padrao, resposta)
            if not match:
                logger.warning(f'Formato inválido de resposta: {resposta}')
                print(f'❌ Formato inválido: {resposta}')
                
                # Pede novamente com instruções claras
                payload = {
                    'chat_id': user_id,
                    'text': f'Por favor, informe a previsão apenas no formato HH:MM (ex: 15:30).\n\nAlerta: {alerta.problema[:100]}...'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
                return {"status": "invalid_format", "msg": "Formato inválido"}
            
            # Montar datetime da previsão para o mesmo dia da resposta
            hora, minuto = match.groups()
            previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
            
            logger.info(f'Prazo processado: {resposta} -> {previsao_dt}')
            print(f'⏰ Prazo processado: {resposta} -> {previsao_dt}')
            
            # Atualiza o alerta com a previsão e prazo
            logger.info(f'Atualizando alerta {alerta.id} com resposta: {resposta}')
            print(f'🔄 Atualizando alerta {alerta.id} com resposta: {resposta}')
            
            alerta.previsao = resposta
            alerta.previsao_datetime = previsao_dt
            alerta.prazo = previsao_dt  # Campo prazo preenchido pelo líder
            alerta.respondido_em = datetime.utcnow()
            alerta.nome_lider = nome_lider
            
            # Força o commit e verifica se foi salvo
            db.commit()
            db.refresh(alerta)  # Recarrega o objeto do banco
            
            # Verifica se a atualização foi bem-sucedida
            alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
            if alerta_atualizado and alerta_atualizado.prazo:
                logger.info(f'✅ Alerta {alerta.id} atualizado com sucesso - Prazo: {alerta_atualizado.prazo}')
                print(f'✅ Alerta {alerta.id} atualizado com sucesso - Prazo: {alerta_atualizado.prazo}')
            else:
                logger.error(f'❌ Falha ao atualizar alerta {alerta.id}')
                print(f'❌ Falha ao atualizar alerta {alerta.id}')
                raise Exception("Falha ao salvar prazo no banco de dados")
            
            # Confirmação para o líder
            payload = {
                'chat_id': user_id,
                'text': f'✅ Prazo registrado: {resposta}\n\nAlerta: {alerta.problema[:100]}...\n\nO alerta será monitorado até este horário.'
            }
            resp_telegram = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
            if resp_telegram.ok:
                logger.info(f'Confirmação enviada para {user_id}')
                print(f'📤 Confirmação enviada')
            else:
                logger.error(f'Erro ao enviar confirmação: {resp_telegram.status_code}')
                print(f'❌ Erro ao enviar confirmação')
            
            # Armazena também como resposta geral (opcional)
            if user_id and resposta and msg_utc:
                add_response({
                    'user_id': str(user_id),
                    'pergunta': alerta.problema,
                    'resposta': resposta,
                    'timestamp': msg_utc.isoformat()
                })
            
            return {"status": "success", "msg": "Prazo registrado com sucesso"}
            
        except Exception as e:
            logger.error(f'Erro ao processar alerta: {str(e)}')
            print(f'❌ Erro ao processar alerta: {str(e)}')
            
            # Envia mensagem de erro para o usuário
            try:
                payload = {
                    'chat_id': user_id,
                    'text': '❌ Erro interno ao processar sua resposta. Tente novamente.'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
            except:
                pass
            
            return {"status": "error", "msg": str(e)}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f'Erro geral no webhook: {str(e)}')
        print(f'❌ Erro geral no webhook: {str(e)}')
        return {"status": "error", "msg": str(e)} 