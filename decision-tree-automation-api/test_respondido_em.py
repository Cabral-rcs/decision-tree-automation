#!/usr/bin/env python3
"""
Script de teste para verificar a correção do campo respondido_em
"""

import requests
import json
from datetime import datetime

def test_respondido_em():
    """Testa a correção do campo respondido_em"""
    print("🕐 TESTE DO CAMPO RESPONDIDO_EM")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Criar um alerta automático
    print("1️⃣ Criando alerta automático...")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=30)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get('alert_id')
            print(f"✅ Alerta criado: ID {alert_id}")
            
            # Aguarda um pouco para garantir que foi criado
            import time
            time.sleep(2)
            
            # 2. Verificar o alerta criado
            print("\n2️⃣ Verificando alerta criado...")
            response2 = requests.get(f'{base_url}/alertas', timeout=30)
            if response2.status_code == 200:
                data2 = response2.json()
                pendentes = data2.get('pendentes', [])
                
                # Encontra o alerta criado
                alerta_criado = None
                for alerta in pendentes:
                    if alerta['id'] == alert_id:
                        alerta_criado = alerta
                        break
                
                if alerta_criado:
                    print(f"✅ Alerta encontrado na lista de pendentes")
                    print(f"   - ID: {alerta_criado['id']}")
                    print(f"   - Criado em: {alerta_criado['criado_em']}")
                    print(f"   - Respondido em: {alerta_criado.get('respondido_em', 'Não definido')}")
                    print(f"   - Status: {alerta_criado.get('status', 'N/A')}")
                    
                    # Verifica se respondido_em está vazio (deveria estar)
                    if not alerta_criado.get('respondido_em'):
                        print("✅ Campo respondido_em está vazio (correto - ainda não foi respondido)")
                    else:
                        print("⚠️  Campo respondido_em já tem valor (pode ser um problema)")
                    
                    # 3. Simular resposta do líder
                    print("\n3️⃣ Simulando resposta do líder...")
                    print("   - Envie uma mensagem para o bot no Telegram (ex: '15:30')")
                    print("   - Aguarde alguns segundos")
                    print("   - Execute novamente este script para verificar")
                    
                else:
                    print(f"❌ Alerta {alert_id} não encontrado na lista de pendentes")
            else:
                print(f"❌ Erro ao listar alertas: {response2.status_code}")
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar criação: {e}")
    
    # 4. Verificar alertas escaladas (que já foram respondidos)
    print("\n4️⃣ Verificando alertas escaladas...")
    try:
        response3 = requests.get(f'{base_url}/alertas', timeout=30)
        if response3.status_code == 200:
            data3 = response3.json()
            escaladas = data3.get('escaladas', [])
            
            if escaladas:
                print(f"📋 Alertas escaladas encontrados: {len(escaladas)}")
                for alerta in escaladas:
                    print(f"   - ID: {alerta['id']}")
                    print(f"     Criado em: {alerta['criado_em']}")
                    print(f"     Respondido em: {alerta.get('respondido_em', 'N/A')}")
                    print(f"     Previsão: {alerta.get('previsao', 'N/A')}")
                    
                    # Verifica se respondido_em é igual ao criado_em
                    if alerta.get('respondido_em') and alerta.get('criado_em'):
                        if alerta['respondido_em'] == alerta['criado_em']:
                            print(f"     ✅ respondido_em = criado_em (CORRETO)")
                        else:
                            print(f"     ❌ respondido_em ≠ criado_em (PROBLEMA)")
                            print(f"        respondido_em: {alerta['respondido_em']}")
                            print(f"        criado_em: {alerta['criado_em']}")
                    print()
            else:
                print("📋 Nenhum alerta escalado encontrado")
        else:
            print(f"❌ Erro ao listar alertas: {response3.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar escaladas: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Envie uma mensagem para o bot no Telegram (ex: '15:30')")
    print("2. Execute novamente este script para verificar se respondido_em = criado_em")
    print("3. Confirme que o alerta aparece na categoria 'Escaladas'")

if __name__ == "__main__":
    test_respondido_em() 