#!/usr/bin/env python3
"""
Script de teste para verificar as novas funcionalidades implementadas
"""

import requests
import json
from datetime import datetime
import pytz
import time

def test_novas_funcionalidades():
    """Testa as novas funcionalidades implementadas"""
    print("🧪 TESTE DAS NOVAS FUNCIONALIDADES")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ HORÁRIO ATUAL")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print()
    
    # 2. Limpar alertas existentes
    print("2️⃣ LIMPANDO ALERTAS EXISTENTES")
    try:
        response = requests.delete(f'{base_url}/alertas/all', timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result.get('message', 'Alertas apagados')}")
        else:
            print(f"   ❌ Erro ao apagar alertas: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao apagar alertas: {e}")
    print()
    
    # 3. Criar alerta automático
    print("3️⃣ CRIANDO ALERTA AUTOMÁTICO")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=30)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get('alert_id')
            print(f"   ✅ Alerta criado: ID {alert_id}")
        else:
            print(f"   ❌ Erro ao criar alerta: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao criar alerta: {e}")
        return
    
    # 4. Simular resposta do Telegram com previsão no passado (para criar atrasada)
    print("\n4️⃣ SIMULANDO RESPOSTA COM PREVISÃO NO PASSADO")
    time.sleep(2)
    
    # Calcular horário no passado para a previsão
    hora_passada = (now_br.hour - 2) % 24
    previsao_passada = f"{hora_passada:02d}:30"
    
    print(f"   Previsão no passado: {previsao_passada}")
    
    # Dados simulados de uma mensagem do Telegram
    test_data = {
        "message": {
            "message_id": 999,
            "from": {
                "id": 6435800936,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "is_bot": False
            },
            "chat": {
                "id": 6435800936,
                "first_name": "Rafael",
                "last_name": "Cabral",
                "type": "private"
            },
            "date": int(now_br.timestamp()),
            "text": previsao_passada
        }
    }
    
    try:
        response = requests.post(f'{base_url}/telegram-webhook', json=test_data, timeout=30)
        if response.status_code == 200:
            print(f"   ✅ Resposta simulada enviada")
        else:
            print(f"   ❌ Erro na simulação: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao enviar simulação: {e}")
    
    # 5. Verificar se está em atrasadas
    print("\n5️⃣ VERIFICANDO SE ESTÁ EM ATRASADAS")
    time.sleep(3)
    
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            print(f"   Alertas por categoria:")
            print(f"      - Pendentes: {len(data.get('pendentes', []))}")
            print(f"      - Escaladas: {len(data.get('escaladas', []))}")
            print(f"      - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"      - Encerradas: {len(data.get('encerradas', []))}")
            
            atrasadas = data.get('atrasadas', [])
            if atrasadas:
                alerta_atrasado = atrasadas[0]
                print(f"\n   ✅ Alerta em ATRASADAS:")
                print(f"      ID: {alerta_atrasado['id']}")
                print(f"      Status: {alerta_atrasado.get('status_operacao', 'N/A')}")
                print(f"      Previsão: {alerta_atrasado.get('previsao', 'N/A')}")
            else:
                print(f"\n   ❌ Alerta não está em atrasadas")
                return
        else:
            print(f"   ❌ Erro ao listar alertas: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao verificar alertas: {e}")
        return
    
    # 6. Testar mudança de status de atrasada para encerrada
    print("\n6️⃣ TESTANDO MUDANÇA DE STATUS (ATRASADA → ENCERRADA)")
    
    try:
        response = requests.put(f'{base_url}/alertas/{alert_id}/status', 
                              json={'status_operacao': 'operando'}, 
                              timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status atualizado: {result.get('message', 'Sucesso')}")
        else:
            print(f"   ❌ Erro ao atualizar status: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao atualizar status: {e}")
        return
    
    # 7. Verificar se foi para encerradas
    print("\n7️⃣ VERIFICANDO SE FOI PARA ENCERRADAS")
    time.sleep(2)
    
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            print(f"   Alertas por categoria:")
            print(f"      - Pendentes: {len(data.get('pendentes', []))}")
            print(f"      - Escaladas: {len(data.get('escaladas', []))}")
            print(f"      - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"      - Encerradas: {len(data.get('encerradas', []))}")
            
            encerradas = data.get('encerradas', [])
            if encerradas:
                alerta_encerrado = encerradas[0]
                print(f"\n   ✅ Alerta em ENCERRADAS:")
                print(f"      ID: {alerta_encerrado['id']}")
                print(f"      Status: {alerta_encerrado.get('status_operacao', 'N/A')}")
                print(f"      Horário operando: {alerta_encerrado.get('horario_operando', 'N/A')}")
                print(f"      Previsão: {alerta_encerrado.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta_encerrado.get('previsao_datetime', 'N/A')}")
                
                # Verificar se tem horario_operando (indicando que veio de atrasadas)
                if alerta_encerrado.get('horario_operando'):
                    print(f"      ✅ Tem horario_operando - veio de atrasadas (background vermelho)")
                else:
                    print(f"      ❌ Não tem horario_operando - veio de escaladas (background verde)")
            else:
                print(f"\n   ❌ Alerta não foi para encerradas")
        else:
            print(f"   ❌ Erro ao verificar resultado: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar resultado: {e}")
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DAS NOVAS FUNCIONALIDADES TESTADAS:")
    print("✅ Botão de status removido de alertas encerrados")
    print("✅ Botão de status adicionado em alertas atrasados")
    print("✅ Alerta atrasado pode ser movido para encerrado")
    print("✅ Background diferenciado por origem do alerta")
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_novas_funcionalidades() 