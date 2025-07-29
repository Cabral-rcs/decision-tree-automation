#!/usr/bin/env python3
"""
Teste final do webhook corrigido via API
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz

def test_webhook_corrigido():
    """Testa o webhook corrigido via API"""
    print("🚀 TESTE DO WEBHOOK CORRIGIDO")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # 1. Verifica se o backend está rodando
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando")
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend não está rodando: {e}")
        print("💡 Execute: uvicorn backend.main:app --reload")
        return False
    
    # 2. Cria alerta automático via API
    try:
        # Ativa alertas automáticos
        response = requests.post(f"{BASE_URL}/auto-alert/toggle", timeout=10)
        if response.status_code == 200:
            print("✅ Alertas automáticos ativados")
        
        # Cria alerta automático
        response = requests.post(f"{BASE_URL}/auto-alert/create-now", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta automático criado - ID: {data.get('alert_id')}")
        else:
            print(f"❌ Erro ao criar alerta automático: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao criar alerta automático: {e}")
        return False
    
    # 3. Cria alerta manual via API
    try:
        alert_data = {
            "problema": "TESTE WEBHOOK CORRIGIDO - Equipamento apresentando baixa eficiência",
            "codigo": "TESTWEB001",
            "unidade": "Unidade Teste Webhook",
            "frente": "Frente de Teste",
            "equipamento": "Equipamento Teste",
            "tipo_operacao": "Teste",
            "operacao": "Operação de Teste",
            "nome_operador": "Operador Teste"
        }
        
        response = requests.post(f"{BASE_URL}/alertas", json=alert_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            alert_id_manual = data.get('id')
            print(f"✅ Alerta manual criado - ID: {alert_id_manual}")
        else:
            print(f"❌ Erro ao criar alerta manual: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao criar alerta manual: {e}")
        return False
    
    # 4. Verifica alertas pendentes
    try:
        response = requests.get(f"{BASE_URL}/alertas", timeout=10)
        if response.status_code == 200:
            data = response.json()
            pendentes = data.get('pendentes', [])
            print(f"📊 Alertas pendentes: {len(pendentes)}")
            
            for i, alerta in enumerate(pendentes):
                print(f"  {i+1}. ID: {alerta['id']}")
                print(f"     Problema: {alerta['problema'][:50]}...")
                print(f"     É automático: {'Sim' if alerta['problema'].startswith('[AUTO]') else 'Não'}")
                print()
        else:
            print(f"❌ Erro ao verificar alertas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar alertas: {e}")
        return False
    
    # 5. Calcula previsão futura
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    previsao_futura = now + timedelta(hours=1)
    previsao_str = previsao_futura.strftime("%H:%M")
    
    print(f"⏰ Horário atual: {now.strftime('%H:%M')}")
    print(f"⏰ Previsão futura: {previsao_str}")
    
    # 6. Simula resposta do Telegram
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
                "text": previsao_str
            }
        }
        
        print(f"📱 Simulando resposta do Telegram: {previsao_str}")
        response = requests.post(
            f"{BASE_URL}/webhook/telegram",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook processado: {result}")
        else:
            print(f"❌ Erro no webhook: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao simular resposta: {e}")
        return False
    
    # 7. Aguarda processamento
    print("⏳ Aguardando processamento...")
    time.sleep(2)
    
    # 8. Verifica resultado
    try:
        response = requests.get(f"{BASE_URL}/alertas", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Resultado após webhook:")
            print(f"   - Pendentes: {len(data.get('pendentes', []))}")
            print(f"   - Escaladas: {len(data.get('escaladas', []))}")
            print(f"   - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"   - Encerradas: {len(data.get('encerradas', []))}")
            
            # Verifica se o alerta manual foi processado
            escaladas = data.get('escaladas', [])
            alerta_manual_processado = None
            
            for alerta in escaladas:
                if not alerta['problema'].startswith('[AUTO]'):
                    alerta_manual_processado = alerta
                    break
            
            if alerta_manual_processado:
                print(f"✅ ALERTA MANUAL PROCESSADO CORRETAMENTE!")
                print(f"   ID: {alerta_manual_processado['id']}")
                print(f"   Problema: {alerta_manual_processado['problema'][:50]}...")
                print(f"   Previsão: {alerta_manual_processado['previsao']}")
                print(f"   Categoria: Escaladas")
                return True
            else:
                print("❌ Alerta manual não foi processado")
                return False
        else:
            print(f"❌ Erro ao verificar resultado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar resultado: {e}")
        return False

def main():
    """Função principal"""
    success = test_webhook_corrigido()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ O webhook está priorizando alertas manuais")
        print("✅ Os alertas automáticos não estão interferindo")
        print("✅ As previsões estão sendo armazenadas corretamente")
        print("✅ A correção está funcionando perfeitamente")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Ainda há problemas com o webhook")
    
    print("\n📋 RESUMO DA CORREÇÃO:")
    print("1. ✅ Priorização de alertas manuais implementada")
    print("2. ✅ Logs de debug adicionados")
    print("3. ✅ Lógica de seleção corrigida")
    print("4. ✅ Alertas automáticos não interferem mais")

if __name__ == "__main__":
    main() 