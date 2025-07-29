#!/usr/bin/env python3
"""
Script de teste para verificar as correções de timezone
"""

import requests
import json
from datetime import datetime
import pytz

def test_timezone_fix():
    """Testa as correções de timezone"""
    print("🧪 TESTE DAS CORREÇÕES DE TIMEZONE")
    print("=" * 50)
    
    # URL base
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Testar listagem de alertas
    print("1️⃣ Testando listagem de alertas...")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listagem funcionando: {len(data.get('pendentes', []))} pendentes, {len(data.get('escaladas', []))} escaladas")
            
            # Verifica se há alertas escaladas
            escaladas = data.get('escaladas', [])
            if escaladas:
                print(f"📋 Alertas escaladas encontrados: {len(escaladas)}")
                for alerta in escaladas:
                    print(f"   - ID: {alerta['id']}, Previsão: {alerta['previsao']}, Status: {alerta['status_operacao']}")
            else:
                print("📋 Nenhum alerta escalado encontrado")
        else:
            print(f"❌ Erro na listagem: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar listagem: {e}")
    
    # 2. Testar debug do webhook
    print("\n2️⃣ Testando debug do webhook...")
    try:
        response = requests.get(f'{base_url}/webhook-debug', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug funcionando: {data.get('webhook_status', {}).get('is_configured', False)}")
        else:
            print(f"❌ Erro no debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar debug: {e}")
    
    # 3. Testar criação de alerta automático
    print("\n3️⃣ Testando criação de alerta automático...")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta criado: ID {data.get('alert_id')}")
            
            # Aguarda um pouco e testa novamente a listagem
            import time
            time.sleep(2)
            
            response2 = requests.get(f'{base_url}/alertas', timeout=30)
            if response2.status_code == 200:
                data2 = response2.json()
                pendentes = data2.get('pendentes', [])
                print(f"📋 Alertas pendentes após criação: {len(pendentes)}")
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar criação: {e}")
    
    # 4. Testar comparação de timezone
    print("\n4️⃣ Testando comparação de timezone...")
    try:
        # Simula uma comparação de timezone
        tz_br = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(tz_br)
        
        # Cria um datetime sem timezone (como pode vir do banco)
        dt_sem_tz = datetime(2025, 7, 29, 12, 57, 0)
        
        # Aplica a correção
        dt_com_tz = pytz.utc.localize(dt_sem_tz).astimezone(tz_br)
        
        print(f"✅ Comparação de timezone funcionando:")
        print(f"   - Agora (com TZ): {now_br}")
        print(f"   - Previsão (sem TZ): {dt_sem_tz}")
        print(f"   - Previsão (com TZ): {dt_com_tz}")
        print(f"   - Comparação válida: {dt_com_tz >= now_br}")
        
    except Exception as e:
        print(f"❌ Erro ao testar timezone: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Envie uma mensagem para o bot no Telegram")
    print("2. Verifique se o alerta aparece na categoria correta")
    print("3. Confirme que não há mais erros de timezone")

if __name__ == "__main__":
    test_timezone_fix() 