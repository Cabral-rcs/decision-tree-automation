#!/usr/bin/env python3
"""
Script de teste para verificar as correções do webhook
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
            "problema": "Teste de vínculo previsão - Equipamento apresentando baixa eficiência",
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
            
            # Verifica se não há coluna "prazo" nas categorias
            if data.get('pendentes'):
                pendente = data['pendentes'][0]
                if 'prazo' in pendente:
                    print("⚠️  Coluna 'prazo' ainda presente em pendentes")
                else:
                    print("✅ Coluna 'prazo' removida de pendentes")
            
            if data.get('escaladas'):
                escalada = data['escaladas'][0]
                if 'prazo' in escalada:
                    print("⚠️  Coluna 'prazo' ainda presente em escaladas")
                else:
                    print("✅ Coluna 'prazo' removida de escaladas")
            
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
            return data.get('status') == 'success'
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao simular webhook: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DAS CORREÇÕES DO WEBHOOK")
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
        
        # Teste 5: Simular resposta do webhook
        print("\n5. Simulando resposta do webhook...")
        if simulate_webhook_response(alert_id):
            print("✅ Webhook funcionando corretamente")
            
            # Aguarda um pouco e verifica se o alerta mudou de categoria
            print("\n6. Verificando mudança de categoria...")
            time.sleep(2)
            
            response = requests.get(f"{BASE_URL}/alertas")
            if response.status_code == 200:
                data = response.json()
                pendentes = data.get('pendentes', [])
                escaladas = data.get('escaladas', [])
                
                # Procura o alerta nas categorias
                alerta_encontrado = None
                categoria = None
                
                for a in pendentes:
                    if a['id'] == alert_id:
                        alerta_encontrado = a
                        categoria = 'pendentes'
                        break
                
                if not alerta_encontrado:
                    for a in escaladas:
                        if a['id'] == alert_id:
                            alerta_encontrado = a
                            categoria = 'escaladas'
                            break
                
                if alerta_encontrado:
                    print(f"✅ Alerta encontrado na categoria: {categoria}")
                    if categoria == 'escaladas':
                        print(f"✅ Previsão registrada: {alerta_encontrado.get('previsao')}")
                        print("✅ Vínculo entre alerta e previsão funcionando!")
                    else:
                        print("⚠️  Alerta ainda na categoria pendentes")
                else:
                    print("❌ Alerta não encontrado")
        else:
            print("❌ Webhook não funcionou")
    
    print("\n" + "=" * 50)
    print("🏁 TESTES CONCLUÍDOS")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Verifique se o alerta aparece na categoria 'Escalada'")
    print("2. Confirme que a coluna 'Prazo' foi removida")
    print("3. Verifique se a 'Previsão' está sendo exibida corretamente")
    print("4. Teste responder no Telegram com formato HH:MM")

if __name__ == "__main__":
    main() 