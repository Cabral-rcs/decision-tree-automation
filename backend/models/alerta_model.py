from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Alerta(Base):
    __tablename__ = 'alertas'
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    problema = Column(Text)
    mensagem_id = Column(Integer, nullable=True)
    previsao = Column(Text, nullable=True)
    previsao_datetime = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default='pendente')  # 'pendente', 'escalada', 'atrasada', 'encerrada'
    status_operacao = Column(String, default='não operando')  # 'operando' ou 'não operando'
    nome_lider = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    respondido_em = Column(DateTime(timezone=True), nullable=True) 