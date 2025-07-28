#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de alertas automáticos
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auto_alert_endpoints():
    """Testa os endpoints de alertas automáticos"""
    
    print("=== Teste de Alertas Automáticos ===\n")
    
    # 1. Testa status inicial
    print("1. Verificando status inicial...")
    try:
        response = requests.get(f"{BASE_URL}/auto-alert/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Status: {status['is_active']}")
            print(f"   ✅ Intervalo: {status['interval_minutes']} minutos")
            print(f"   ✅ Última execução: {status['last_execution']}")
        else:
            print(f"   ❌ Erro ao obter status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 2. Testa criação de alerta manual
    print("\n2. Testando criação de alerta manual...")
    try:
        response = requests.post(f"{BASE_URL}/auto-alert/create-now")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Alerta criado com sucesso!")
            print(f"   ✅ ID do alerta: {result['alert_id']}")
            print(f"   ✅ Mensagem: {result['message']}")
        else:
            print(f"   ❌ Erro ao criar alerta: {response.status_code}")
            print(f"   ❌ Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 3. Testa ativação/desativação
    print("\n3. Testando ativação/desativação...")
    try:
        response = requests.post(f"{BASE_URL}/auto-alert/toggle")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Erro ao alternar status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 4. Testa atualização de intervalo
    print("\n4. Testando atualização de intervalo...")
    try:
        response = requests.post(f"{BASE_URL}/auto-alert/update-interval?interval_minutes=5")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ Erro ao atualizar intervalo: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 5. Verifica status final
    print("\n5. Verificando status final...")
    try:
        response = requests.get(f"{BASE_URL}/auto-alert/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Status: {status['is_active']}")
            print(f"   ✅ Intervalo: {status['interval_minutes']} minutos")
        else:
            print(f"   ❌ Erro ao obter status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    test_auto_alert_endpoints() 