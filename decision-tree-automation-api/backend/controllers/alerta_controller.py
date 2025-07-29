from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.alerta_model import Alerta
from backend.config import TELEGRAM_API_URL
import requests
from datetime import datetime, timezone, timedelta
import pytz

import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post('/alertas')
def criar_alerta(alerta: dict):
    db: Session = SessionLocal()
    try:
        # Validação dos dados obrigatórios
        if not alerta.get('problema'):
            raise HTTPException(status_code=400, detail='Problema é obrigatório')
        
        # Usar Rafael Cabral como líder fixo
        nome_lider = 'Rafael Cabral'
        chat_id = '6435800936'
        
        # Criar alerta com campos essenciais
        novo_alerta = Alerta(
            chat_id=chat_id,
            problema=alerta['problema'],
            status='pendente',
            status_operacao='não operando',  # Status inicial
            nome_lider=nome_lider
        )
        logger.info(f"Criando alerta: problema={alerta['problema']}, status_operacao=não operando")
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        # Envia mensagem ao líder no Telegram
        try:
            mensagem = f"Qual o prazo para resolução do problema?\n\n{novo_alerta.problema}\n\n(Responda apenas o horário no formato HH:MM)"
            payload = {
                'chat_id': novo_alerta.chat_id,
                'text': mensagem
            }
            resp = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
            if resp.ok:
                mensagem_id = resp.json().get('result', {}).get('message_id')
                novo_alerta.mensagem_id = mensagem_id
                db.commit()
                logger.info(f"Mensagem enviada ao Telegram para chat_id {novo_alerta.chat_id}")
            else:
                logger.warning(f'Erro ao enviar mensagem ao Telegram: {resp.status_code} - {resp.text}')
        except Exception as e:
            logger.error(f'Erro ao enviar mensagem ao Telegram: {str(e)}')
            # Continua mesmo se falhar o envio da mensagem
        
        return {"id": novo_alerta.id, "message": "Alerta criado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar alerta: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close()

@router.put('/alertas/{alerta_id}/status')
def atualizar_status_operacao(alerta_id: int, body: dict):
    novo_status = body.get('status_operacao')
    if novo_status not in ['operando', 'não operando']:
        raise HTTPException(status_code=400, detail='Status inválido')
    
    db: Session = SessionLocal()
    try:
        alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
        if not alerta:
            raise HTTPException(status_code=404, detail='Alerta não encontrado')
        
        alerta.status_operacao = novo_status
        # Se mudou para operando, salva o horário
        if novo_status == 'operando':
            tz_br = pytz.timezone('America/Sao_Paulo')
            alerta.horario_operando = datetime.now(tz_br)
        # Se mudou para operando, vai para encerradas
        if novo_status == 'operando' and alerta.status == 'escalada':
            alerta.status = 'encerrada'
        
        db.commit()
        logger.info(f"Status do alerta {alerta_id} atualizado para {novo_status}")
        return {"ok": True, "message": f"Status atualizado para {novo_status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status do alerta {alerta_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close()

@router.get('/alertas')
def listar_alertas():
    db: Session = SessionLocal()
    try:
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        pendentes = []
        escaladas = []
        atrasadas = []
        encerradas = []
        
        logger.info(f"Listando alertas - horário atual: {now}")
        
        for alerta in db.query(Alerta).order_by(Alerta.criado_em.desc()).all():
            logger.info(f"Processando alerta ID {alerta.id}: previsao={alerta.previsao}, status_operacao={alerta.status_operacao}")
            
            # Modelo chave-valor: se não tem previsão, está pendente
            if not alerta.previsao:
                pendentes.append(alerta)
                logger.info(f"Alerta {alerta.id} adicionado aos pendentes (sem previsão)")
                continue
            
            # Se tem previsão, verifica as outras categorias baseado no status de operação
            if alerta.status_operacao == 'operando':
                # Encerradas: Previsão não excedida e status operando
                if alerta.previsao_datetime >= now:
                    encerradas.append(alerta)
                    logger.info(f"Alerta {alerta.id} adicionado aos encerrados")
                else:
                    # Atrasadas: Previsão excedida mas status operando (caso raro)
                    atrasadas.append(alerta)
                    logger.info(f"Alerta {alerta.id} adicionado aos atrasados (operando mas previsão excedida)")
            else:
                # Status não operando
                if alerta.previsao_datetime >= now:
                    # Escaladas: Com previsão, dentro da previsão e status não operando
                    escaladas.append(alerta)
                    logger.info(f"Alerta {alerta.id} adicionado aos escalados (com previsão: {alerta.previsao})")
                else:
                    # Atrasadas: Previsão excedida e status não operando
                    atrasadas.append(alerta)
                    logger.info(f"Alerta {alerta.id} adicionado aos atrasados (previsão excedida)")
        
        return {
            "pendentes": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "criado_em": a.criado_em, 
                    "nome_lider": a.nome_lider, "status_operacao": a.status_operacao, "previsao": None
                } for a in pendentes
            ],
            "escaladas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao
                } for a in escaladas
            ],
            "atrasadas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao
                } for a in atrasadas
            ],
            "encerradas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao, "horario_operando": a.horario_operando
                } for a in encerradas
            ]
        }
    except Exception as e:
        logger.error(f"Erro ao listar alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close()

@router.post("/alertas/forcar-atualizacao")
def forcar_atualizacao():
    """Força uma atualização dos alertas"""
    db = SessionLocal()
    try:
        # Simplesmente retorna o status atual para forçar o frontend a recarregar
        total_alertas = db.query(Alerta).count()
        alertas_com_previsao = db.query(Alerta).filter(Alerta.previsao.isnot(None)).count()
        
        logger.info(f"Forçando atualização - Total: {total_alertas}, Com previsão: {alertas_com_previsao}")
        
        return {
            "success": True,
            "message": "Atualização forçada",
            "total_alertas": total_alertas,
            "alertas_com_previsao": alertas_com_previsao,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao forçar atualização: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close()

@router.get("/alertas/ultima-atualizacao")
def get_ultima_atualizacao():
    """Retorna a data da última atualização de alertas"""
    db = SessionLocal()
    try:
        # Busca o alerta mais recentemente atualizado considerando múltiplos campos
        ultimo_alerta_respondido = db.query(Alerta).filter(
            Alerta.respondido_em.isnot(None)
        ).order_by(Alerta.respondido_em.desc()).first()
        
        ultimo_alerta_criado = db.query(Alerta).order_by(Alerta.criado_em.desc()).first()
        
        ultimo_alerta_previsao = db.query(Alerta).filter(
            Alerta.previsao_datetime.isnot(None)
        ).order_by(Alerta.previsao_datetime.desc()).first()
        
        # Determina qual é o mais recente
        timestamps = []
        if ultimo_alerta_respondido and ultimo_alerta_respondido.respondido_em:
            timestamps.append(('respondido_em', ultimo_alerta_respondido.respondido_em, ultimo_alerta_respondido.id))
        
        if ultimo_alerta_criado and ultimo_alerta_criado.criado_em:
            timestamps.append(('criado_em', ultimo_alerta_criado.criado_em, ultimo_alerta_criado.id))
            
        if ultimo_alerta_previsao and ultimo_alerta_previsao.previsao_datetime:
            timestamps.append(('previsao_datetime', ultimo_alerta_previsao.previsao_datetime, ultimo_alerta_previsao.id))
        
        if timestamps:
            # Pega o timestamp mais recente
            timestamps.sort(key=lambda x: x[1], reverse=True)
            campo_mais_recente, timestamp_mais_recente, alerta_id = timestamps[0]
            
            return {
                "ultima_atualizacao": timestamp_mais_recente.isoformat(),
                "alerta_id": alerta_id,
                "campo_atualizado": campo_mais_recente,
                "tem_atualizacao": True
            }
        else:
            return {
                "ultima_atualizacao": None,
                "alerta_id": None,
                "campo_atualizado": None,
                "tem_atualizacao": False
            }
    except Exception as e:
        logger.error(f"Erro ao buscar última atualização: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close()

@router.get("/alertas/debug")
def debug_alertas():
    """Endpoint para debug dos alertas"""
    db = SessionLocal()
    try:
        total_alertas = db.query(Alerta).count()
        pendentes = db.query(Alerta).filter(Alerta.previsao.is_(None)).count()
        com_previsao = db.query(Alerta).filter(Alerta.previsao.isnot(None)).count()
        
        # Últimos 5 alertas
        ultimos_alertas = db.query(Alerta).order_by(Alerta.criado_em.desc()).limit(5).all()
        
        return {
            "total_alertas": total_alertas,
            "pendentes": pendentes,
            "com_previsao": com_previsao,
            "ultimos_alertas": [
                {
                    "id": a.id,
                    "problema": a.problema[:50] + "..." if len(a.problema) > 50 else a.problema,
                    "previsao": a.previsao,
                    "previsao_datetime": a.previsao_datetime.isoformat() if a.previsao_datetime else None,
                    "respondido_em": a.respondido_em.isoformat() if a.respondido_em else None,
                    "status_operacao": a.status_operacao,
                    "criado_em": a.criado_em.isoformat() if a.criado_em else None
                } for a in ultimos_alertas
            ]
        }
    except Exception as e:
        logger.error(f"Erro no debug de alertas: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close()

@router.delete('/alertas/all')
def apagar_todos_alertas():
    """Apaga todos os alertas do sistema"""
    db: Session = SessionLocal()
    try:
        # Conta quantos alertas existem antes de apagar
        total_alertas = db.query(Alerta).count()
        
        # Apaga todos os alertas
        db.query(Alerta).delete()
        db.commit()
        
        logger.info(f"Todos os {total_alertas} alertas foram apagados")
        
        return {
            "success": True,
            "message": f"Todos os {total_alertas} alertas foram apagados com sucesso",
            "alertas_apagados": total_alertas
        }
    except Exception as e:
        logger.error(f"Erro ao apagar alertas: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close() 