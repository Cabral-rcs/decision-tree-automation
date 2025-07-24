from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Lider(Base):
    __tablename__ = 'lideres'
    id = Column(Integer, primary_key=True, index=True)
    nome_lider = Column(String, unique=True, nullable=False)
    chat_id = Column(String, unique=True, nullable=False) 