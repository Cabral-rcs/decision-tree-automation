# telegram_webhook.py - Controller para integração com o bot do Telegram
from fastapi import Request, HTTPException
from backend.models.responses_model import add_response, SessionLocal
from backend.models.alerta_model import Alerta
from datetime import datetime, timedelta
from backend.controllers.telegram_scheduler import enviar_pergunta_para_usuario
import pytz
import re
from backend.config import TELEGRAM_API_URL
import requests
import logging
import json
import traceback

# Configurar logging mais detalhado
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para processar webhooks do Telegram
async def telegram_webhook(request: Request):
    """Processa webhooks do Telegram"""
    logger.info("🚀 INICIANDO PROCESSAMENTO DO WEBHOOK")
    print("🚀 INICIANDO PROCESSAMENTO DO WEBHOOK")
    
    # Log de headers para debug
    headers = dict(request.headers)
    logger.info(f"📋 Headers recebidos: {json.dumps(headers, indent=2)}")
    print(f"📋 Headers recebidos: {json.dumps(headers, indent=2)}")
    
    try:
        # Log do corpo da requisição
        body = await request.body()
        logger.info(f"📦 Body recebido (bytes): {len(body)} bytes")
        print(f"📦 Body recebido (bytes): {len(body)} bytes")
        
        # Tenta fazer parse do JSON
        try:
            data = await request.json()
            logger.info(f'📥 Dados JSON recebidos no webhook: {json.dumps(data, indent=2)}')
            print(f'📥 Dados JSON recebidos no webhook: {json.dumps(data, indent=2)}')
        except Exception as json_error:
            logger.error(f'❌ Erro ao fazer parse do JSON: {json_error}')
            print(f'❌ Erro ao fazer parse do JSON: {json_error}')
            print(f'📄 Conteúdo raw: {body.decode("utf-8", errors="ignore")}')
            return {"status": "error", "msg": f"Erro ao fazer parse do JSON: {json_error}"}
        
        # Verifica se é uma mensagem válida
        if 'message' not in data:
            logger.warning('❌ Webhook não contém mensagem')
            print('❌ Webhook não contém mensagem')
            logger.info(f'📋 Estrutura dos dados: {list(data.keys())}')
            print(f'📋 Estrutura dos dados: {list(data.keys())}')
            return {"status": "ignored", "msg": "Não é uma mensagem"}
        
        message = data.get('message', {})
        user_id = message.get('from', {}).get('id')
        nome_lider = message.get('from', {}).get('first_name', '')
        if message.get('from', {}).get('last_name'):
            nome_lider += ' ' + message['from']['last_name']
        
        # Log detalhado da mensagem
        logger.info(f'📨 Mensagem detalhada: {json.dumps(message, indent=2)}')
        print(f'📨 Mensagem detalhada: {json.dumps(message, indent=2)}')
        
        # Data da mensagem em UTC
        msg_utc = datetime.utcfromtimestamp(message.get('date')) if message.get('date') else None
        # Converter para horário de Brasília
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.replace(tzinfo=pytz.utc).astimezone(tz_br) if msg_utc else None
        resposta = message.get('text') or '[outro tipo de mensagem]'
        
        logger.info(f'👤 Processando mensagem de {nome_lider} (ID: {user_id}): {resposta}')
        print(f'👤 Processando mensagem de {nome_lider} (ID: {user_id}): {resposta}')
        print(f'⏰ Data da mensagem (UTC): {msg_utc}')
        print(f'⏰ Data da mensagem (BR): {msg_br}')
        
        # Verifica se é o Rafael Cabral (validação mais flexível)
        nome_completo = nome_lider.lower()
        is_rafael = ('rafael' in nome_completo or 'cabral' in nome_completo or user_id == 6435800936)
        
        logger.info(f'🔍 Validação de usuário: nome="{nome_completo}", user_id={user_id}, is_rafael={is_rafael}')
        print(f'🔍 Validação de usuário: nome="{nome_completo}", user_id={user_id}, is_rafael={is_rafael}')
        
        if not is_rafael:
            logger.info(f'🚫 Mensagem ignorada - não é do Rafael Cabral: {nome_lider} (ID: {user_id})')
            print(f'🚫 Mensagem ignorada - não é do Rafael Cabral: {nome_lider} (ID: {user_id})')
            return {"status": "ignored", "msg": "Não é do líder autorizado"}
        
        logger.info(f'✅ Usuário autorizado: {nome_lider} (ID: {user_id})')
        print(f'✅ Usuário autorizado: {nome_lider} (ID: {user_id})')
        
        db = SessionLocal()
        try:
            # Busca o alerta mais antigo sem previsão (previsao = null)
            alerta = db.query(Alerta).filter(
                Alerta.previsao.is_(None)
            ).order_by(Alerta.criado_em.asc()).first()
            
            if not alerta:
                logger.warning('Nenhum alerta pendente encontrado')
                print('⚠️  Nenhum alerta pendente encontrado')
                
                # Verifica se há alertas no sistema
                total_alertas = db.query(Alerta).count()
                logger.info(f'Total de alertas no sistema: {total_alertas}')
                print(f'📊 Total de alertas no sistema: {total_alertas}')
                
                # Lista todos os alertas para debug
                todos_alertas = db.query(Alerta).all()
                logger.info(f'📋 Todos os alertas: {[(a.id, a.previsao, a.status) for a in todos_alertas]}')
                print(f'📋 Todos os alertas: {[(a.id, a.previsao, a.status) for a in todos_alertas]}')
                
                # Envia mensagem informando que não há alertas pendentes
                payload = {
                    'chat_id': user_id,
                    'text': f'Não há alertas pendentes aguardando previsão no momento.\n\nTotal de alertas no sistema: {total_alertas}'
                }
                resp_telegram = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
                if resp_telegram.ok:
                    logger.info(f'Mensagem de "sem alertas" enviada para {user_id}')
                    print(f'📤 Mensagem de "sem alertas" enviada')
                else:
                    logger.error(f'Erro ao enviar mensagem: {resp_telegram.status_code} - {resp_telegram.text}')
                    print(f'❌ Erro ao enviar mensagem: {resp_telegram.status_code}')
                
                return {"status": "no_pending", "msg": "Nenhum alerta pendente"}
            
            # Log de debug: mostra o alerta que será processado
            logger.info(f'Alerta a ser processado: ID {alerta.id}, Criado: {alerta.criado_em}')
            print(f'🎯 Alerta a ser processado: ID {alerta.id}')
            print(f'   Criado em: {alerta.criado_em}')
            print(f'   Problema: {alerta.problema[:100]}...')
            print(f'   Status atual: {alerta.status}')
            print(f'   Previsão atual: {alerta.previsao}')
            
            # Verifica quantos alertas pendentes existem no total
            total_pendentes = db.query(Alerta).filter(
                Alerta.previsao.is_(None)
            ).count()
            
            print(f'📋 Total de alertas pendentes na fila: {total_pendentes}')
            
            # Validação do padrão HH:MM
            padrao = r'^(\d{2}):(\d{2})$'
            match = re.match(padrao, resposta)
            if not match:
                logger.warning(f'Formato inválido de resposta: {resposta}')
                print(f'❌ Formato inválido: {resposta}')
                
                # Pede novamente com instruções claras
                payload = {
                    'chat_id': user_id,
                    'text': f'Por favor, informe a previsão apenas no formato HH:MM (ex: 15:30).\n\nAlerta ID: {alerta.id}\nProblema: {alerta.problema[:100]}...\n\nAlertas na fila: {total_pendentes}'
                }
                resp_telegram = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
                if resp_telegram.ok:
                    logger.info(f'Instruções de formato enviadas para {user_id}')
                    print(f'📤 Instruções de formato enviadas')
                else:
                    logger.error(f'Erro ao enviar instruções: {resp_telegram.status_code}')
                    print(f'❌ Erro ao enviar instruções: {resp_telegram.status_code}')
                
                return {"status": "invalid_format", "msg": "Formato inválido"}
            
            # Montar datetime da previsão - CORREÇÃO: Sempre usar horário atual como base
            hora, minuto = match.groups()
            
            # CORREÇÃO: Sempre usar o horário atual de Brasília como base, não a data da mensagem
            tz_br = pytz.timezone('America/Sao_Paulo')
            now_br = datetime.now(tz_br)
            
            # Cria o datetime da previsão para HOJE com o horário informado
            previsao_dt = now_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
            
            # CORREÇÃO: Se a previsão está no passado, move para o próximo dia
            if previsao_dt <= now_br:
                # Se a previsão está no passado, move para o próximo dia
                previsao_dt = previsao_dt + timedelta(days=1)
                logger.info(f'Previsão ajustada para o próximo dia: {resposta} -> {previsao_dt}')
                print(f'⏰ Previsão ajustada para o próximo dia: {resposta} -> {previsao_dt}')
            else:
                logger.info(f'Previsão processada: {resposta} -> {previsao_dt}')
                print(f'⏰ Previsão processada: {resposta} -> {previsao_dt}')
            
            # Atualiza o alerta específico com a previsão
            logger.info(f'Atualizando alerta {alerta.id} com previsão: {resposta}')
            print(f'🔄 Atualizando alerta {alerta.id} com previsão: {resposta}')
            
            # CORREÇÃO: Usar o horário atual real para respondido_em, não dados fictícios
            alerta.previsao = resposta
            alerta.previsao_datetime = previsao_dt
            alerta.respondido_em = now_br  # Usa o horário atual real
            alerta.nome_lider = nome_lider
            alerta.status = 'escalada'  # Muda status para escalada
            
            # Força o commit e verifica se foi salvo
            db.commit()
            db.refresh(alerta)  # Recarrega o objeto do banco
            
            # Verifica se a atualização foi bem-sucedida
            alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
            if alerta_atualizado and alerta_atualizado.previsao:
                logger.info(f'✅ Alerta {alerta.id} atualizado com sucesso - Previsão: {alerta_atualizado.previsao}')
                print(f'✅ Alerta {alerta.id} atualizado com sucesso - Previsão: {alerta_atualizado.previsao}')
                print(f'✅ Status alterado para: {alerta_atualizado.status}')
                print(f'✅ Timestamp de resposta: {alerta_atualizado.respondido_em}')
                print(f'✅ Previsão datetime: {alerta_atualizado.previsao_datetime}')
            else:
                logger.error(f'❌ Falha ao atualizar alerta {alerta.id}')
                print(f'❌ Falha ao atualizar alerta {alerta.id}')
                raise Exception("Falha ao salvar previsão no banco de dados")
            
            # Verifica quantos alertas ainda estão pendentes
            alertas_restantes = db.query(Alerta).filter(
                Alerta.previsao.is_(None)
            ).count()
            
            # Confirmação para o líder
            mensagem_confirmacao = f'✅ Previsão registrada: {resposta}\n\n'
            mensagem_confirmacao += f'Alerta ID: {alerta.id}\n'
            mensagem_confirmacao += f'Problema: {alerta.problema[:100]}...\n\n'
            mensagem_confirmacao += f'O alerta foi movido para "Escaladas" e será monitorado até {resposta}.\n\n'
            
            if alertas_restantes > 0:
                mensagem_confirmacao += f'⚠️  Ainda há {alertas_restantes} alerta(s) pendente(s) na fila.'
            else:
                mensagem_confirmacao += f'✅ Todos os alertas foram processados!'
            
            payload = {
                'chat_id': user_id,
                'text': mensagem_confirmacao
            }
            resp_telegram = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
            if resp_telegram.ok:
                logger.info(f'Confirmação enviada para {user_id}')
                print(f'📤 Confirmação enviada')
            else:
                logger.error(f'Erro ao enviar confirmação: {resp_telegram.status_code} - {resp_telegram.text}')
                print(f'❌ Erro ao enviar confirmação: {resp_telegram.status_code}')
            
            # Armazena também como resposta geral (opcional)
            if user_id and resposta and msg_utc:
                try:
                    # Converte a string ISO para objeto datetime
                    if isinstance(msg_utc, str):
                        # Se for string, converte para datetime
                        timestamp_dt = datetime.fromisoformat(msg_utc.replace('Z', '+00:00'))
                    else:
                        # Se já for datetime, usa diretamente
                        timestamp_dt = msg_utc
                    
                    add_response({
                        'user_id': str(user_id),
                        'pergunta': alerta.problema,
                        'resposta': resposta,
                        'timestamp': timestamp_dt
                    })
                    logger.info(f'Resposta armazenada no histórico')
                    print(f'💾 Resposta armazenada no histórico')
                except Exception as resp_error:
                    logger.error(f'Erro ao armazenar resposta: {resp_error}')
                    print(f'❌ Erro ao armazenar resposta: {resp_error}')
                    # Continua mesmo se falhar o armazenamento da resposta
            
            return {
                "status": "success", 
                "msg": "Previsão registrada com sucesso", 
                "alerta_id": alerta.id,
                "alertas_restantes": alertas_restantes
            }
            
        except Exception as e:
            logger.error(f'❌ Erro ao processar alerta: {str(e)}')
            logger.error(f'❌ Traceback: {traceback.format_exc()}')
            print(f'❌ Erro ao processar alerta: {str(e)}')
            print(f'❌ Traceback: {traceback.format_exc()}')
            
            # Envia mensagem de erro para o usuário
            try:
                payload = {
                    'chat_id': user_id,
                    'text': '❌ Erro interno ao processar sua resposta. Tente novamente.'
                }
                requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
            except Exception as send_error:
                logger.error(f'Erro ao enviar mensagem de erro: {send_error}')
                print(f'❌ Erro ao enviar mensagem de erro: {send_error}')
            
            return {"status": "error", "msg": str(e)}
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f'❌ Erro geral no webhook: {str(e)}')
        logger.error(f'❌ Traceback: {traceback.format_exc()}')
        print(f'❌ Erro geral no webhook: {str(e)}')
        print(f'❌ Traceback: {traceback.format_exc()}')
        return {"status": "error", "msg": str(e)}
    finally:
        logger.info("🏁 FINALIZANDO PROCESSAMENTO DO WEBHOOK")
        print("🏁 FINALIZANDO PROCESSAMENTO DO WEBHOOK") 