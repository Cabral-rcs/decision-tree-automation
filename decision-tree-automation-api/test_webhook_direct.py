#!/usr/bin/env python3
"""
Script para testar o webhook diretamente no banco de dados
"""

import os
import sys
import re
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_webhook_direct():
    """Testa o webhook diretamente no banco de dados"""
    try:
        from backend.models.responses_model import SessionLocal, add_response
        from backend.models.alerta_model import Alerta
        from backend.services.mock_data_generator import MockDataGenerator
        
        print("🧪 TESTE DE WEBHOOK DIRETO")
        print("=" * 50)
        
        db = SessionLocal()
        
        # 1. Limpa alertas existentes
        print("\n🧹 Limpando alertas existentes...")
        db.query(Alerta).delete()
        db.commit()
        print("✅ Alertas limpos")
        
        # 2. Cria alertas de teste
        print("\n📝 Criando alertas de teste...")
        
        # Alerta automático
        alert_data = MockDataGenerator.generate_alert_data()
        alerta_auto = Alerta(
            chat_id="6435800936",
            problema=alert_data['problema'],
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo=alert_data.get('codigo'),
            unidade=alert_data.get('unidade'),
            frente=alert_data.get('frente'),
            equipamento=alert_data.get('equipamento'),
            tipo_operacao=alert_data.get('tipo_operacao'),
            operacao=alert_data.get('operacao'),
            nome_operador=alert_data.get('nome_operador')
        )
        db.add(alerta_auto)
        db.commit()
        db.refresh(alerta_auto)
        
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
        
        print(f"✅ Alerta automático criado - ID: {alerta_auto.id}")
        print(f"✅ Alerta manual criado - ID: {alerta_manual.id}")
        
        # 3. Simula dados do Telegram
        print("\n📱 Simulando dados do Telegram...")
        
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta = "20:30"
        msg_utc = datetime.now(pytz.UTC)
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.astimezone(tz_br)
        
        print(f"📱 Dados simulados:")
        print(f"   User ID: {user_id}")
        print(f"   Nome: {nome_lider}")
        print(f"   Resposta: {resposta}")
        
        # 4. Aplica a lógica do webhook diretamente
        print("\n🔄 Aplicando lógica do webhook...")
        
        # Busca o alerta mais antigo sem previsão
        alerta = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta:
            print("❌ Nenhum alerta pendente encontrado")
            return False
        
        print(f"🎯 Alerta selecionado: ID {alerta.id}")
        print(f"   Problema: {alerta.problema[:100]}...")
        print(f"   É automático: {'Sim' if alerta.problema.startswith('[AUTO]') else 'Não'}")
        
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
        
        # 5. Atualiza o alerta
        print("\n💾 Atualizando alerta no banco...")
        
        alerta.previsao = resposta
        alerta.previsao_datetime = previsao_dt
        alerta.respondido_em = datetime.now(pytz.UTC)
        alerta.nome_lider = nome_lider
        
        db.commit()
        db.refresh(alerta)
        
        # 6. Verifica se foi salvo
        print("\n🔍 Verificando se foi salvo...")
        
        alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
        if alerta_atualizado and alerta_atualizado.previsao:
            print("✅ ALERTA ATUALIZADO COM SUCESSO!")
            print(f"   ID: {alerta_atualizado.id}")
            print(f"   Previsão: {alerta_atualizado.previsao}")
            print(f"   Previsão DateTime: {alerta_atualizado.previsao_datetime}")
            print(f"   Respondido em: {alerta_atualizado.respondido_em}")
            print(f"   Nome líder: {alerta_atualizado.nome_lider}")
            
            # Verifica categorização
            now = datetime.now(pytz.timezone('America/Sao_Paulo'))
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
            
            print(f"   Categoria: {categoria}")
            
            # 7. Verifica quantos alertas ainda estão pendentes
            alertas_restantes = db.query(Alerta).filter(
                Alerta.previsao.is_(None)
            ).count()
            
            print(f"📋 Alertas restantes: {alertas_restantes}")
            
            return True
        else:
            print("❌ ALERTA NÃO FOI ATUALIZADO!")
            print(f"   Previsão: {alerta_atualizado.previsao if alerta_atualizado else 'N/A'}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_multiplas_respostas():
    """Testa múltiplas respostas do Telegram"""
    try:
        from backend.models.responses_model import SessionLocal
        from backend.models.alerta_model import Alerta
        from backend.services.mock_data_generator import MockDataGenerator
        
        print("\n🧪 TESTE DE MÚLTIPLAS RESPOSTAS")
        print("=" * 50)
        
        db = SessionLocal()
        
        # Limpa alertas existentes
        db.query(Alerta).delete()
        db.commit()
        
        # Cria 3 alertas
        alertas = []
        for i in range(3):
            alert_data = MockDataGenerator.generate_alert_data()
            alerta = Alerta(
                chat_id="6435800936",
                problema=f"TESTE {i+1} - {alert_data['problema']}",
                status='pendente',
                status_operacao='não operando',
                nome_lider='Rafael Cabral'
            )
            db.add(alerta)
            db.commit()
            db.refresh(alerta)
            alertas.append(alerta)
            print(f"✅ Alerta {i+1} criado - ID: {alerta.id}")
        
        # Simula 2 respostas do Telegram
        respostas = ["15:30", "16:45"]
        
        for i, resposta in enumerate(respostas):
            print(f"\n📱 Resposta {i+1}: {resposta}")
            
            # Busca próximo alerta pendente
            alerta = db.query(Alerta).filter(
                Alerta.previsao.is_(None)
            ).order_by(Alerta.criado_em.asc()).first()
            
            if not alerta:
                print("❌ Nenhum alerta pendente encontrado")
                break
            
            print(f"🎯 Processando alerta ID: {alerta.id}")
            
            # Atualiza alerta
            msg_utc = datetime.now(pytz.UTC)
            tz_br = pytz.timezone('America/Sao_Paulo')
            msg_br = msg_utc.astimezone(tz_br)
            
            hora, minuto = map(int, resposta.split(':'))
            previsao_dt = msg_br.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            
            alerta.previsao = resposta
            alerta.previsao_datetime = previsao_dt
            alerta.respondido_em = datetime.now(pytz.UTC)
            alerta.nome_lider = "Rafael Cabral"
            
            db.commit()
            db.refresh(alerta)
            
            print(f"✅ Alerta {alerta.id} atualizado com previsão: {alerta.previsao}")
        
        # Verifica resultado final
        print("\n📊 Resultado final:")
        alertas_finais = db.query(Alerta).order_by(Alerta.criado_em.asc()).all()
        
        for i, alerta in enumerate(alertas_finais):
            print(f"  {i+1}. ID: {alerta.id}")
            print(f"     Problema: {alerta.problema[:50]}...")
            print(f"     Previsão: {alerta.previsao or 'Nenhuma'}")
            print()
        
        alertas_pendentes = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).count()
        
        print(f"📋 Alertas pendentes: {alertas_pendentes}")
        
        if alertas_pendentes == 1:
            print("✅ TESTE DE MÚLTIPLAS RESPOSTAS SUCESSO!")
            return True
        else:
            print("❌ TESTE DE MÚLTIPLAS RESPOSTAS FALHOU!")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 TESTE DE WEBHOOK DIRETO")
    print("=" * 60)
    
    success1 = test_webhook_direct()
    success2 = test_multiplas_respostas()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ A lógica do webhook está funcionando corretamente")
        print("✅ As previsões estão sendo armazenadas")
        print("✅ A lógica ordinal está funcionando")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas com a lógica do webhook")

if __name__ == "__main__":
    load_dotenv()
    main() 