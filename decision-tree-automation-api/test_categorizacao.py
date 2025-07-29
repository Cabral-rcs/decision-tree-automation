#!/usr/bin/env python3
"""
Script de teste para verificar a categorização de alertas
"""

import requests
import json
from datetime import datetime
import pytz

def test_categorizacao():
    """Testa a categorização de alertas"""
    print("🎯 TESTE DE CATEGORIZAÇÃO DE ALERTAS")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ Verificando horário atual...")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    
    # 2. Criar um alerta automático
    print("\n2️⃣ Criando alerta automático...")
    try:
        response = requests.post(f'{base_url}/auto-alert/create-now', timeout=30)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get('alert_id')
            print(f"✅ Alerta criado: ID {alert_id}")
            
            # Aguarda um pouco
            import time
            time.sleep(2)
            
            # 3. Verificar se está em pendentes
            print("\n3️⃣ Verificando se está em pendentes...")
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
                    print(f"✅ Alerta {alert_id} encontrado em pendentes")
                    print(f"   - Criado em: {alerta_criado['criado_em']}")
                    print(f"   - Status: {alerta_criado.get('status_operacao', 'N/A')}")
                    
                    # 4. Simular resposta do líder
                    print("\n4️⃣ Simulando resposta do líder...")
                    print("   - Envie uma mensagem para o bot no Telegram")
                    print("   - Use um horário no futuro (ex: '18:00' ou '23:30')")
                    print("   - Aguarde alguns segundos")
                    print("   - Execute novamente este script para verificar")
                    
                else:
                    print(f"❌ Alerta {alert_id} não encontrado em pendentes")
            else:
                print(f"❌ Erro ao listar alertas: {response2.status_code}")
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar criação: {e}")
    
    # 5. Verificar alertas escaladas
    print("\n5️⃣ Verificando alertas escaladas...")
    try:
        response3 = requests.get(f'{base_url}/alertas', timeout=30)
        if response3.status_code == 200:
            data3 = response3.json()
            escaladas = data3.get('escaladas', [])
            
            if escaladas:
                print(f"📋 Alertas escaladas encontrados: {len(escaladas)}")
                for alerta in escaladas:
                    print(f"   - ID: {alerta['id']}")
                    print(f"     Criado: {alerta['criado_em']}")
                    print(f"     Respondido: {alerta.get('respondido_em', 'N/A')}")
                    print(f"     Previsão: {alerta.get('previsao', 'N/A')}")
                    print(f"     Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                    print(f"     Status: {alerta.get('status_operacao', 'N/A')}")
                    
                    # Verificar se respondido_em = criado_em
                    if alerta.get('respondido_em') and alerta.get('criado_em'):
                        if alerta['respondido_em'] == alerta['criado_em']:
                            print(f"     ✅ respondido_em = criado_em")
                        else:
                            print(f"     ❌ respondido_em ≠ criado_em")
                    
                    # Verificar se previsão está no futuro
                    if alerta.get('previsao_datetime'):
                        try:
                            previsao_dt = datetime.fromisoformat(alerta['previsao_datetime'].replace('Z', '+00:00'))
                            if previsao_dt.tzinfo is None:
                                previsao_dt = pytz.utc.localize(previsao_dt).astimezone(tz_br)
                            else:
                                previsao_dt = previsao_dt.astimezone(tz_br)
                            
                            if previsao_dt > now_br:
                                print(f"     ✅ Previsão no futuro: {previsao_dt}")
                            else:
                                print(f"     ❌ Previsão no passado: {previsao_dt}")
                        except Exception as e:
                            print(f"     ❌ Erro ao processar previsão: {e}")
                    print()
            else:
                print("📋 Nenhum alerta escalado encontrado")
        else:
            print(f"❌ Erro ao listar alertas: {response3.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar escaladas: {e}")
    
    # 6. Verificar alertas atrasadas
    print("\n6️⃣ Verificando alertas atrasadas...")
    try:
        response4 = requests.get(f'{base_url}/alertas', timeout=30)
        if response4.status_code == 200:
            data4 = response4.json()
            atrasadas = data4.get('atrasadas', [])
            
            if atrasadas:
                print(f"📋 Alertas atrasadas encontrados: {len(atrasadas)}")
                for alerta in atrasadas:
                    print(f"   - ID: {alerta['id']}")
                    print(f"     Criado: {alerta['criado_em']}")
                    print(f"     Respondido: {alerta.get('respondido_em', 'N/A')}")
                    print(f"     Previsão: {alerta.get('previsao', 'N/A')}")
                    print(f"     Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                    print(f"     Status: {alerta.get('status_operacao', 'N/A')}")
                    
                    # Verificar se respondido_em = criado_em
                    if alerta.get('respondido_em') and alerta.get('criado_em'):
                        if alerta['respondido_em'] == alerta['criado_em']:
                            print(f"     ✅ respondido_em = criado_em")
                        else:
                            print(f"     ❌ respondido_em ≠ criado_em")
                    
                    # Verificar se previsão está no passado
                    if alerta.get('previsao_datetime'):
                        try:
                            previsao_dt = datetime.fromisoformat(alerta['previsao_datetime'].replace('Z', '+00:00'))
                            if previsao_dt.tzinfo is None:
                                previsao_dt = pytz.utc.localize(previsao_dt).astimezone(tz_br)
                            else:
                                previsao_dt = previsao_dt.astimezone(tz_br)
                            
                            if previsao_dt < now_br:
                                print(f"     ✅ Previsão no passado (correto para atrasadas): {previsao_dt}")
                            else:
                                print(f"     ❌ Previsão no futuro (problema para atrasadas): {previsao_dt}")
                        except Exception as e:
                            print(f"     ❌ Erro ao processar previsão: {e}")
                    print()
            else:
                print("📋 Nenhum alerta atrasado encontrado")
        else:
            print(f"❌ Erro ao listar alertas: {response4.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar atrasadas: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")
    print("\n📋 RESULTADO ESPERADO:")
    print("1. Alerta criado deve aparecer em 'Pendentes'")
    print("2. Após resposta, deve ir para 'Escaladas' (não 'Atrasadas')")
    print("3. respondido_em deve ser igual ao criado_em")
    print("4. previsao_datetime deve estar no futuro")

if __name__ == "__main__":
    test_categorizacao() 