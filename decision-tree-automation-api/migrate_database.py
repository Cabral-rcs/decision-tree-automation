#!/usr/bin/env python3
"""
Script de migração do banco de dados
Agora apenas inicializa o banco em memória (dados zerados a cada deploy)
"""

import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import DATABASE_URL
from backend.models.responses_model import init_db
from backend.models.alerta_model import Base as AlertaBase
from backend.models.auto_alert_config_model import Base as AutoAlertConfigBase
from sqlalchemy import create_engine

def migrate_database():
    """Inicializa o banco de dados (dados zerados a cada deploy)"""
    print("🔄 Iniciando inicialização do banco de dados...")
    
    try:
        # Cria o engine
        engine = create_engine(DATABASE_URL)
        
        # Recria todas as tabelas (dados zerados)
        print("🗑️  Removendo tabelas existentes...")
        AlertaBase.metadata.drop_all(bind=engine, checkfirst=True)
        AutoAlertConfigBase.metadata.drop_all(bind=engine, checkfirst=True)
        
        print("📋 Criando novas tabelas...")
        AlertaBase.metadata.create_all(bind=engine)  # Cria com novos campos
        AutoAlertConfigBase.metadata.create_all(bind=engine)
        init_db()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("ℹ️  Dados zerados a cada deploy (banco em memória)")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    success = migrate_database()
    if not success:
        sys.exit(1) 