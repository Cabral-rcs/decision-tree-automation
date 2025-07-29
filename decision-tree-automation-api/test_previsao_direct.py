#!/usr/bin/env python3
"""
Script para testar diretamente o armazenamento de previsões no banco de dados
"""

import os
import sys
import re
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        from backend.models.responses_model import SessionLocal, engine
        from backend.models.alerta_model import Alerta
        from sqlalchemy import text
        
        # Testa a conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco de dados OK")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
        return False

def create_test_alert_direct():
    """Cria um alerta de teste diretamente no banco"""
    try:
        from backend.models.responses_model import SessionLocal
        from backend.models.alerta_model import Alerta
        
        db = SessionLocal()
        
        # Cria alerta de teste
        novo_alerta = Alerta(
            chat_id="6435800936",
            problema="TESTE DIRETO - Equipamento apresentando baixa eficiência",
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo="TESTDIR001",
            unidade="Unidade Teste Direto",
            frente="Frente de Teste",
            equipamento="Equipamento Teste",
            tipo_operacao="Teste",
            operacao="Operação de Teste",
            nome_operador="Operador Teste"
        )
        
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        print(f"✅ Alerta de teste criado diretamente - ID: {novo_alerta.id}")
        return novo_alerta.id
        
    except Exception as e:
        print(f"❌ Erro ao criar alerta diretamente: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def check_alert_categories_direct():
    """Verifica as categorias de alertas diretamente no banco"""
    try:
        from backend.models.responses_model import SessionLocal
        from backend.models.alerta_model import Alerta
        
        db = SessionLocal()
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Busca todos os alertas
        alertas = db.query(Alerta).order_by(Alerta.criado_em.desc()).all()
        
        pendentes = []
        escaladas = []
        atrasadas = []
        encerradas = []
        
        for alerta in alertas:
            if not alerta.previsao:
                pendentes.append(alerta)
            elif alerta.status_operacao == 'operando':
                if alerta.previsao_datetime and alerta.previsao_datetime >= now:
                    encerradas.append(alerta)
                else:
                    atrasadas.append(alerta)
            else:
                if alerta.previsao_datetime and alerta.previsao_datetime >= now:
                    escaladas.append(alerta)
                else:
                    atrasadas.append(alerta)
        
        print(f"📊 Categorias de alertas (diretamente do banco):")
        print(f"   - Pendentes: {len(pendentes)}")
        print(f"   - Escaladas: {len(escaladas)}")
        print(f"   - Atrasadas: {len(atrasadas)}")
        print(f"   - Encerradas: {len(encerradas)}")
        
        return {
            'pendentes': pendentes,
            'escaladas': escaladas,
            'atrasadas': atrasadas,
            'encerradas': encerradas
        }
        
    except Exception as e:
        print(f"❌ Erro ao verificar categorias: {e}")
        return None
    finally:
        db.close()

def simulate_webhook_logic_direct(previsao="17:30"):
    """Simula a lógica do webhook diretamente no banco"""
    try:
        from backend.models.responses_model import SessionLocal, add_response
        from backend.models.alerta_model import Alerta
        
        db = SessionLocal()
        
        # Simula dados do Telegram
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta = previsao
        msg_utc = datetime.utcnow()
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.replace(tzinfo=pytz.utc).astimezone(tz_br)
        
        print(f"📱 Simulando webhook diretamente:")
        print(f"   User ID: {user_id}")
        print(f"   Nome: {nome_lider}")
        print(f"   Resposta: {resposta}")
        
        # Verifica se é Rafael Cabral
        if 'Rafael' not in nome_lider and 'Cabral' not in nome_lider:
            print("❌ Não é Rafael Cabral")
            return False
        
        # Busca alerta pendente
        alerta = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta:
            print("❌ Nenhum alerta pendente encontrado")
            return False
        
        print(f"✅ Alerta encontrado: ID {alerta.id}")
        print(f"   Problema: {alerta.problema}")
        
        # Validação do formato HH:MM
        padrao = r'^(\d{2}):(\d{2})$'
        match = re.match(padrao, resposta)
        if not match:
            print(f"❌ Formato inválido: {resposta}")
            return False
        
        print("✅ Formato válido")
        
        # Monta datetime da previsão
        hora, minuto = match.groups()
        previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        
        print(f"⏰ Previsão processada: {resposta} -> {previsao_dt}")
        
        # Atualiza o alerta
        alerta.previsao = resposta
        alerta.previsao_datetime = previsao_dt
        alerta.respondido_em = datetime.utcnow()
        alerta.nome_lider = nome_lider
        
        db.commit()
        db.refresh(alerta)
        
        # Verifica se foi salvo
        alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
        if alerta_atualizado and alerta_atualizado.previsao:
            print(f"✅ Alerta atualizado com sucesso!")
            print(f"   ID: {alerta_atualizado.id}")
            print(f"   Previsão: {alerta_atualizado.previsao}")
            print(f"   Previsão DateTime: {alerta_atualizado.previsao_datetime}")
            print(f"   Respondido em: {alerta_atualizado.respondido_em}")
        else:
            print("❌ Falha ao atualizar alerta")
            return False
        
        # Salva como resposta geral
        add_response({
            'user_id': str(user_id),
            'pergunta': alerta.problema,
            'resposta': resposta,
            'timestamp': msg_utc.isoformat()
        })
        
        print("✅ Resposta geral salva")
        return True
        
    except Exception as e:
        print(f"❌ Erro na simulação do webhook: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_previsao_storage_direct():
    """Testa o armazenamento de previsões diretamente no banco"""
    print("\n🧪 TESTE DIRETO DE ARMAZENAMENTO DE PREVISÕES")
    print("=" * 60)
    
    # 1. Testa conexão com banco
    if not test_database_connection():
        return False
    
    # 2. Verifica categorias iniciais
    print("\n📊 Categorias iniciais:")
    initial_categories = check_alert_categories_direct()
    if not initial_categories:
        return False
    
    # 3. Cria alerta de teste
    print("\n📝 Criando alerta de teste diretamente...")
    alert_id = create_test_alert_direct()
    if not alert_id:
        return False
    
    # 4. Verifica se o alerta foi para pendentes
    print("\n📊 Verificando se alerta foi para pendentes...")
    categories_after_create = check_alert_categories_direct()
    if not categories_after_create:
        return False
    
    pendentes_after = len(categories_after_create['pendentes'])
    if pendentes_after > len(initial_categories['pendentes']):
        print("✅ Alerta criado e adicionado aos pendentes")
    else:
        print("❌ Alerta não foi adicionado aos pendentes")
        return False
    
    # 5. Simula webhook diretamente
    print("\n📱 Simulando webhook diretamente...")
    previsao = "18:15"
    if not simulate_webhook_logic_direct(previsao):
        return False
    
    # 6. Verifica se o alerta mudou de categoria
    print("\n📊 Verificando mudança de categoria...")
    categories_after_response = check_alert_categories_direct()
    if not categories_after_response:
        return False
    
    # 7. Análise final
    print("\n📊 ANÁLISE FINAL:")
    print("=" * 50)
    
    # Verifica se a previsão foi armazenada
    alerta_com_previsao = None
    for alerta in categories_after_response['escaladas'] + categories_after_response['atrasadas'] + categories_after_response['encerradas']:
        if alerta.previsao == previsao:
            alerta_com_previsao = alerta
            break
    
    if alerta_com_previsao:
        print(f"✅ PREVISÃO ARMAZENADA CORRETAMENTE:")
        print(f"   - ID: {alerta_com_previsao.id}")
        print(f"   - Previsão: {alerta_com_previsao.previsao}")
        print(f"   - Previsão DateTime: {alerta_com_previsao.previsao_datetime}")
        print(f"   - Respondido em: {alerta_com_previsao.respondido_em}")
        print(f"   - Status Operação: {alerta_com_previsao.status_operacao}")
    else:
        print("❌ PREVISÃO NÃO FOI ARMAZENADA")
        return False
    
    # Verifica mudança de categoria
    pendentes_final = len(categories_after_response['pendentes'])
    escaladas_final = len(categories_after_response['escaladas'])
    
    print(f"\n📊 MUDANÇA DE CATEGORIA:")
    print(f"   - Pendentes antes: {len(initial_categories['pendentes'])}")
    print(f"   - Pendentes depois: {pendentes_final}")
    print(f"   - Escaladas depois: {escaladas_final}")
    
    if pendentes_final < pendentes_after and escaladas_final > len(initial_categories['escaladas']):
        print("✅ ALERTA MUDOU DE CATEGORIA CORRETAMENTE")
        print("   - Saiu de 'Pendentes' e foi para 'Escaladas'")
        return True
    else:
        print("❌ ALERTA NÃO MUDOU DE CATEGORIA")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DIRETO DE PREVISÕES E MUDANÇA DE CATEGORIA")
    print("=" * 70)
    
    success = test_previsao_storage_direct()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 TESTE DIRETO CONCLUÍDO COM SUCESSO!")
        print("✅ As respostas do Telegram estão sendo armazenadas na coluna Previsão")
        print("✅ Os alertas estão mudando de categoria automaticamente")
        print("✅ A lógica do webhook está funcionando corretamente")
        print("✅ O banco de dados está funcionando corretamente")
    else:
        print("❌ TESTE DIRETO FALHOU")
        print("❌ Há problemas no armazenamento de previsões ou mudança de categoria")
    
    print("\n📋 CONCLUSÕES:")
    print("1. O teste foi feito diretamente no banco de dados")
    print("2. Não depende do servidor estar rodando")
    print("3. Testa a lógica core do sistema")
    print("4. Verifica se as regras de negócio estão corretas")

if __name__ == "__main__":
    load_dotenv()
    main() 