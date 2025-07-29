# responses_model.py - Model para respostas usando SQLAlchemy/PostgreSQL
import os
from typing import List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import func
from dotenv import load_dotenv
from backend.models.alerta_model import Alerta, Base as AlertaBase, force_recreate_alerta_table
from backend.models.auto_alert_config_model import AutoAlertConfig, Base as AutoAlertConfigBase
from backend.config import DATABASE_URL

load_dotenv()

Base = declarative_base()

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    pergunta = Column(Text)
    resposta = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class EstadoUsuario(Base):
    __tablename__ = 'estado_usuario'
    user_id = Column(String, primary_key=True, index=True)
    aguardando_resposta = Column(Boolean, default=False)

# Cria o engine com a configuração centralizada
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria a sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Inicializa o banco de dados"""
    Base.metadata.create_all(bind=engine)
    AlertaBase.metadata.create_all(bind=engine)
    AutoAlertConfigBase.metadata.create_all(bind=engine)

def add_response(response_data: dict):
    """Adiciona uma nova resposta ao banco"""
    db = SessionLocal()
    try:
        response = Response(**response_data)
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_responses(user_id: str = None, limit: int = 100):
    """Busca respostas do banco"""
    db = SessionLocal()
    try:
        query = db.query(Response)
        if user_id:
            query = query.filter(Response.user_id == user_id)
        return query.order_by(Response.timestamp.desc()).limit(limit).all()
    finally:
        db.close()

def set_aguardando_resposta(user_id: str):
    """Marca que o usuário está aguardando resposta"""
    # Implementação simplificada - sempre retorna True
    return True

def is_aguardando_resposta(user_id: str):
    """Verifica se o usuário está aguardando resposta"""
    # Implementação simplificada - sempre retorna False
    return False 