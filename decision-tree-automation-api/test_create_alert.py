#!/usr/bin/env python3
"""
Script para testar a criação de alertas diretamente no banco
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from backend.models.responses_model import SessionLocal
from backend.models.alerta_model import Alerta

def test_create_alert():
    """Testa a criação de um alerta diretamente no banco"""
    
    print("🧪 TESTE DE CRIAÇÃO DE ALERTA")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada")
        return
    
    db = SessionLocal()
    try:
        # Verifica alertas existentes
        alertas_existentes = db.query(Alerta).count()
        print(f"📊 Alertas existentes: {alertas_existentes}")
        
        # Cria um alerta de teste
        novo_alerta = Alerta(
            chat_id='6435800936',
            problema='Teste de alerta via script - Problema de teste',
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo='TEST001',
            unidade='Unidade Teste',
            frente='Frente de Teste',
            equipamento='Equipamento Teste',
            codigo_equipamento='EQ001',
            tipo_operacao='Teste',
            operacao='Operação de Teste',
            nome_operador='Operador Teste',
            data_operacao=datetime.now(),
            tempo_abertura='1h 30min',
            tipo_arvore='Árvore de Teste',
            justificativa=None,
            prazo=None  # Campo que será preenchido pelo Telegram
        )
        
        print("🔄 Criando alerta de teste...")
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        print(f"✅ Alerta criado com sucesso!")
        print(f"   ID: {novo_alerta.id}")
        print(f"   Problema: {novo_alerta.problema}")
        print(f"   Status: {novo_alerta.status}")
        print(f"   Prazo: {novo_alerta.prazo}")
        print(f"   Criado em: {novo_alerta.criado_em}")
        
        # Verifica se foi salvo
        alerta_salvo = db.query(Alerta).filter(Alerta.id == novo_alerta.id).first()
        if alerta_salvo:
            print(f"✅ Alerta confirmado no banco - ID: {alerta_salvo.id}")
        else:
            print("❌ Alerta não foi salvo no banco")
        
        # Conta alertas novamente
        alertas_finais = db.query(Alerta).count()
        print(f"📊 Total de alertas após criação: {alertas_finais}")
        
        # Lista todos os alertas
        todos_alertas = db.query(Alerta).all()
        print("📋 Todos os alertas:")
        for a in todos_alertas:
            print(f"   ID: {a.id}, Problema: {a.problema[:50]}..., Prazo: {a.prazo}, Status: {a.status}")
        
        print("\n" + "=" * 50)
        print("🏁 TESTE CONCLUÍDO")
        print("\n📱 Agora teste responder no Telegram com formato HH:MM")
        print("🔄 O alerta deve ser atualizado com o prazo")
        
    except Exception as e:
        print(f"❌ Erro ao criar alerta: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_create_alert() 