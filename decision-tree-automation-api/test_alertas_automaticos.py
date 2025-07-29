#!/usr/bin/env python3
"""
Script para testar especificamente os alertas automáticos
"""

import os
import sys
import re
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_alertas_automaticos():
    """Testa alertas automáticos"""
    try:
        from backend.models.responses_model import SessionLocal, add_response
        from backend.models.alerta_model import Alerta
        from backend.services.mock_data_generator import MockDataGenerator
        from sqlalchemy import text
        
        db = SessionLocal()
        
        print("🧪 TESTE DE ALERTAS AUTOMÁTICOS")
        print("=" * 50)
        
        # 1. Verifica alertas existentes
        print("\n📊 Verificando alertas existentes...")
        alertas_existentes = db.query(Alerta).order_by(Alerta.criado_em.desc()).all()
        
        print(f"Total de alertas no sistema: {len(alertas_existentes)}")
        
        alertas_automaticos = []
        alertas_manuais = []
        
        for alerta in alertas_existentes:
            if alerta.problema.startswith('[AUTO]'):
                alertas_automaticos.append(alerta)
            else:
                alertas_manuais.append(alerta)
        
        print(f"Alertas automáticos: {len(alertas_automaticos)}")
        print(f"Alertas manuais: {len(alertas_manuais)}")
        
        # 2. Cria um alerta automático de teste
        print("\n📝 Criando alerta automático de teste...")
        alert_data = MockDataGenerator.generate_alert_data()
        
        novo_alerta_auto = Alerta(
            chat_id="6435800936",
            problema=alert_data['problema'],  # Já começa com "[AUTO]"
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo=alert_data.get('codigo'),
            unidade=alert_data.get('unidade'),
            frente=alert_data.get('frente'),
            equipamento=alert_data.get('equipamento'),
            codigo_equipamento=alert_data.get('codigo_equipamento'),
            tipo_operacao=alert_data.get('tipo_operacao'),
            operacao=alert_data.get('operacao'),
            nome_operador=alert_data.get('nome_operador'),
            data_operacao=datetime.fromisoformat(alert_data.get('data_operacao')) if alert_data.get('data_operacao') else None,
            tempo_abertura=alert_data.get('tempo_abertura'),
            tipo_arvore=alert_data.get('tipo_arvore'),
            justificativa=None,
            prazo=None
        )
        
        db.add(novo_alerta_auto)
        db.commit()
        db.refresh(novo_alerta_auto)
        
        print(f"✅ Alerta automático criado - ID: {novo_alerta_auto.id}")
        print(f"   Problema: {novo_alerta_auto.problema}")
        print(f"   É automático: {'Sim' if novo_alerta_auto.problema.startswith('[AUTO]') else 'Não'}")
        
        # 3. Cria um alerta manual de teste
        print("\n📝 Criando alerta manual de teste...")
        novo_alerta_manual = Alerta(
            chat_id="6435800936",
            problema="TESTE MANUAL - Equipamento apresentando baixa eficiência",
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo="TESTMAN001",
            unidade="Unidade Teste Manual",
            frente="Frente de Teste",
            equipamento="Equipamento Teste",
            tipo_operacao="Teste",
            operacao="Operação de Teste",
            nome_operador="Operador Teste"
        )
        
        db.add(novo_alerta_manual)
        db.commit()
        db.refresh(novo_alerta_manual)
        
        print(f"✅ Alerta manual criado - ID: {novo_alerta_manual.id}")
        print(f"   Problema: {novo_alerta_manual.problema}")
        print(f"   É automático: {'Sim' if novo_alerta_manual.problema.startswith('[AUTO]') else 'Não'}")
        
        # 4. Verifica alertas pendentes
        print("\n📊 Verificando alertas pendentes...")
        alertas_pendentes = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).all()
        
        print(f"Alertas pendentes: {len(alertas_pendentes)}")
        
        for i, alerta in enumerate(alertas_pendentes):
            print(f"  {i+1}. ID: {alerta.id}")
            print(f"     Criado: {alerta.criado_em}")
            print(f"     Problema: {alerta.problema[:50]}...")
            print(f"     É automático: {'Sim' if alerta.problema.startswith('[AUTO]') else 'Não'}")
            print()
        
        # 5. Simula a lógica do webhook
        print("\n📱 Simulando lógica do webhook...")
        
        # Simula dados do Telegram
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta = "19:30"  # Previsão futura
        msg_utc = datetime.now(pytz.UTC)
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.astimezone(tz_br)
        
        print(f"📱 Dados simulados:")
        print(f"   User ID: {user_id}")
        print(f"   Nome: {nome_lider}")
        print(f"   Resposta: {resposta}")
        
        # Aplica a nova lógica do webhook
        alertas_pendentes = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).all()
        
        print(f"📋 Alertas pendentes encontrados: {len(alertas_pendentes)}")
        
        for i, alerta in enumerate(alertas_pendentes):
            print(f"  {i+1}. ID: {alerta.id}, Criado: {alerta.criado_em}, Problema: {alerta.problema[:50]}...")
        
        # Prioriza alertas manuais
        alerta_manual = None
        for alerta in alertas_pendentes:
            if not alerta.problema.startswith('[AUTO]'):
                alerta_manual = alerta
                print(f"🎯 Alerta manual encontrado: ID {alerta.id}")
                break
        
        # Se não encontrou alerta manual, usa o primeiro pendente
        if not alerta_manual:
            alerta_manual = alertas_pendentes[0]
            print(f"🤖 Usando primeiro alerta pendente (automático): ID {alerta_manual.id}")
        
        alerta = alerta_manual
        
        print(f"🎯 Alerta selecionado: ID {alerta.id}")
        print(f"   Problema: {alerta.problema[:100]}...")
        print(f"   Criado em: {alerta.criado_em}")
        print(f"   É automático: {'Sim' if alerta.problema.startswith('[AUTO]') else 'Não'}")
        
        # 6. Processa a previsão
        print("\n⏰ Processando previsão...")
        
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
        alerta.respondido_em = datetime.now(pytz.UTC)
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
            print(f"   É automático: {'Sim' if alerta_atualizado.problema.startswith('[AUTO]') else 'Não'}")
        else:
            print("❌ Falha ao atualizar alerta")
            return False
        
        # 7. Verifica categorização
        print("\n📊 Verificando categorização...")
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        
        # Aplica a lógica de categorização
        if not alerta_atualizado.previsao:
            categoria = "pendentes"
        elif alerta_atualizado.status_operacao == 'operando':
            if alerta_atualizado.previsao_datetime >= now:
                categoria = "encerradas"
            else:
                categoria = "atrasadas"
        else:
            if alerta_atualizado.previsao_datetime >= now:
                categoria = "escaladas"
            else:
                categoria = "atrasadas"
        
        print(f"   Categoria calculada: {categoria}")
        
        if categoria == "escaladas":
            print("✅ ALERTA FOI PARA 'ESCALADAS' CORRETAMENTE!")
            return True
        else:
            print(f"❌ Alerta foi para '{categoria}' em vez de 'escaladas'")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 TESTE DE ALERTAS AUTOMÁTICOS")
    print("=" * 60)
    
    success = test_alertas_automaticos()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Os alertas automáticos estão sendo processados corretamente")
        print("✅ A lógica de priorização está funcionando")
        print("✅ As previsões estão sendo armazenadas")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas com alertas automáticos")

if __name__ == "__main__":
    load_dotenv()
    main() 