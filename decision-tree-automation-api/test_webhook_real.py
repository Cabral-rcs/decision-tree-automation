#!/usr/bin/env python3
"""
Script para testar o webhook com dados reais do Telegram
"""

import os
import sys
import json
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_webhook_real():
    """Testa o webhook com dados reais do Telegram"""
    db = None
    try:
        from backend.models.responses_model import SessionLocal
        from backend.models.alerta_model import Alerta
        from backend.services.mock_data_generator import MockDataGenerator
        
        print("🧪 TESTE DE WEBHOOK REAL")
        print("=" * 50)
        
        # 1. Verifica se o backend está rodando
        print("\n🔍 Verificando se o backend está rodando...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend está rodando")
            else:
                print("❌ Backend não está respondendo corretamente")
                return False
        except requests.exceptions.RequestException:
            print("❌ Backend não está rodando")
            print("💡 Execute: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
            return False
        
        # 2. Cria um alerta de teste
        print("\n📝 Criando alerta de teste...")
        db = SessionLocal()
        
        # Limpa alertas existentes
        db.query(Alerta).delete()
        db.commit()
        
        # Cria alerta de teste
        alert_data = MockDataGenerator.generate_alert_data()
        novo_alerta = Alerta(
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
        
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        print(f"✅ Alerta criado - ID: {novo_alerta.id}")
        print(f"   Problema: {novo_alerta.problema[:100]}...")
        
        # 3. Verifica se o alerta está pendente
        alertas_pendentes = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).count()
        
        print(f"📋 Alertas pendentes: {alertas_pendentes}")
        
        # 4. Simula dados reais do Telegram
        print("\n📱 Simulando dados reais do Telegram...")
        
        # Dados reais do Telegram (baseado no formato real)
        webhook_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": 6435800936,  # ID real do Rafael Cabral
                    "is_bot": False,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafael_cabral",
                    "language_code": "pt"
                },
                "chat": {
                    "id": 6435800936,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafael_cabral",
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": "20:30"  # Resposta no formato HH:MM
            }
        }
        
        print(f"📤 Enviando webhook para o backend...")
        print(f"   User ID: {webhook_data['message']['from']['id']}")
        print(f"   Nome: {webhook_data['message']['from']['first_name']} {webhook_data['message']['from']['last_name']}")
        print(f"   Resposta: {webhook_data['message']['text']}")
        
        # 5. Envia o webhook para o backend
        try:
            response = requests.post(
                "http://localhost:8000/telegram-webhook",
                json=webhook_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📥 Resposta do webhook: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhook processado com sucesso")
                print(f"   Status: {result.get('status')}")
                print(f"   Mensagem: {result.get('msg')}")
                print(f"   Alerta ID: {result.get('alerta_id')}")
                print(f"   Alertas restantes: {result.get('alertas_restantes')}")
            else:
                print(f"❌ Erro no webhook: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao enviar webhook: {e}")
            return False
        
        # 6. Verifica se o alerta foi atualizado
        print("\n🔍 Verificando se o alerta foi atualizado...")
        
        db.refresh(novo_alerta)
        alerta_atualizado = db.query(Alerta).filter(Alerta.id == novo_alerta.id).first()
        
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
        if db:
            db.close()

def test_webhook_diferentes_formatos():
    """Testa diferentes formatos de resposta"""
    print("\n🧪 TESTE DE DIFERENTES FORMATOS")
    print("=" * 50)
    
    formatos_teste = [
        "20:30",
        "15:45", 
        "09:15",
        "23:59",
        "00:00"
    ]
    
    for formato in formatos_teste:
        print(f"\n📱 Testando formato: {formato}")
        
        webhook_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": 6435800936,
                    "is_bot": False,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafael_cabral",
                    "language_code": "pt"
                },
                "chat": {
                    "id": 6435800936,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafael_cabral",
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": formato
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/telegram-webhook",
                json=webhook_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Sucesso: {result.get('status')}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 TESTE DE WEBHOOK REAL")
    print("=" * 60)
    
    success = test_webhook_real()
    
    if success:
        test_webhook_diferentes_formatos()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ O webhook está funcionando corretamente")
        print("✅ As previsões estão sendo armazenadas")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas com o webhook")

if __name__ == "__main__":
    load_dotenv()
    main() 