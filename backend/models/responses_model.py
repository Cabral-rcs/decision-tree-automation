# responses_model.py - Model para respostas usando SQLAlchemy/PostgreSQL
import os
from typing import List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func
from dotenv import load_dotenv
from backend.models.alerta_model import Alerta, Base as AlertaBase, force_recreate_alerta_table

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL não configurada!')

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Resposta(Base):
    __tablename__ = 'respostas'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    pergunta = Column(Text)
    resposta = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class EstadoUsuario(Base):
    __tablename__ = 'estado_usuario'
    user_id = Column(String, primary_key=True, index=True)
    aguardando_resposta = Column(Boolean, default=False)

def init_db():
    try:
        force_recreate_alerta_table()  # Força o drop e recriação da tabela alertas
        Base.metadata.create_all(bind=engine)
        AlertaBase.metadata.create_all(bind=engine)
    except OperationalError as e:
        print('Erro ao conectar ao banco:', e)

# CRUD

def add_response(data: Dict):
    db = SessionLocal()
    try:
        resposta = Resposta(
            user_id=data['user_id'],
            pergunta=data['pergunta'],
            resposta=data['resposta'],
            timestamp=data['timestamp']
        )
        db.add(resposta)
        # Marca que o usuário não está mais aguardando resposta
        estado = db.query(EstadoUsuario).filter_by(user_id=data['user_id']).first()
        if not estado:
            estado = EstadoUsuario(user_id=data['user_id'], aguardando_resposta=False)
            db.add(estado)
        else:
            estado.aguardando_resposta = False
        db.commit()
    finally:
        db.close()

def get_all_responses() -> List[Dict]:
    db = SessionLocal()
    try:
        respostas = db.query(Resposta).order_by(Resposta.timestamp.desc()).all()
        return [
            {
                "user_id": r.user_id,
                "pergunta": r.pergunta,
                "resposta": r.resposta,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None
            }
            for r in respostas
        ]
    finally:
        db.close()

def set_aguardando_resposta(user_id: str):
    db = SessionLocal()
    try:
        estado = db.query(EstadoUsuario).filter_by(user_id=user_id).first()
        if not estado:
            estado = EstadoUsuario(user_id=user_id, aguardando_resposta=True)
            db.add(estado)
        else:
            estado.aguardando_resposta = True
        db.commit()
    finally:
        db.close()

def is_aguardando_resposta(user_id: str) -> bool:
    db = SessionLocal()
    try:
        estado = db.query(EstadoUsuario).filter_by(user_id=user_id).first()
        return bool(estado and estado.aguardando_resposta)
    finally:
        db.close()

init_db() 