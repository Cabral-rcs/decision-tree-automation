#!/usr/bin/env python3
"""
Script para simular resposta do Telegram e testar a categorização
"""

import requests
import json
from datetime import datetime
import pytz

def simular_resposta_telegram():
    """Simula uma resposta do Telegram para testar a categorização"""
    print("🤖 SIMULANDO RESPOSTA DO TELEGRAM")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ HORÁRIO ATUAL")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print()
    
    # 2. Verificar alertas pendentes
    print("2️⃣ VERIFICANDO ALERTAS PENDENTES")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            pendentes = data.get('pendentes', [])
            
            if pendentes:
                alerta = pendentes[0]
                print(f"   ✅ Alerta pendente encontrado: ID {alerta['id']}")
                print(f"      Criado em: {alerta.get('criado_em', 'N/A')}")
                print(f"      Problema: {alerta.get('problema', 'N/A')[:50]}...")
            else:
                print("   ❌ Nenhum alerta pendente encontrado")
                return
        else:
            print(f"   ❌ Erro ao listar alertas: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao verificar alertas: {e}")
        return
    
    # 3. Simular resposta do Telegram
    print("\n3️⃣ SIMULANDO RESPOSTA DO TELEGRAM")
    
    # Calcular horário futuro para a previsão (2 horas à frente)
    hora_futura = (now_br.hour + 2) % 24
    previsao = f"{hora_futura:02d}:30"
    
    print(f"   Previsão simulada: {previsao}")
    print(f"   Horário atual: {now_br.strftime('%H:%M')}")
    print(f"   Previsão será para: {hora_futura:02d}:30")
    
    # Dados simulados de uma mensagem do Telegram
    test_data = {
        "message": {
            "message_id": 999,
            "from": {
                "id": 6435800936,  # ID do Rafael Cabral
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
            "text": previsao  # Resposta simulada
        }
    }
    
    print(f"   Dados simulados: {json.dumps(test_data, indent=2)}")
    
    # 4. Enviar simulação para o webhook REAL (não o de teste)
    print("\n4️⃣ ENVIANDO SIMULAÇÃO PARA O WEBHOOK REAL")
    try:
        response = requests.post(f'{base_url}/telegram-webhook', json=test_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Simulação enviada com sucesso")
            print(f"   Resultado: {result.get('message', 'Sucesso')}")
        else:
            print(f"   ❌ Erro na simulação: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro ao enviar simulação: {e}")
    
    # 5. Verificar resultado da categorização
    print("\n5️⃣ VERIFICANDO RESULTADO DA CATEGORIZAÇÃO")
    import time
    time.sleep(3)  # Aguarda processamento
    
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            print(f"   Alertas por categoria:")
            print(f"      - Pendentes: {len(data.get('pendentes', []))}")
            print(f"      - Escaladas: {len(data.get('escaladas', []))}")
            print(f"      - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"      - Encerradas: {len(data.get('encerradas', []))}")
            
            # Verificar se o alerta foi para escaladas
            escaladas = data.get('escaladas', [])
            if escaladas:
                alerta_escalado = escaladas[0]
                print(f"\n   ✅ Alerta movido para ESCALADAS:")
                print(f"      ID: {alerta_escalado['id']}")
                print(f"      Previsão: {alerta_escalado.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta_escalado.get('previsao_datetime', 'N/A')}")
                print(f"      Respondido em: {alerta_escalado.get('respondido_em', 'N/A')}")
                print(f"      Status: {alerta_escalado.get('status_operacao', 'N/A')}")
                
                # Verificar se a previsão está no futuro
                if alerta_escalado.get('previsao_datetime'):
                    try:
                        previsao_str = alerta_escalado['previsao_datetime']
                        if 'Z' in previsao_str:
                            previsao_str = previsao_str.replace('Z', '+00:00')
                        
                        previsao_dt = datetime.fromisoformat(previsao_str)
                        
                        # Garantir timezone
                        if previsao_dt.tzinfo is None:
                            previsao_dt = pytz.utc.localize(previsao_dt).astimezone(tz_br)
                        else:
                            previsao_dt = previsao_dt.astimezone(tz_br)
                        
                        if previsao_dt > now_br:
                            print(f"      ✅ Previsão no FUTURO: {previsao_dt}")
                        else:
                            print(f"      ❌ Previsão no PASSADO: {previsao_dt}")
                            
                    except Exception as e:
                        print(f"      ❌ Erro ao processar previsão: {e}")
                
            else:
                print(f"\n   ❌ Alerta não foi para escaladas")
                
                # Verificar se foi para atrasadas
                atrasadas = data.get('atrasadas', [])
                if atrasadas:
                    print(f"   ❌ Alerta foi para ATRASADAS (PROBLEMA!)")
                    alerta_atrasado = atrasadas[0]
                    print(f"      ID: {alerta_atrasado['id']}")
                    print(f"      Previsão: {alerta_atrasado.get('previsao', 'N/A')}")
                    print(f"      Previsão DT: {alerta_atrasado.get('previsao_datetime', 'N/A')}")
        else:
            print(f"   ❌ Erro ao verificar resultado: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar resultado: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 SIMULAÇÃO CONCLUÍDA")

if __name__ == "__main__":
    import time
    simular_resposta_telegram() 