#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema está funcionando corretamente
"""

import requests
import json
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Testa se o backend está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend está funcionando")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return False

def test_alertas_endpoint():
    """Testa o endpoint de alertas"""
    try:
        response = requests.get(f"{BASE_URL}/alertas")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint /alertas funcionando")
            print(f"   - Pendentes: {len(data.get('pendentes', []))}")
            print(f"   - Escaladas: {len(data.get('escaladas', []))}")
            print(f"   - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"   - Encerradas: {len(data.get('encerradas', []))}")
            return True
        else:
            print(f"❌ Endpoint /alertas retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint /alertas: {e}")
        return False

def test_debug_endpoint():
    """Testa o endpoint de debug"""
    try:
        response = requests.get(f"{BASE_URL}/alertas/debug")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint /alertas/debug funcionando")
            print(f"   - Total de alertas: {data.get('total_alertas', 0)}")
            print(f"   - Pendentes: {data.get('pendentes', 0)}")
            print(f"   - Com prazo: {data.get('com_prazo', 0)}")
            return True
        else:
            print(f"❌ Endpoint /alertas/debug retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint /alertas/debug: {e}")
        return False

def test_auto_alert_status():
    """Testa o status dos alertas automáticos"""
    try:
        response = requests.get(f"{BASE_URL}/auto-alert/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint /auto-alert/status funcionando")
            print(f"   - Ativo: {data.get('is_active', False)}")
            print(f"   - Intervalo: {data.get('interval_minutes', 0)} minutos")
            return True
        else:
            print(f"❌ Endpoint /auto-alert/status retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint /auto-alert/status: {e}")
        return False

def test_create_alert():
    """Testa a criação de um alerta"""
    try:
        alert_data = {
            "problema": "Teste de alerta via script",
            "codigo": "TEST001",
            "unidade": "Unidade Teste",
            "frente": "Frente de Teste",
            "equipamento": "Equipamento Teste",
            "tipo_operacao": "Teste",
            "operacao": "Operação de Teste",
            "nome_operador": "Operador Teste"
        }
        
        response = requests.post(f"{BASE_URL}/alertas", json=alert_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta criado com sucesso - ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao testar criação de alerta: {e}")
        return None

def main():
    """Função principal de teste"""
    print("🧪 INICIANDO TESTES DO SISTEMA")
    print("=" * 50)
    
    # Teste 1: Backend
    print("\n1. Testando backend...")
    if not test_backend_health():
        print("❌ Backend não está funcionando. Aborte os testes.")
        return
    
    # Teste 2: Endpoint de alertas
    print("\n2. Testando endpoint de alertas...")
    test_alertas_endpoint()
    
    # Teste 3: Endpoint de debug
    print("\n3. Testando endpoint de debug...")
    test_debug_endpoint()
    
    # Teste 4: Status dos alertas automáticos
    print("\n4. Testando status dos alertas automáticos...")
    test_auto_alert_status()
    
    # Teste 5: Criação de alerta
    print("\n5. Testando criação de alerta...")
    alert_id = test_create_alert()
    
    if alert_id:
        print(f"\n✅ Alerta criado com ID: {alert_id}")
        print("📱 Agora teste responder no Telegram com formato HH:MM")
        print("🔄 O alerta deve mudar de 'Aguardando Previsão' para 'Escalada'")
    
    print("\n" + "=" * 50)
    print("🏁 TESTES CONCLUÍDOS")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Abra o frontend: decision-tree-automation-ui/index.html")
    print("2. Verifique se o alerta aparece na categoria 'Aguardando Previsão'")
    print("3. Responda no Telegram com formato HH:MM (ex: 15:30)")
    print("4. Verifique se o alerta muda para 'Escalada'")
    print("5. Use o botão 'Debug Alertas' para verificar o status")

if __name__ == "__main__":
    main() 