from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from backend.config import DATABASE_URL

Base = declarative_base()

class Alerta(Base):
    __tablename__ = 'alertas'
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    problema = Column(Text)
    mensagem_id = Column(Integer, nullable=True)
    previsao = Column(Text, nullable=True)  # Null inicialmente, preenchido via Telegram
    previsao_datetime = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='pendente')  # 'pendente', 'escalada', 'atrasada', 'encerrada'
    status_operacao = Column(String, default='não operando')  # 'operando' ou 'não operando'
    nome_lider = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    respondido_em = Column(DateTime(timezone=True), nullable=True)
    horario_operando = Column(DateTime(timezone=True), nullable=True)

# Função para inicializar o banco de dados (recriado a cada deploy)
def init_database():
    """Inicializa o banco de dados - recria todas as tabelas"""
    load_dotenv()
    
    # Cria o engine com a configuração centralizada
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Recria todas as tabelas (dados zerados)
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Banco de dados inicializado (dados zerados)")
    return engine

# Função utilitária para forçar o drop e recriação da tabela alertas
# Use apenas em ambiente de desenvolvimento/teste!
def force_recreate_alerta_table():
    load_dotenv()
    engine = create_engine(DATABASE_URL)
    Alerta.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine) 