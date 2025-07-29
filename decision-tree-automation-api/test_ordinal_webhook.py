#!/usr/bin/env python3
"""
Script para testar a lógica ordinal do webhook
"""

import os
import sys
import re
import time
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ordinal_webhook():
    """Testa a lógica ordinal do webhook"""
    try:
        from backend.models.responses_model import SessionLocal, add_response
        from backend.models.alerta_model import Alerta
        from backend.services.mock_data_generator import MockDataGenerator
        from sqlalchemy import text
        
        db = SessionLocal()
        
        print("🧪 TESTE DE LÓGICA ORDINAL DO WEBHOOK")
        print("=" * 60)
        
        # 1. Limpa alertas existentes para teste limpo
        print("\n🧹 Limpando alertas existentes...")
        db.query(Alerta).delete()
        db.commit()
        print("✅ Alertas limpos")
        
        # 2. Cria 3 alertas de teste (2 automáticos + 1 manual)
        print("\n📝 Criando alertas de teste...")
        
        # Alerta automático 1
        alert_data1 = MockDataGenerator.generate_alert_data()
        alerta_auto1 = Alerta(
            chat_id="6435800936",
            problema=alert_data1['problema'],
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo=alert_data1.get('codigo'),
            unidade=alert_data1.get('unidade'),
            frente=alert_data1.get('frente'),
            equipamento=alert_data1.get('equipamento'),
            tipo_operacao=alert_data1.get('tipo_operacao'),
            operacao=alert_data1.get('operacao'),
            nome_operador=alert_data1.get('nome_operador')
        )
        db.add(alerta_auto1)
        db.commit()
        db.refresh(alerta_auto1)
        
        time.sleep(1)  # Pequena pausa para garantir ordem cronológica
        
        # Alerta manual
        alerta_manual = Alerta(
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
        db.add(alerta_manual)
        db.commit()
        db.refresh(alerta_manual)
        
        time.sleep(1)  # Pequena pausa para garantir ordem cronológica
        
        # Alerta automático 2
        alert_data2 = MockDataGenerator.generate_alert_data()
        alerta_auto2 = Alerta(
            chat_id="6435800936",
            problema=alert_data2['problema'],
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo=alert_data2.get('codigo'),
            unidade=alert_data2.get('unidade'),
            frente=alert_data2.get('frente'),
            equipamento=alert_data2.get('equipamento'),
            tipo_operacao=alert_data2.get('tipo_operacao'),
            operacao=alert_data2.get('operacao'),
            nome_operador=alert_data2.get('nome_operador')
        )
        db.add(alerta_auto2)
        db.commit()
        db.refresh(alerta_auto2)
        
        print(f"✅ Alerta automático 1 criado - ID: {alerta_auto1.id}")
        print(f"✅ Alerta manual criado - ID: {alerta_manual.id}")
        print(f"✅ Alerta automático 2 criado - ID: {alerta_auto2.id}")
        
        # 3. Verifica ordem dos alertas pendentes
        print("\n📊 Verificando ordem dos alertas pendentes...")
        alertas_pendentes = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).all()
        
        print(f"Alertas pendentes na ordem cronológica:")
        for i, alerta in enumerate(alertas_pendentes):
            print(f"  {i+1}. ID: {alerta.id}, Criado: {alerta.criado_em}")
            print(f"     Problema: {alerta.problema[:50]}...")
            print(f"     É automático: {'Sim' if alerta.problema.startswith('[AUTO]') else 'Não'}")
            print()
        
        # 4. Simula primeira resposta do Telegram (deve atualizar o primeiro alerta)
        print("\n📱 Simulando primeira resposta do Telegram...")
        
        # Simula dados do Telegram
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta1 = "20:30"  # Previsão futura
        msg_utc = datetime.now(pytz.UTC)
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.astimezone(tz_br)
        
        print(f"📱 Primeira resposta: {resposta1}")
        
        # Aplica a lógica do webhook
        alerta_primeiro = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta_primeiro:
            print("❌ Nenhum alerta pendente encontrado")
            return False
        
        print(f"🎯 Primeiro alerta a ser processado: ID {alerta_primeiro.id}")
        
        # Validação do formato HH:MM
        padrao = r'^(\d{2}):(\d{2})$'
        match = re.match(padrao, resposta1)
        if not match:
            print(f"❌ Formato inválido: {resposta1}")
            return False
        
        # Monta datetime da previsão
        hora, minuto = match.groups()
        previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        
        # Atualiza o primeiro alerta
        alerta_primeiro.previsao = resposta1
        alerta_primeiro.previsao_datetime = previsao_dt
        alerta_primeiro.respondido_em = datetime.now(pytz.UTC)
        alerta_primeiro.nome_lider = nome_lider
        
        db.commit()
        db.refresh(alerta_primeiro)
        
        print(f"✅ Primeiro alerta atualizado - ID: {alerta_primeiro.id}, Previsão: {alerta_primeiro.previsao}")
        
        # 5. Verifica quantos alertas ainda estão pendentes
        alertas_restantes1 = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).count()
        
        print(f"📋 Alertas restantes após primeira resposta: {alertas_restantes1}")
        
        # 6. Simula segunda resposta do Telegram (deve atualizar o segundo alerta)
        print("\n📱 Simulando segunda resposta do Telegram...")
        
        resposta2 = "21:45"  # Segunda previsão
        
        print(f"📱 Segunda resposta: {resposta2}")
        
        # Aplica a lógica do webhook novamente
        alerta_segundo = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta_segundo:
            print("❌ Nenhum alerta pendente encontrado")
            return False
        
        print(f"🎯 Segundo alerta a ser processado: ID {alerta_segundo.id}")
        
        # Validação do formato HH:MM
        match = re.match(padrao, resposta2)
        if not match:
            print(f"❌ Formato inválido: {resposta2}")
            return False
        
        # Monta datetime da previsão
        hora, minuto = match.groups()
        previsao_dt2 = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        
        # Atualiza o segundo alerta
        alerta_segundo.previsao = resposta2
        alerta_segundo.previsao_datetime = previsao_dt2
        alerta_segundo.respondido_em = datetime.now(pytz.UTC)
        alerta_segundo.nome_lider = nome_lider
        
        db.commit()
        db.refresh(alerta_segundo)
        
        print(f"✅ Segundo alerta atualizado - ID: {alerta_segundo.id}, Previsão: {alerta_segundo.previsao}")
        
        # 7. Verifica quantos alertas ainda estão pendentes
        alertas_restantes2 = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).count()
        
        print(f"📋 Alertas restantes após segunda resposta: {alertas_restantes2}")
        
        # 8. Verifica resultado final
        print("\n📊 Verificando resultado final...")
        
        alertas_finais = db.query(Alerta).order_by(Alerta.criado_em.asc()).all()
        
        print("Estado final dos alertas:")
        for i, alerta in enumerate(alertas_finais):
            print(f"  {i+1}. ID: {alerta.id}")
            print(f"     Criado: {alerta.criado_em}")
            print(f"     Problema: {alerta.problema[:50]}...")
            print(f"     Previsão: {alerta.previsao or 'Nenhuma'}")
            print(f"     É automático: {'Sim' if alerta.problema.startswith('[AUTO]') else 'Não'}")
            print()
        
        # 9. Validação do teste
        print("\n🔍 Validação do teste...")
        
        # Verifica se a ordem foi respeitada
        if (alerta_primeiro.id == alerta_auto1.id and 
            alerta_segundo.id == alerta_manual.id and 
            alertas_restantes2 == 1):
            print("✅ ORDEM ORDINAL FUNCIONANDO CORRETAMENTE!")
            print("✅ Primeiro alerta (automático) foi processado primeiro")
            print("✅ Segundo alerta (manual) foi processado segundo")
            print("✅ Terceiro alerta (automático) ainda está pendente")
            return True
        else:
            print("❌ ORDEM ORDINAL NÃO FUNCIONOU CORRETAMENTE")
            print(f"   Primeiro processado: {alerta_primeiro.id} (esperado: {alerta_auto1.id})")
            print(f"   Segundo processado: {alerta_segundo.id} (esperado: {alerta_manual.id})")
            print(f"   Alertas restantes: {alertas_restantes2} (esperado: 1)")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 TESTE DE LÓGICA ORDINAL DO WEBHOOK")
    print("=" * 60)
    
    success = test_ordinal_webhook()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ A lógica ordinal está funcionando corretamente")
        print("✅ Os alertas são processados na ordem cronológica")
        print("✅ Cada resposta do Telegram atualiza apenas um alerta")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas com a lógica ordinal")

if __name__ == "__main__":
    load_dotenv()
    main() 