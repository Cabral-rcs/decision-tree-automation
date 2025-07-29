#!/usr/bin/env python3
"""
Script para testar especificamente o armazenamento de previsões e mudança de categoria
"""

import os
import sys
import requests
import json
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_connection():
    """Testa se o backend está rodando"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend não está rodando: {e}")
        return False

def create_test_alert():
    """Cria um alerta de teste"""
    try:
        alert_data = {
            "problema": "TESTE PREVISÃO - Equipamento apresentando baixa eficiência",
            "codigo": "TEST001",
            "unidade": "Unidade Teste",
            "frente": "Frente de Teste",
            "equipamento": "Equipamento Teste",
            "tipo_operacao": "Teste",
            "operacao": "Operação de Teste",
            "nome_operador": "Operador Teste"
        }
        
        response = requests.post("http://localhost:8000/alertas", json=alert_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta de teste criado - ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro ao criar alerta de teste: {e}")
        return None

def check_alert_categories():
    """Verifica as categorias de alertas"""
    try:
        response = requests.get("http://localhost:8000/alertas", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Categorias de alertas:")
            print(f"   - Pendentes: {len(data.get('pendentes', []))}")
            print(f"   - Escaladas: {len(data.get('escaladas', []))}")
            print(f"   - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"   - Encerradas: {len(data.get('encerradas', []))}")
            return data
        else:
            print(f"❌ Erro ao verificar categorias: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao verificar categorias: {e}")
        return None

def simulate_telegram_response(previsao="15:30"):
    """Simula uma resposta do Telegram"""
    try:
        webhook_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": 6435800936,
                    "is_bot": False,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafaelcabral"
                },
                "chat": {
                    "id": 6435800936,
                    "first_name": "Rafael",
                    "last_name": "Cabral",
                    "username": "rafaelcabral",
                    "type": "private"
                },
                "date": int(datetime.now().timestamp()),
                "text": previsao
            }
        }
        
        print(f"📱 Simulando resposta do Telegram: {previsao}")
        response = requests.post(
            "http://localhost:8000/webhook/telegram",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processado: {result}")
            return True
        else:
            print(f"❌ Erro no webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao simular resposta: {e}")
        return False

def check_alert_debug():
    """Verifica o debug dos alertas"""
    try:
        response = requests.get("http://localhost:8000/alertas/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"🔍 Debug dos alertas:")
            print(f"   - Total: {data.get('total_alertas', 0)}")
            print(f"   - Pendentes: {data.get('pendentes', 0)}")
            print(f"   - Com previsão: {data.get('com_previsao', 0)}")
            
            print("📋 Últimos alertas:")
            for alerta in data.get('ultimos_alertas', []):
                print(f"   ID: {alerta['id']}")
                print(f"     Problema: {alerta['problema']}")
                print(f"     Previsão: {alerta['previsao']}")
                print(f"     Previsão DateTime: {alerta['previsao_datetime']}")
                print(f"     Status Operação: {alerta['status_operacao']}")
                print(f"     Respondido em: {alerta['respondido_em']}")
                print()
            return data
        else:
            print(f"❌ Erro no debug: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao verificar debug: {e}")
        return None

def test_previsao_storage():
    """Testa especificamente o armazenamento de previsões"""
    print("\n🧪 TESTE DE ARMAZENAMENTO DE PREVISÕES")
    print("=" * 50)
    
    # 1. Verifica se o backend está rodando
    if not test_backend_connection():
        print("❌ Backend não está rodando. Execute: uvicorn backend.main:app --reload")
        return False
    
    # 2. Verifica categorias iniciais
    print("\n📊 Categorias iniciais:")
    initial_categories = check_alert_categories()
    if not initial_categories:
        return False
    
    # 3. Cria alerta de teste
    print("\n📝 Criando alerta de teste...")
    alert_id = create_test_alert()
    if not alert_id:
        return False
    
    # 4. Verifica se o alerta foi para pendentes
    print("\n📊 Verificando se alerta foi para pendentes...")
    categories_after_create = check_alert_categories()
    if not categories_after_create:
        return False
    
    pendentes_after = len(categories_after_create.get('pendentes', []))
    if pendentes_after > len(initial_categories.get('pendentes', [])):
        print("✅ Alerta criado e adicionado aos pendentes")
    else:
        print("❌ Alerta não foi adicionado aos pendentes")
        return False
    
    # 5. Simula resposta do Telegram
    print("\n📱 Simulando resposta do Telegram...")
    previsao = "16:45"
    if not simulate_telegram_response(previsao):
        return False
    
    # 6. Verifica se o alerta mudou de categoria
    print("\n📊 Verificando mudança de categoria...")
    categories_after_response = check_alert_categories()
    if not categories_after_response:
        return False
    
    # 7. Verifica debug para confirmar previsão
    print("\n🔍 Verificando debug dos alertas...")
    debug_data = check_alert_debug()
    if not debug_data:
        return False
    
    # 8. Análise final
    print("\n📊 ANÁLISE FINAL:")
    print("=" * 50)
    
    # Verifica se a previsão foi armazenada
    alerta_com_previsao = None
    for alerta in debug_data.get('ultimos_alertas', []):
        if alerta['previsao'] == previsao:
            alerta_com_previsao = alerta
            break
    
    if alerta_com_previsao:
        print(f"✅ PREVISÃO ARMAZENADA CORRETAMENTE:")
        print(f"   - ID: {alerta_com_previsao['id']}")
        print(f"   - Previsão: {alerta_com_previsao['previsao']}")
        print(f"   - Previsão DateTime: {alerta_com_previsao['previsao_datetime']}")
        print(f"   - Respondido em: {alerta_com_previsao['respondido_em']}")
    else:
        print("❌ PREVISÃO NÃO FOI ARMAZENADA")
        return False
    
    # Verifica mudança de categoria
    pendentes_final = len(categories_after_response.get('pendentes', []))
    escaladas_final = len(categories_after_response.get('escaladas', []))
    
    print(f"\n📊 MUDANÇA DE CATEGORIA:")
    print(f"   - Pendentes antes: {len(initial_categories.get('pendentes', []))}")
    print(f"   - Pendentes depois: {pendentes_final}")
    print(f"   - Escaladas depois: {escaladas_final}")
    
    if pendentes_final < pendentes_after and escaladas_final > len(initial_categories.get('escaladas', [])):
        print("✅ ALERTA MUDOU DE CATEGORIA CORRETAMENTE")
        print("   - Saiu de 'Pendentes' e foi para 'Escaladas'")
        return True
    else:
        print("❌ ALERTA NÃO MUDOU DE CATEGORIA")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DE PREVISÕES E MUDANÇA DE CATEGORIA")
    print("=" * 60)
    
    success = test_previsao_storage()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ As respostas do Telegram estão sendo armazenadas na coluna Previsão")
        print("✅ Os alertas estão mudando de categoria automaticamente")
        print("✅ O sistema está funcionando corretamente")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas no armazenamento de previsões ou mudança de categoria")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Verifique o frontend para confirmar visualmente")
    print("2. Teste com diferentes horários (HH:MM)")
    print("3. Teste a mudança de status de operação")
    print("4. Verifique se as categorias estão corretas")

if __name__ == "__main__":
    load_dotenv()
    main() 