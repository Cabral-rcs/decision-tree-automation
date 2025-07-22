from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.alerta_model import Alerta
from backend.config import TELEGRAM_API_URL
import requests
from datetime import datetime

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

@router.get('/alertas')
def listar_alertas():
    db: Session = SessionLocal()
    try:
        pendentes = db.query(Alerta).filter(Alerta.status == 'pendente').order_by(Alerta.criado_em.desc()).all()
        escaladas = db.query(Alerta).filter(Alerta.status == 'escalada').order_by(Alerta.criado_em.desc()).all()
        return {
            "pendentes": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "criado_em": a.criado_em} for a in pendentes
            ],
            "escaladas": [
                {"id": a.id, "chat_id": a.chat_id, "problema": a.problema, "previsao": a.previsao, "respondido_em": a.respondido_em} for a in escaladas
            ]
        }
    finally:
        db.close() 