#!/usr/bin/env python3
"""
Script de teste para verificar se as correções da categorização funcionaram
"""

import requests
import json
from datetime import datetime
import pytz
import time

def test_correcao_categorizacao():
    """Testa se as correções da categorização funcionaram"""
    print("🧪 TESTE DA CORREÇÃO DA CATEGORIZAÇÃO")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ HORÁRIO ATUAL")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print()
    
    # 2. Apagar todos os alertas existentes
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
    
    # 3. Criar um alerta automático
    print("3️⃣ CRIANDO ALERTA AUTOMÁTICO")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=30)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get('alert_id')
            print(f"   ✅ Alerta criado: ID {alert_id}")
            
            # Aguarda um pouco
            time.sleep(2)
            
            # 4. Verificar se está em pendentes
            print("\n4️⃣ VERIFICANDO SE ESTÁ EM PENDENTES")
            response2 = requests.get(f'{base_url}/alertas', timeout=30)
            if response2.status_code == 200:
                data2 = response2.json()
                pendentes = data2.get('pendentes', [])
                
                if pendentes:
                    alerta_pendente = pendentes[0]
                    print(f"   ✅ Alerta {alerta_pendente['id']} está em pendentes")
                    print(f"      Criado em: {alerta_pendente.get('criado_em', 'N/A')}")
                    print(f"      Status: {alerta_pendente.get('status_operacao', 'N/A')}")
                    print(f"      Previsão: {alerta_pendente.get('previsao', 'N/A')}")
                else:
                    print(f"   ❌ Alerta não está em pendentes")
                    print(f"   Alertas por categoria:")
                    print(f"      - Pendentes: {len(data2.get('pendentes', []))}")
                    print(f"      - Escaladas: {len(data2.get('escaladas', []))}")
                    print(f"      - Atrasadas: {len(data2.get('atrasadas', []))}")
                    print(f"      - Encerradas: {len(data2.get('encerradas', []))}")
            else:
                print(f"   ❌ Erro ao listar alertas: {response2.status_code}")
        else:
            print(f"   ❌ Erro ao criar alerta: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao testar criação: {e}")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUÇÕES PARA TESTE MANUAL:")
    print("1. Envie uma mensagem para o bot no Telegram")
    print("2. Use um horário no futuro (ex: '18:00' ou '23:30')")
    print("3. Aguarde alguns segundos")
    print("4. Execute novamente este script para verificar")
    print("5. O alerta deve aparecer em 'Escaladas', não em 'Atrasadas'")
    
    print("\n📋 RESULTADO ESPERADO:")
    print("✅ Alerta criado em pendentes")
    print("✅ Após resposta, alerta vai para escaladas")
    print("✅ Previsão datetime está no futuro")
    print("✅ respondido_em usa horário atual real")

if __name__ == "__main__":
    test_correcao_categorizacao() 