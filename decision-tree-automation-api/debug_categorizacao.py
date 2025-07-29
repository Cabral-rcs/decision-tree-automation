#!/usr/bin/env python3
"""
Script de debug para entender a categorização de alertas
"""

import requests
import json
from datetime import datetime
import pytz

def debug_categorizacao():
    """Debug da categorização de alertas"""
    print("🔍 DEBUG DA CATEGORIZAÇÃO DE ALERTAS")
    print("=" * 60)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ Verificando horário atual...")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print(f"   Horário atual (UTC): {now_br.utctimetuple()}")
    
    # 2. Listar todos os alertas
    print("\n2️⃣ Listando todos os alertas...")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # Verificar pendentes
            pendentes = data.get('pendentes', [])
            print(f"   📋 Pendentes: {len(pendentes)}")
            for alerta in pendentes:
                print(f"      - ID: {alerta['id']}, Criado: {alerta['criado_em']}")
            
            # Verificar escaladas
            escaladas = data.get('escaladas', [])
            print(f"   📋 Escaladas: {len(escaladas)}")
            for alerta in escaladas:
                print(f"      - ID: {alerta['id']}")
                print(f"        Criado: {alerta['criado_em']}")
                print(f"        Respondido: {alerta.get('respondido_em', 'N/A')}")
                print(f"        Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"        Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                print(f"        Status: {alerta.get('status_operacao', 'N/A')}")
                
                # Verificar se respondido_em = criado_em
                if alerta.get('respondido_em') and alerta.get('criado_em'):
                    if alerta['respondido_em'] == alerta['criado_em']:
                        print(f"        ✅ respondido_em = criado_em")
                    else:
                        print(f"        ❌ respondido_em ≠ criado_em")
                        print(f"           respondido_em: {alerta['respondido_em']}")
                        print(f"           criado_em: {alerta['criado_em']}")
                print()
            
            # Verificar atrasadas
            atrasadas = data.get('atrasadas', [])
            print(f"   📋 Atrasadas: {len(atrasadas)}")
            for alerta in atrasadas:
                print(f"      - ID: {alerta['id']}")
                print(f"        Criado: {alerta['criado_em']}")
                print(f"        Respondido: {alerta.get('respondido_em', 'N/A')}")
                print(f"        Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"        Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                print(f"        Status: {alerta.get('status_operacao', 'N/A')}")
                
                # Verificar se respondido_em = criado_em
                if alerta.get('respondido_em') and alerta.get('criado_em'):
                    if alerta['respondido_em'] == alerta['criado_em']:
                        print(f"        ✅ respondido_em = criado_em")
                    else:
                        print(f"        ❌ respondido_em ≠ criado_em")
                        print(f"           respondido_em: {alerta['respondido_em']}")
                        print(f"           criado_em: {alerta['criado_em']}")
                
                # Verificar se previsão está no passado
                if alerta.get('previsao_datetime'):
                    try:
                        previsao_dt = datetime.fromisoformat(alerta['previsao_datetime'].replace('Z', '+00:00'))
                        if previsao_dt.tzinfo is None:
                            previsao_dt = pytz.utc.localize(previsao_dt).astimezone(tz_br)
                        else:
                            previsao_dt = previsao_dt.astimezone(tz_br)
                        
                        if previsao_dt < now_br:
                            print(f"        ⏰ Previsão no passado: {previsao_dt} < {now_br}")
                        else:
                            print(f"        ⏰ Previsão no futuro: {previsao_dt} > {now_br}")
                    except Exception as e:
                        print(f"        ❌ Erro ao processar previsão: {e}")
                print()
            
            # Verificar encerradas
            encerradas = data.get('encerradas', [])
            print(f"   📋 Encerradas: {len(encerradas)}")
            for alerta in encerradas:
                print(f"      - ID: {alerta['id']}, Criado: {alerta['criado_em']}")
            
        else:
            print(f"❌ Erro ao listar alertas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar alertas: {e}")
    
    # 3. Verificar debug do sistema
    print("\n3️⃣ Verificando debug do sistema...")
    try:
        response = requests.get(f'{base_url}/alertas/debug', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   Total de alertas: {data.get('total_alertas', 0)}")
            print(f"   Alertas com previsão: {data.get('alertas_com_previsao', 0)}")
            print(f"   Alertas pendentes: {data.get('alertas_pendentes', 0)}")
            print(f"   Última atualização: {data.get('ultima_atualizacao', 'N/A')}")
        else:
            print(f"❌ Erro no debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao verificar debug: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 DEBUG CONCLUÍDO")
    print("\n📋 ANÁLISE:")
    print("1. Verifique se o horário atual está correto")
    print("2. Verifique se as previsões estão sendo criadas corretamente")
    print("3. Verifique se respondido_em = criado_em")
    print("4. Verifique se as previsões estão no futuro ou passado")

if __name__ == "__main__":
    debug_categorizacao() 