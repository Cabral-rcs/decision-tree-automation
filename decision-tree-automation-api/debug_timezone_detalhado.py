#!/usr/bin/env python3
"""
Script de debug específico para analisar o problema de timezone
"""

import requests
import json
from datetime import datetime
import pytz

def debug_timezone_detalhado():
    """Debug detalhado do problema de timezone"""
    print("🔍 DEBUG DETALHADO DO TIMEZONE")
    print("=" * 50)
    
    base_url = "https://decision-tree-automation-1.onrender.com"
    
    # 1. Verificar horário atual
    print("1️⃣ HORÁRIO ATUAL")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    print(f"   Horário atual (BR): {now_br}")
    print(f"   Timestamp: {now_br.timestamp()}")
    print()
    
    # 2. Listar alertas e analisar timezone
    print("2️⃣ ANÁLISE DE TIMEZONE DOS ALERTAS")
    try:
        response = requests.get(f'{base_url}/alertas', timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            all_alertas = []
            all_alertas.extend(data.get('pendentes', []))
            all_alertas.extend(data.get('escaladas', []))
            all_alertas.extend(data.get('atrasadas', []))
            all_alertas.extend(data.get('encerradas', []))
            
            for alerta in all_alertas:
                print(f"   📋 ALERTA ID: {alerta['id']}")
                print(f"      Previsão: {alerta.get('previsao', 'N/A')}")
                print(f"      Previsão DT (raw): {alerta.get('previsao_datetime', 'N/A')}")
                
                if alerta.get('previsao_datetime'):
                    try:
                        previsao_str = alerta['previsao_datetime']
                        print(f"      String original: {previsao_str}")
                        
                        # Teste 1: Parse direto
                        previsao_dt1 = datetime.fromisoformat(previsao_str.replace('Z', '+00:00'))
                        print(f"      Parse direto: {previsao_dt1}")
                        print(f"      Timezone info: {previsao_dt1.tzinfo}")
                        
                        # Teste 2: Conversão para Brasília
                        if previsao_dt1.tzinfo is None:
                            previsao_dt2 = pytz.utc.localize(previsao_dt1).astimezone(tz_br)
                            print(f"      Convertido (UTC->BR): {previsao_dt2}")
                        else:
                            previsao_dt2 = previsao_dt1.astimezone(tz_br)
                            print(f"      Convertido (BR): {previsao_dt2}")
                        
                        # Teste 3: Comparação
                        print(f"      Comparação com agora: {previsao_dt2} > {now_br} = {previsao_dt2 > now_br}")
                        print(f"      Diferença (segundos): {previsao_dt2.timestamp() - now_br.timestamp()}")
                        
                        # Teste 4: Recriar a previsão como o webhook faz
                        hora, minuto = alerta.get('previsao', '00:00').split(':')
                        previsao_recriada = now_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
                        print(f"      Previsão recriada: {previsao_recriada}")
                        print(f"      Comparação recriada: {previsao_recriada} > {now_br} = {previsao_recriada > now_br}")
                        
                    except Exception as e:
                        print(f"      ❌ Erro ao processar: {e}")
                
                print()
        else:
            print(f"❌ Erro ao listar alertas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
    
    # 3. Teste de criação de previsão
    print("3️⃣ TESTE DE CRIAÇÃO DE PREVISÃO")
    hora_teste = 15
    minuto_teste = 30
    
    # Teste 1: Como o webhook faz
    previsao_webhook = now_br.replace(hour=hora_teste, minute=minuto_teste, second=0, microsecond=0)
    print(f"   Previsão webhook: {previsao_webhook}")
    print(f"   Comparação webhook: {previsao_webhook} > {now_br} = {previsao_webhook > now_br}")
    
    # Teste 2: Como deveria ser
    from datetime import timedelta
    if previsao_webhook <= now_br:
        previsao_ajustada = previsao_webhook + timedelta(days=1)
        print(f"   Previsão ajustada: {previsao_ajustada}")
        print(f"   Comparação ajustada: {previsao_ajustada} > {now_br} = {previsao_ajustada > now_br}")
    
    print("\n" + "=" * 50)
    print("🏁 ANÁLISE CONCLUÍDA")

if __name__ == "__main__":
    debug_timezone_detalhado() 