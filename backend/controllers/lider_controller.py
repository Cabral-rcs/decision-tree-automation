from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.lider_model import Lider

router = APIRouter()

@router.get('/lideres')
def listar_lideres():
    db: Session = SessionLocal()
    try:
        return [
            {"id": l.id, "nome_lider": l.nome_lider, "chat_id": l.chat_id}
            for l in db.query(Lider).order_by(Lider.nome_lider.asc()).all()
        ]
    finally:
        db.close()

@router.post('/lideres')
def criar_lider(lider: dict):
    db: Session = SessionLocal()
    try:
        if db.query(Lider).filter((Lider.nome_lider == lider['nome_lider']) | (Lider.chat_id == lider['chat_id'])).first():
            raise HTTPException(status_code=400, detail='Nome ou chat_id já cadastrado')
        novo = Lider(nome_lider=lider['nome_lider'], chat_id=lider['chat_id'])
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return {"id": novo.id}
    finally:
        db.close()

@router.put('/lideres/{lider_id}')
def editar_lider(lider_id: int, body: dict):
    db: Session = SessionLocal()
    try:
        lider = db.query(Lider).filter(Lider.id == lider_id).first()
        if not lider:
            raise HTTPException(status_code=404, detail='Líder não encontrado')
        if 'nome_lider' in body:
            lider.nome_lider = body['nome_lider']
        if 'chat_id' in body:
            lider.chat_id = body['chat_id']
        db.commit()
        return {"ok": True}
    finally:
        db.close()

@router.delete('/lideres/{lider_id}')
def remover_lider(lider_id: int):
    db: Session = SessionLocal()
    try:
        lider = db.query(Lider).filter(Lider.id == lider_id).first()
        if not lider:
            raise HTTPException(status_code=404, detail='Líder não encontrado')
        db.delete(lider)
        db.commit()
        return {"ok": True}
    finally:
        db.close() 