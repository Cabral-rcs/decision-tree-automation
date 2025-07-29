#!/usr/bin/env python3
"""
Teste direto para simular alerta atrasado
"""

import requests
import json
from datetime import datetime, timedelta
import pytz
import time

def test_direto_atrasadas():
    """Teste direto para simular alerta atrasado"""
    print("🧪 TESTE DIRETO - ALERTA ATRASADO")
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
    
    # 4. Simular resposta do Telegram com previsão no passado
    print("\n4️⃣ SIMULANDO RESPOSTA COM PREVISÃO NO PASSADO")
    time.sleep(2)
    
    # Usar uma previsão que será ajustada para o próximo dia mas ainda ficará no passado
    hora_passada = 5  # 5:30 da manhã (muito cedo)
    previsao_passada = f"{hora_passada:02d}:30"
    
    print(f"   Previsão no passado: {previsao_passada}")
    print(f"   Horário atual: {now_br.strftime('%H:%M')}")
    print(f"   Previsão será ajustada para o próximo dia mas ainda ficará no passado")
    
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
    
    # 5. Verificar categorização
    print("\n5️⃣ VERIFICANDO CATEGORIZAÇÃO")
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
            
            # Verificar onde está o alerta
            all_alertas = []
            all_alertas.extend(data.get('pendentes', []))
            all_alertas.extend(data.get('escaladas', []))
            all_alertas.extend(data.get('atrasadas', []))
            all_alertas.extend(data.get('encerradas', []))
            
            if all_alertas:
                alerta = all_alertas[0]
                print(f"\n   📋 ALERTA ENCONTRADO:")
                print(f"      ID: {alerta['id']}")
                print(f"      Status: {alerta.get('status_operacao', 'N/A')}")
                print(f"      Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                
                # Verificar se está em atrasadas
                atrasadas = data.get('atrasadas', [])
                if atrasadas:
                    print(f"      ✅ Alerta está em ATRASADAS")
                    
                    # 6. Testar mudança de status
                    print(f"\n6️⃣ TESTANDO MUDANÇA DE STATUS (ATRASADA → ENCERRADA)")
                    
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
                    print(f"\n7️⃣ VERIFICANDO SE FOI PARA ENCERRADAS")
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
                else:
                    print(f"      ❌ Alerta não está em atrasadas")
                    print(f"      ⚠️  Precisamos criar um alerta que realmente fique atrasado")
            else:
                print(f"   ❌ Nenhum alerta encontrado")
        else:
            print(f"   ❌ Erro ao listar alertas: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar alertas: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_direto_atrasadas() 