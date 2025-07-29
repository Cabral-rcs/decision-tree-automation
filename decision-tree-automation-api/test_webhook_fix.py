#!/usr/bin/env python3
"""
Script de teste para verificar o modelo chave-valor dos alertas
Testa o vínculo entre alertas e previsões
"""

import requests
import json
import time
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"

def test_alert_creation():
    """Testa a criação de um alerta"""
    try:
        alert_data = {
            "problema": "Teste modelo chave-valor - Equipamento apresentando baixa eficiência",
            "codigo": "TEST001",
            "unidade": "Unidade Teste",
            "frente": "Frente de Teste",
            "equipamento": "Equipamento Teste",
            "tipo_operacao": "Teste",
            "operacao": "Operação de Teste",
            "nome_operador": "Operador Teste"
        }
        
        response = requests.post(f"{BASE_URL}/alertas", json=alert_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alerta criado com sucesso - ID: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Erro ao criar alerta: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao testar criação de alerta: {e}")
        return None

def test_alert_categorization():
    """Testa a categorização dos alertas"""
    try:
        response = requests.get(f"{BASE_URL}/alertas")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorização funcionando:")
            print(f"   - Pendentes: {len(data.get('pendentes', []))}")
            print(f"   - Escaladas: {len(data.get('escaladas', []))}")
            print(f"   - Atrasadas: {len(data.get('atrasadas', []))}")
            print(f"   - Encerradas: {len(data.get('encerradas', []))}")
            
            # Verifica se pendentes não têm previsão
            if data.get('pendentes'):
                pendente = data['pendentes'][0]
                if 'previsao' in pendente and pendente['previsao'] is None:
                    print("✅ Pendentes sem previsão (correto)")
                else:
                    print("⚠️  Pendentes com previsão (incorreto)")
            
            # Verifica se escaladas têm previsão
            if data.get('escaladas'):
                escalada = data['escaladas'][0]
                if 'previsao' in escalada and escalada['previsao']:
                    print("✅ Escaladas com previsão (correto)")
                else:
                    print("⚠️  Escaladas sem previsão (incorreto)")
            
            return True
        else:
            print(f"❌ Erro ao testar categorização: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar categorização: {e}")
        return False

def test_debug_endpoint():
    """Testa o endpoint de debug"""
    try:
        response = requests.get(f"{BASE_URL}/alertas/debug")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug funcionando:")
            print(f"   - Total de alertas: {data.get('total_alertas', 0)}")
            print(f"   - Pendentes: {data.get('pendentes', 0)}")
            print(f"   - Com previsão: {data.get('com_previsao', 0)}")
            
            # Verifica últimos alertas
            if data.get('ultimos_alertas'):
                for alerta in data['ultimos_alertas'][:3]:
                    print(f"   - Alerta {alerta['id']}: previsão = {alerta.get('previsao', 'None')}")
            
            return True
        else:
            print(f"❌ Erro no debug: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar debug: {e}")
        return False

def simulate_webhook_response(alert_id):
    """Simula uma resposta do webhook"""
    try:
        # Simula dados de webhook do Telegram
        webhook_data = {
            "message": {
                "from": {
                    "id": 6435800936,
                    "first_name": "Rafael",
                    "last_name": "Cabral"
                },
                "text": "15:30",
                "date": int(datetime.now().timestamp())
            }
        }
        
        response = requests.post(f"{BASE_URL}/webhook/telegram", json=webhook_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook simulado: {data.get('status')}")
            if data.get('alerta_id'):
                print(f"✅ Alerta ID associado: {data.get('alerta_id')}")
            return data.get('status') == 'success'
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao simular webhook: {e}")
        return False

def verify_alert_movement(alert_id):
    """Verifica se o alerta mudou de categoria"""
    try:
        response = requests.get(f"{BASE_URL}/alertas")
        if response.status_code == 200:
            data = response.json()
            
            # Procura o alerta nas categorias
            alerta_encontrado = None
            categoria = None
            
            # Procura em pendentes
            for a in data.get('pendentes', []):
                if a['id'] == alert_id:
                    alerta_encontrado = a
                    categoria = 'pendentes'
                    break
            
            # Se não encontrou em pendentes, procura em escaladas
            if not alerta_encontrado:
                for a in data.get('escaladas', []):
                    if a['id'] == alert_id:
                        alerta_encontrado = a
                        categoria = 'escaladas'
                        break
            
            if alerta_encontrado:
                print(f"✅ Alerta {alert_id} encontrado na categoria: {categoria}")
                if categoria == 'escaladas':
                    previsao = alerta_encontrado.get('previsao')
                    print(f"✅ Previsão registrada: {previsao}")
                    print("✅ Modelo chave-valor funcionando corretamente!")
                    return True
                else:
                    print("⚠️  Alerta ainda na categoria pendentes")
                    return False
            else:
                print("❌ Alerta não encontrado")
                return False
        else:
            print(f"❌ Erro ao verificar alertas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar movimento do alerta: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DO MODELO CHAVE-VALOR")
    print("=" * 50)
    
    # Teste 1: Backend
    print("\n1. Testando backend...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend não está funcionando. Aborte os testes.")
            return
        print("✅ Backend funcionando")
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return
    
    # Teste 2: Categorização atual
    print("\n2. Testando categorização atual...")
    test_alert_categorization()
    
    # Teste 3: Debug
    print("\n3. Testando endpoint de debug...")
    test_debug_endpoint()
    
    # Teste 4: Criação de alerta
    print("\n4. Criando alerta de teste...")
    alert_id = test_alert_creation()
    
    if alert_id:
        print(f"\n✅ Alerta criado com ID: {alert_id}")
        
        # Verifica se está em pendentes
        print("\n5. Verificando se alerta está em pendentes...")
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/alertas")
        if response.status_code == 200:
            data = response.json()
            pendentes = data.get('pendentes', [])
            alerta_pendente = next((a for a in pendentes if a['id'] == alert_id), None)
            if alerta_pendente:
                print("✅ Alerta está em pendentes (correto)")
                print(f"   - Previsão: {alerta_pendente.get('previsao', 'None')}")
            else:
                print("❌ Alerta não está em pendentes")
        
        # Teste 6: Simular resposta do webhook
        print("\n6. Simulando resposta do webhook...")
        if simulate_webhook_response(alert_id):
            print("✅ Webhook funcionando corretamente")
            
            # Aguarda um pouco e verifica se o alerta mudou de categoria
            print("\n7. Verificando mudança de categoria...")
            time.sleep(2)
            
            if verify_alert_movement(alert_id):
                print("✅ Teste do modelo chave-valor APROVADO!")
            else:
                print("❌ Falha no modelo chave-valor")
        else:
            print("❌ Webhook não funcionou")
    
    print("\n" + "=" * 50)
    print("🏁 TESTES CONCLUÍDOS")
    print("\n📋 RESULTADO ESPERADO:")
    print("1. Alerta criado → aparece em 'Pendentes' com previsão vazia")
    print("2. Resposta do líder → preenche chave 'Previsão' do alerta específico")
    print("3. Alerta move de 'Pendentes' para 'Escaladas'")
    print("4. Previsão aparece como valor na coluna 'Previsão'")

if __name__ == "__main__":
    main() 