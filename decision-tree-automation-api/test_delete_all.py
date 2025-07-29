#!/usr/bin/env python3
"""
Script de teste para verificar o endpoint de apagar todos os alertas
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Testa se o backend está funcionando"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend está funcionando")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return False

def create_test_alerts():
    """Cria alguns alertas de teste"""
    alertas_criados = []
    
    for i in range(3):
        alert_data = {
            "problema": f"Alerta de teste {i+1} - Equipamento apresentando problemas",
            "codigo": f"TEST{i+1:03d}",
            "unidade": f"Unidade Teste {i+1}",
            "frente": "Frente de Teste",
            "equipamento": f"Equipamento Teste {i+1}",
            "tipo_operacao": "Teste",
            "operacao": f"Operação de Teste {i+1}",
            "nome_operador": "Operador Teste"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/alertas", json=alert_data)
            if response.status_code == 200:
                data = response.json()
                alertas_criados.append(data.get('id'))
                print(f"✅ Alerta {i+1} criado - ID: {data.get('id')}")
            else:
                print(f"❌ Erro ao criar alerta {i+1}: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao criar alerta {i+1}: {e}")
    
    return alertas_criados

def count_alertas():
    """Conta quantos alertas existem no sistema"""
    try:
        response = requests.get(f"{BASE_URL}/alertas")
        if response.status_code == 200:
            data = response.json()
            total = (len(data.get('pendentes', [])) + 
                    len(data.get('escaladas', [])) + 
                    len(data.get('atrasadas', [])) + 
                    len(data.get('encerradas', [])))
            return total
        else:
            print(f"❌ Erro ao contar alertas: {response.status_code}")
            return 0
    except Exception as e:
        print(f"❌ Erro ao contar alertas: {e}")
        return 0

def test_delete_all_alertas():
    """Testa o endpoint de apagar todos os alertas"""
    try:
        print("🗑️  Testando apagar todos os alertas...")
        response = requests.delete(f"{BASE_URL}/alertas/all")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Todos os alertas foram apagados com sucesso!")
                print(f"   - Alertas apagados: {data.get('alertas_apagados', 0)}")
                print(f"   - Mensagem: {data.get('message', '')}")
                return True
            else:
                print(f"❌ Erro na resposta: {data.get('message', 'Erro desconhecido')}")
                return False
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DO ENDPOINT APAGAR TODOS OS ALERTAS")
    print("=" * 60)
    
    # Teste 1: Backend
    print("\n1. Testando backend...")
    if not test_backend_health():
        print("❌ Backend não está funcionando. Aborte os testes.")
        return
    
    # Teste 2: Contar alertas iniciais
    print("\n2. Contando alertas iniciais...")
    alertas_iniciais = count_alertas()
    print(f"   - Alertas iniciais: {alertas_iniciais}")
    
    # Teste 3: Criar alertas de teste
    print("\n3. Criando alertas de teste...")
    alertas_criados = create_test_alerts()
    print(f"   - Alertas criados: {len(alertas_criados)}")
    
    # Teste 4: Verificar alertas após criação
    print("\n4. Verificando alertas após criação...")
    alertas_apos_criacao = count_alertas()
    print(f"   - Alertas após criação: {alertas_apos_criacao}")
    
    if alertas_apos_criacao == 0:
        print("⚠️  Nenhum alerta encontrado após criação. Teste pode não funcionar corretamente.")
    
    # Teste 5: Apagar todos os alertas
    print("\n5. Testando apagar todos os alertas...")
    if test_delete_all_alertas():
        print("✅ Endpoint funcionando corretamente!")
    else:
        print("❌ Endpoint falhou!")
        return
    
    # Teste 6: Verificar se todos foram apagados
    print("\n6. Verificando se todos os alertas foram apagados...")
    alertas_finais = count_alertas()
    print(f"   - Alertas finais: {alertas_finais}")
    
    if alertas_finais == 0:
        print("✅ Todos os alertas foram apagados com sucesso!")
    else:
        print(f"⚠️  Ainda existem {alertas_finais} alertas no sistema")
    
    print("\n" + "=" * 60)
    print("🏁 TESTES CONCLUÍDOS")
    print("\n📋 RESUMO:")
    print(f"   - Alertas iniciais: {alertas_iniciais}")
    print(f"   - Alertas criados: {len(alertas_criados)}")
    print(f"   - Alertas finais: {alertas_finais}")
    print(f"   - Total apagados: {alertas_apos_criacao - alertas_finais}")

if __name__ == "__main__":
    main() 