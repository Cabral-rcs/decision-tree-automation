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
        
        # Criar alerta com todos os campos disponíveis
        novo_alerta = Alerta(
            chat_id=chat_id,
            problema=alerta['problema'],
            status='pendente',
            status_operacao='não operando',  # Status inicial
            nome_lider=nome_lider,
            # Novos campos se disponíveis
            codigo=alerta.get('codigo'),
            unidade=alerta.get('unidade'),
            frente=alerta.get('frente'),
            equipamento=alerta.get('equipamento'),
            codigo_equipamento=alerta.get('codigo_equipamento'),
            tipo_operacao=alerta.get('tipo_operacao'),
            operacao=alerta.get('operacao'),
            nome_operador=alerta.get('nome_operador'),
            data_operacao=datetime.fromisoformat(alerta.get('data_operacao')) if alerta.get('data_operacao') else None,
            tempo_abertura=alerta.get('tempo_abertura'),
            tipo_arvore=alerta.get('tipo_arvore'),
            justificativa=None,  # Campo não preenchido automaticamente
            prazo=None  # Campo preenchido pelo líder via Telegram
        )
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        # Envia mensagem ao líder no Telegram
        try:
            mensagem = f"Novo alerta criado:\n\n{novo_alerta.problema}\n\nQual a previsão para resolução?\n(Responda apenas o horário no formato HH:MM)"
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
        
        for alerta in db.query(Alerta).order_by(Alerta.criado_em.desc()).all():
            # Aguardando Previsão: Sem prazo respondido pelo líder
            if not alerta.prazo:
                pendentes.append(alerta)
                continue
            
            # Se tem prazo, verifica as outras categorias
            if alerta.status_operacao == 'operando':
                # Encerradas: Prazo não excedido e status operando
                if alerta.prazo >= now:
                    encerradas.append(alerta)
                else:
                    # Atrasadas: Prazo excedido mas status operando (caso raro)
                    atrasadas.append(alerta)
            else:
                # Status não operando
                if alerta.prazo >= now:
                    # Escaladas: Prazo respondido, atual dentro do prazo e status não operando
                    escaladas.append(alerta)
                else:
                    # Atrasadas: Prazo excedido e status não operando
                    atrasadas.append(alerta)
        
        return {
            "pendentes": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "criado_em": a.criado_em, 
                    "nome_lider": a.nome_lider, "codigo": a.codigo, "unidade": a.unidade, "frente": a.frente,
                    "equipamento": a.equipamento, "codigo_equipamento": a.codigo_equipamento, "tipo_operacao": a.tipo_operacao,
                    "operacao": a.operacao, "nome_operador": a.nome_operador, "data_operacao": a.data_operacao,
                    "tempo_abertura": a.tempo_abertura, "tipo_arvore": a.tipo_arvore, "justificativa": a.justificativa,
                    "prazo": a.prazo, "status_operacao": a.status_operacao
                } for a in pendentes
            ],
            "escaladas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao, "codigo": a.codigo, "unidade": a.unidade, "frente": a.frente,
                    "equipamento": a.equipamento, "codigo_equipamento": a.codigo_equipamento, "tipo_operacao": a.tipo_operacao,
                    "operacao": a.operacao, "nome_operador": a.nome_operador, "data_operacao": a.data_operacao,
                    "tempo_abertura": a.tempo_abertura, "tipo_arvore": a.tipo_arvore, "justificativa": a.justificativa,
                    "prazo": a.prazo
                } for a in escaladas
            ],
            "atrasadas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao, "codigo": a.codigo, "unidade": a.unidade, "frente": a.frente,
                    "equipamento": a.equipamento, "codigo_equipamento": a.codigo_equipamento, "tipo_operacao": a.tipo_operacao,
                    "operacao": a.operacao, "nome_operador": a.nome_operador, "data_operacao": a.data_operacao,
                    "tempo_abertura": a.tempo_abertura, "tipo_arvore": a.tipo_arvore, "justificativa": a.justificativa,
                    "prazo": a.prazo
                } for a in atrasadas
            ],
            "encerradas": [
                {
                    "id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, 
                    "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, 
                    "status_operacao": a.status_operacao, "horario_operando": a.horario_operando, "codigo": a.codigo, 
                    "unidade": a.unidade, "frente": a.frente, "equipamento": a.equipamento, "codigo_equipamento": a.codigo_equipamento, 
                    "tipo_operacao": a.tipo_operacao, "operacao": a.operacao, "nome_operador": a.nome_operador, 
                    "data_operacao": a.data_operacao, "tempo_abertura": a.tempo_abertura, "tipo_arvore": a.tipo_arvore, 
                    "justificativa": a.justificativa, "prazo": a.prazo
                } for a in encerradas
            ]
        }
    except Exception as e:
        logger.error(f"Erro ao listar alertas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close() 