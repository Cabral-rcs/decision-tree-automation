#!/usr/bin/env python3
"""
Script para migrar a base de dados e adicionar as novas colunas ao modelo de alerta
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from backend.models.alerta_model import Alerta, Base
from backend.models.auto_alert_config_model import AutoAlertConfig
from backend.models.lider_model import Lider
from backend.models.responses_model import Resposta, EstadoUsuario

def migrate_database():
    """Migra a base de dados para incluir as novas colunas"""
    
    print("=== Migração da Base de Dados ===\n")
    
    # Carrega variáveis de ambiente
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no arquivo .env")
        return False
    
    try:
        # Cria engine
        engine = create_engine(DATABASE_URL)
        
        print("1. Verificando conexão com banco...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✅ Conexão OK")
        
        print("2. Verificando tabelas existentes...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            existing_tables = [row[0] for row in result]
            print(f"   Tabelas encontradas: {existing_tables}")
        
        print("3. Verificando colunas da tabela alertas...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'alertas'
            """))
            existing_columns = [row[0] for row in result]
            print(f"   Colunas existentes: {existing_columns}")
        
        # Novas colunas a serem adicionadas
        new_columns = [
            'codigo', 'unidade', 'frente', 'equipamento', 'codigo_equipamento',
            'tipo_operacao', 'operacao', 'nome_operador', 'data_operacao',
            'tempo_abertura', 'tipo_arvore', 'justificativa', 'prazo'
        ]
        
        print("4. Adicionando novas colunas...")
        with engine.connect() as conn:
            for column in new_columns:
                if column not in existing_columns:
                    try:
                        if column in ['data_operacao', 'prazo']:
                            # Colunas de data/hora
                            conn.execute(text(f"ALTER TABLE alertas ADD COLUMN {column} TIMESTAMP WITH TIME ZONE"))
                        elif column in ['justificativa']:
                            # Coluna de texto longo
                            conn.execute(text(f"ALTER TABLE alertas ADD COLUMN {column} TEXT"))
                        else:
                            # Colunas de string
                            conn.execute(text(f"ALTER TABLE alertas ADD COLUMN {column} VARCHAR"))
                        print(f"   ✅ Coluna {column} adicionada")
                    except Exception as e:
                        print(f"   ⚠️  Coluna {column} já existe ou erro: {e}")
            
            conn.commit()
        
        print("5. Verificando tabela auto_alert_config...")
        if 'auto_alert_config' not in existing_tables:
            print("   Criando tabela auto_alert_config...")
            Base.metadata.create_all(bind=engine, tables=[AutoAlertConfig.__table__])
            print("   ✅ Tabela auto_alert_config criada")
        else:
            print("   ✅ Tabela auto_alert_config já existe")
        
        print("6. Verificando tabela lideres...")
        if 'lideres' not in existing_tables:
            print("   Criando tabela lideres...")
            Base.metadata.create_all(bind=engine, tables=[Lider.__table__])
            print("   ✅ Tabela lideres criada")
        else:
            print("   ✅ Tabela lideres já existe")
        
        print("7. Verificando tabelas de respostas...")
        if 'respostas' not in existing_tables:
            print("   Criando tabelas de respostas...")
            Base.metadata.create_all(bind=engine, tables=[Resposta.__table__, EstadoUsuario.__table__])
            print("   ✅ Tabelas de respostas criadas")
        else:
            print("   ✅ Tabelas de respostas já existem")
        
        print("\n=== Migração Concluída com Sucesso! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        return False

if __name__ == "__main__":
    migrate_database() 