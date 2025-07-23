from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.alerta_model import Alerta
from backend.config import TELEGRAM_API_URL
import requests
from datetime import datetime, timezone, timedelta
import pytz

router = APIRouter()

@router.post('/alertas')
def criar_alerta(alerta: dict):
    db: Session = SessionLocal()
    try:
        novo_alerta = Alerta(
            chat_id=alerta['chat_id'],
            problema=alerta['problema'],
            status='pendente'
        )
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        # Envia mensagem ao líder no Telegram
        mensagem = f"Qual a previsão para o problema: {novo_alerta.problema}?"
        payload = {
            'chat_id': novo_alerta.chat_id,
            'text': mensagem
        }
        resp = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
        if resp.ok:
            mensagem_id = resp.json().get('result', {}).get('message_id')
            novo_alerta.mensagem_id = mensagem_id
            db.commit()
        else:
            print('Erro ao enviar mensagem ao Telegram:', resp.text)
        return {"id": novo_alerta.id}
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
        # Se mudou para operando, vai para encerradas
        if novo_status == 'operando' and alerta.status == 'escalada':
            alerta.status = 'encerrada'
        db.commit()
        return {"ok": True}
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
            # Atualiza categorias dinamicamente
            if alerta.status == 'pendente':
                pendentes.append(alerta)
            elif alerta.status in ['escalada', 'atrasada', 'encerrada']:
                # Se previsão passou e não operando -> atrasada
                if alerta.status in ['escalada', 'atrasada'] and alerta.status_operacao == 'não operando' and alerta.previsao_datetime and alerta.previsao_datetime < now:
                    alerta.status = 'atrasada'
                    db.commit()
                    atrasadas.append(alerta)
                # Se operando -> encerrada
                elif alerta.status in ['escalada', 'encerrada'] and alerta.status_operacao == 'operando':
                    alerta.status = 'encerrada'
                    db.commit()
                    encerradas.append(alerta)
                # Se ainda escalada
                elif alerta.status == 'escalada':
                    escaladas.append(alerta)
                elif alerta.status == 'atrasada':
                    atrasadas.append(alerta)
                elif alerta.status == 'encerrada':
                    encerradas.append(alerta)
        return {
            "pendentes": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "criado_em": a.criado_em} for a in pendentes
            ],
            "escaladas": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, "status_operacao": a.status_operacao} for a in escaladas
            ],
            "atrasadas": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, "status_operacao": a.status_operacao} for a in atrasadas
            ],
            "encerradas": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, "previsao_datetime": a.previsao_datetime, "respondido_em": a.respondido_em, "nome_lider": a.nome_lider, "status_operacao": a.status_operacao} for a in encerradas
            ]
        }
    finally:
        db.close() 