#!/usr/bin/env python3
"""
Script de debug detalhado para analisar o problema de categorização dos alertas
"""

import requests
import json
from datetime import datetime
import pytz

def debug_categorizacao_detalhado():
    """Debug detalhado da categorização de alertas"""
    print("🔍 DEBUG DETALHADO DA CATEGORIZAÇÃO DE ALERTAS")
    print("=" * 60)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ HORÁRIO ATUAL")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print(f"   Timestamp: {now_br.timestamp()}")
    print()
    
    # 2. Listar todos os alertas com detalhes
    print("2️⃣ TODOS OS ALERTAS NO SISTEMA")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            all_alertas = []
            all_alertas.extend(data.get('pendentes', []))
            all_alertas.extend(data.get('escaladas', []))
            all_alertas.extend(data.get('atrasadas', []))
            all_alertas.extend(data.get('encerradas', []))
            
            print(f"   Total de alertas: {len(all_alertas)}")
            print(f"   - Pendentes: {len(data.get('pendentes', []))}")
            print(f"   - Escaladas: {len(data.get('escaladas', []))}")
            print(f"   - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"   - Encerradas: {len(data.get('encerradas', []))}")
            print()
            
            # Analisar cada alerta em detalhes
            for alerta in all_alertas:
                print(f"   📋 ALERTA ID: {alerta['id']}")
                print(f"      Criado em: {alerta.get('criado_em', 'N/A')}")
                print(f"      Respondido em: {alerta.get('respondido_em', 'N/A')}")
                print(f"      Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                print(f"      Status operação: {alerta.get('status_operacao', 'N/A')}")
                print(f"      Problema: {alerta.get('problema', 'N/A')[:50]}...")
                
                # Analisar previsão datetime
                if alerta.get('previsao_datetime'):
                    try:
                        previsao_str = alerta['previsao_datetime']
                        if 'Z' in previsao_str:
                            previsao_str = previsao_str.replace('Z', '+00:00')
                        
                        previsao_dt = datetime.fromisoformat(previsao_str)
                        
                        # Garantir timezone
                        if previsao_dt.tzinfo is None:
                            previsao_dt = pytz.utc.localize(previsao_dt).astimezone(tz_br)
                        else:
                            previsao_dt = previsao_dt.astimezone(tz_br)
                        
                        print(f"      Previsão processada: {previsao_dt}")
                        print(f"      Previsão timestamp: {previsao_dt.timestamp()}")
                        print(f"      Agora timestamp: {now_br.timestamp()}")
                        print(f"      Diferença (segundos): {previsao_dt.timestamp() - now_br.timestamp()}")
                        
                        if previsao_dt > now_br:
                            print(f"      ✅ Previsão no FUTURO")
                        else:
                            print(f"      ❌ Previsão no PASSADO")
                            
                    except Exception as e:
                        print(f"      ❌ Erro ao processar previsão: {e}")
                
                print()
        else:
            print(f"❌ Erro ao listar alertas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
    
    # 3. Verificar debug do sistema
    print("3️⃣ DEBUG DO SISTEMA")
    try:
        response = requests.get(f'{base_url}/alertas/debug', timeout=30)
        if response.status_code == 200:
            debug_data = response.json()
            print(f"   Total alertas: {debug_data.get('total_alertas', 0)}")
            print(f"   Pendentes: {debug_data.get('pendentes', 0)}")
            print(f"   Com previsão: {debug_data.get('com_previsao', 0)}")
            
            print("   Últimos alertas:")
            for alerta in debug_data.get('ultimos_alertas', []):
                print(f"      ID {alerta['id']}: {alerta['problema']}")
                print(f"         Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"         Previsão DT: {alerta.get('previsao_datetime', 'N/A')}")
                print(f"         Status: {alerta.get('status_operacao', 'N/A')}")
        else:
            print(f"❌ Erro no debug: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 ANÁLISE CONCLUÍDA")
    print("\n📋 POSSÍVEIS CAUSAS DO PROBLEMA:")
    print("1. Campo 'data_operacao' sendo usado incorretamente")
    print("2. Previsão sendo criada no passado")
    print("3. Timezone incorreto na comparação")
    print("4. Campo 'criado_em' com dados fictícios")
    print("5. Lógica de categorização com bug")

if __name__ == "__main__":
    debug_categorizacao_detalhado() 