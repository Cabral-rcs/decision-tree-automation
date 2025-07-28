#!/usr/bin/env python3
"""
Script para debug das respostas do Telegram
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from backend.models.responses_model import SessionLocal, Resposta
from backend.models.alerta_model import Alerta

def debug_responses():
    """Debug das respostas do Telegram"""
    
    print("🔍 DEBUG DAS RESPOSTAS DO TELEGRAM")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada")
        return
    
    try:
        # Cria engine
        engine = create_engine(DATABASE_URL)
        
        print("1. Verificando tabela de respostas...")
        with engine.connect() as conn:
            # Verifica se a tabela existe
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'respostas'
            """))
            if result.fetchone():
                print("   ✅ Tabela 'respostas' existe")
            else:
                print("   ❌ Tabela 'respostas' NÃO existe")
                return
            
            # Conta respostas
            result = conn.execute(text("SELECT COUNT(*) FROM respostas"))
            count = result.fetchone()[0]
            print(f"   📊 Total de respostas: {count}")
            
            # Lista as últimas 5 respostas
            result = conn.execute(text("""
                SELECT id, user_id, pergunta, resposta, timestamp 
                FROM respostas 
                ORDER BY timestamp DESC 
                LIMIT 5
            """))
            
            print("   📋 Últimas 5 respostas:")
            for row in result:
                print(f"      ID: {row[0]}, User: {row[1]}, Resposta: {row[3]}, Timestamp: {row[4]}")
        
        print("\n2. Verificando alertas...")
        with engine.connect() as conn:
            # Conta alertas
            result = conn.execute(text("SELECT COUNT(*) FROM alertas"))
            count = result.fetchone()[0]
            print(f"   📊 Total de alertas: {count}")
            
            # Alertas com prazo
            result = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE prazo IS NOT NULL"))
            count_com_prazo = result.fetchone()[0]
            print(f"   📊 Alertas com prazo: {count_com_prazo}")
            
            # Alertas sem prazo
            result = conn.execute(text("SELECT COUNT(*) FROM alertas WHERE prazo IS NULL"))
            count_sem_prazo = result.fetchone()[0]
            print(f"   📊 Alertas sem prazo: {count_sem_prazo}")
            
            # Últimos 5 alertas
            result = conn.execute(text("""
                SELECT id, problema, prazo, respondido_em, nome_lider, status_operacao
                FROM alertas 
                ORDER BY criado_em DESC 
                LIMIT 5
            """))
            
            print("   📋 Últimos 5 alertas:")
            for row in result:
                print(f"      ID: {row[0]}, Problema: {row[1][:50]}..., Prazo: {row[2]}, Respondido: {row[3]}, Líder: {row[4]}, Status: {row[5]}")
        
        print("\n3. Verificando via SQLAlchemy...")
        db = SessionLocal()
        try:
            # Respostas via SQLAlchemy
            respostas = db.query(Resposta).order_by(Resposta.timestamp.desc()).limit(5).all()
            print(f"   📊 Respostas via SQLAlchemy: {len(respostas)}")
            for r in respostas:
                print(f"      ID: {r.id}, User: {r.user_id}, Resposta: {r.resposta}, Timestamp: {r.timestamp}")
            
            # Alertas via SQLAlchemy
            alertas = db.query(Alerta).order_by(Alerta.criado_em.desc()).limit(5).all()
            print(f"   📊 Alertas via SQLAlchemy: {len(alertas)}")
            for a in alertas:
                print(f"      ID: {a.id}, Problema: {a.problema[:50]}..., Prazo: {a.prazo}, Respondido: {a.respondido_em}, Líder: {a.nome_lider}")
                
        finally:
            db.close()
        
        print("\n" + "=" * 50)
        print("🏁 DEBUG CONCLUÍDO")
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

if __name__ == "__main__":
    debug_responses() 