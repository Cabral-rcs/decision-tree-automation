#!/usr/bin/env python3
"""
Script para testar o sistema completo de alertas automáticos
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_complete_system():
    """Testa o sistema completo"""
    
    print("=== Teste Completo do Sistema ===\n")
    
    try:
        # 1. Testa se o servidor está rodando
        print("1. Testando conexão com servidor...")
        resp = requests.get(f"{BASE_URL}/")
        if resp.status_code == 200:
            print("   ✅ Servidor está rodando")
        else:
            print(f"   ❌ Servidor retornou status {resp.status_code}")
            return False
        
        # 2. Testa status dos alertas automáticos
        print("\n2. Testando status dos alertas automáticos...")
        resp = requests.get(f"{BASE_URL}/auto-alert/status")
        if resp.status_code == 200:
            status = resp.json()
            print(f"   ✅ Status: {status}")
        else:
            print(f"   ❌ Erro ao obter status: {resp.status_code}")
            return False
        
        # 3. Testa criação de alerta manual
        print("\n3. Testando criação de alerta manual...")
        resp = requests.post(f"{BASE_URL}/auto-alert/create-now")
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✅ Alerta criado: {result}")
        else:
            print(f"   ❌ Erro ao criar alerta: {resp.status_code}")
            return False
        
        # 4. Testa ativação dos alertas automáticos
        print("\n4. Testando ativação dos alertas automáticos...")
        resp = requests.post(f"{BASE_URL}/auto-alert/toggle")
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✅ Status alterado: {result}")
        else:
            print(f"   ❌ Erro ao alterar status: {resp.status_code}")
            return False
        
        # 5. Testa atualização de intervalo
        print("\n5. Testando atualização de intervalo...")
        resp = requests.post(f"{BASE_URL}/auto-alert/update-interval?interval_minutes=5")
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✅ Intervalo atualizado: {result}")
        else:
            print(f"   ❌ Erro ao atualizar intervalo: {resp.status_code}")
            return False
        
        # 6. Testa listagem de alertas
        print("\n6. Testando listagem de alertas...")
        resp = requests.get(f"{BASE_URL}/alertas")
        if resp.status_code == 200:
            alertas = resp.json()
            print(f"   ✅ Alertas encontrados:")
            print(f"      - Pendentes: {len(alertas.get('pendentes', []))}")
            print(f"      - Escaladas: {len(alertas.get('escaladas', []))}")
            print(f"      - Atrasadas: {len(alertas.get('atrasadas', []))}")
            print(f"      - Encerradas: {len(alertas.get('encerradas', []))}")
            
            # Verifica se há alertas com os novos campos
            if alertas.get('pendentes'):
                primeiro_alerta = alertas['pendentes'][0]
                campos_esperados = ['codigo', 'unidade', 'frente', 'equipamento', 'tipo_operacao', 'operacao', 'nome_operador', 'data_operacao', 'tempo_abertura', 'tipo_arvore', 'justificativa', 'prazo']
                campos_presentes = [campo for campo in campos_esperados if campo in primeiro_alerta]
                print(f"   ✅ Novos campos presentes: {len(campos_presentes)}/{len(campos_esperados)}")
                if len(campos_presentes) == len(campos_esperados):
                    print("   ✅ Todos os novos campos estão presentes!")
                else:
                    print(f"   ⚠️  Campos faltando: {set(campos_esperados) - set(campos_presentes)}")
        else:
            print(f"   ❌ Erro ao listar alertas: {resp.status_code}")
            return False
        
        # 7. Testa listagem de líderes
        print("\n7. Testando listagem de líderes...")
        resp = requests.get(f"{BASE_URL}/lideres")
        if resp.status_code == 200:
            lideres = resp.json()
            print(f"   ✅ Líderes encontrados: {len(lideres)}")
            if lideres:
                print(f"   ✅ Rafael Cabral presente: {'Rafael Cabral' in [l['nome_lider'] for l in lideres]}")
        else:
            print(f"   ❌ Erro ao listar líderes: {resp.status_code}")
            return False
        
        # 8. Aguarda um pouco e testa novamente
        print("\n8. Aguardando 10 segundos para verificar criação automática...")
        time.sleep(10)
        
        resp = requests.get(f"{BASE_URL}/alertas")
        if resp.status_code == 200:
            alertas_apos = resp.json()
            total_antes = len(alertas.get('pendentes', [])) + len(alertas.get('escaladas', [])) + len(alertas.get('atrasadas', [])) + len(alertas.get('encerradas', []))
            total_apos = len(alertas_apos.get('pendentes', [])) + len(alertas_apos.get('escaladas', [])) + len(alertas_apos.get('atrasadas', [])) + len(alertas_apos.get('encerradas', []))
            print(f"   ✅ Total de alertas: {total_antes} → {total_apos}")
            if total_apos > total_antes:
                print("   ✅ Novos alertas foram criados automaticamente!")
            else:
                print("   ⚠️  Nenhum novo alerta foi criado (pode ser normal se o intervalo for maior)")
        
        print("\n=== Teste Completo Concluído com Sucesso! ===")
        print("\nPróximos passos:")
        print("1. Abra o frontend: decision-tree-automation-ui/index.html")
        print("2. Vá para a aba 'Alertas Automáticos'")
        print("3. Use os controles para gerenciar os alertas automáticos")
        print("4. Verifique as tabelas com todos os novos campos")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que o servidor está rodando:")
        print("   uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    test_complete_system() 