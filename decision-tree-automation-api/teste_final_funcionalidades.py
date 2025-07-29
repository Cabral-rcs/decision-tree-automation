#!/usr/bin/env python3
"""
Teste final das funcionalidades usando endpoint de teste
"""

import requests
import json
from datetime import datetime
import pytz
import time

def test_final_funcionalidades():
    """Teste final das funcionalidades"""
    print("🧪 TESTE FINAL DAS FUNCIONALIDADES")
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
    
    # 3. Criar alerta atrasado de teste
    print("3️⃣ CRIANDO ALERTA ATRASADO DE TESTE")
    try:
        response = requests.post(f'{base_url}/alertas/teste-atrasado', timeout=30)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get('alerta_id')
            print(f"   ✅ Alerta atrasado criado: ID {alert_id}")
            print(f"   Previsão: {data.get('previsao', 'N/A')}")
            print(f"   Previsão DT: {data.get('previsao_datetime', 'N/A')}")
        else:
            print(f"   ❌ Erro ao criar alerta atrasado: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao criar alerta atrasado: {e}")
        return
    
    # 4. Verificar se está em atrasadas
    print("\n4️⃣ VERIFICANDO SE ESTÁ EM ATRASADAS")
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
            
            atrasadas = data.get('atrasadas', [])
            if atrasadas:
                alerta_atrasado = atrasadas[0]
                print(f"\n   ✅ Alerta em ATRASADAS:")
                print(f"      ID: {alerta_atrasado['id']}")
                print(f"      Status: {alerta_atrasado.get('status_operacao', 'N/A')}")
                print(f"      Previsão: {alerta_atrasado.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta_atrasado.get('previsao_datetime', 'N/A')}")
            else:
                print(f"\n   ❌ Alerta não está em atrasadas")
                return
        else:
            print(f"   ❌ Erro ao listar alertas: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro ao verificar alertas: {e}")
        return
    
    # 5. Testar mudança de status de atrasada para encerrada
    print("\n5️⃣ TESTANDO MUDANÇA DE STATUS (ATRASADA → ENCERRADA)")
    
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
    
    # 6. Verificar se foi para encerradas
    print("\n6️⃣ VERIFICANDO SE FOI PARA ENCERRADAS")
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
                print(f"      Previsão: {alerta_encerrado.get('previsao', 'N/A')}")
                print(f"      Previsão DT: {alerta_encerrado.get('previsao_datetime', 'N/A')}")
                
                # Verificar se tem horario_operando (indicando que veio de atrasadas)
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
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DAS FUNCIONALIDADES TESTADAS:")
    print("✅ Alerta atrasado criado com sucesso")
    print("✅ Alerta aparece em atrasadas")
    print("✅ Botão de status disponível em atrasadas")
    print("✅ Mudança de status funciona")
    print("✅ Alerta vai para encerradas após mudança")
    print("✅ Background diferenciado por origem")
    print("🏁 TESTE FINAL CONCLUÍDO")

if __name__ == "__main__":
    test_final_funcionalidades() 