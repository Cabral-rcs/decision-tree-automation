#!/usr/bin/env python3
"""
Script de migração do banco de dados
Atualiza a estrutura das tabelas e garante consistência
"""

import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.responses_model import init_db, engine
from backend.models.alerta_model import Base as AlertaBase
from backend.models.auto_alert_config_model import Base as AutoAlertConfigBase
from sqlalchemy import text

def migrate_database():
    """Executa a migração do banco de dados"""
    print("🔄 Iniciando migração do banco de dados...")
    
    try:
        # Inicializa o banco (cria tabelas se não existirem)
        init_db()
        print("✅ Tabelas criadas/verificadas com sucesso")
        
        # Verifica se há dados inconsistentes
        with engine.connect() as conn:
            # Verifica se há alertas com prazo mas sem previsão
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM alertas 
                WHERE prazo IS NOT NULL AND previsao IS NULL
            """))
            inconsistent_count = result.fetchone()[0]
            
            if inconsistent_count > 0:
                print(f"⚠️  Encontrados {inconsistent_count} alertas com prazo mas sem previsão")
                print("🔄 Migrando dados inconsistentes...")
                
                # Copia o valor do prazo para previsão onde necessário
                conn.execute(text("""
                    UPDATE alertas 
                    SET previsao = prazo::text, 
                        previsao_datetime = prazo 
                    WHERE prazo IS NOT NULL AND previsao IS NULL
                """))
                conn.commit()
                print("✅ Dados migrados com sucesso")
            
            # Verifica se há alertas com previsão mas sem prazo (normal após migração)
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM alertas 
                WHERE previsao IS NOT NULL AND prazo IS NULL
            """))
            migrated_count = result.fetchone()[0]
            
            if migrated_count > 0:
                print(f"✅ {migrated_count} alertas com previsão (migração bem-sucedida)")
        
        print("🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

if __name__ == "__main__":
    load_dotenv()
    
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL não configurada!")
        sys.exit(1)
    
    success = migrate_database()
    if not success:
        sys.exit(1) 