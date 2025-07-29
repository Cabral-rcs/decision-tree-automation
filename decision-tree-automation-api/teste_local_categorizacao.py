#!/usr/bin/env python3
"""
Teste local da correção de timezone na categorização
"""

from datetime import datetime
import pytz

def test_timezone_correction():
    """Testa a correção de timezone localmente"""
    print("🧪 TESTE LOCAL DA CORREÇÃO DE TIMEZONE")
    print("=" * 50)
    
    # 1. Simular dados do banco
    print("1️⃣ SIMULANDO DADOS DO BANCO")
    tz_br = pytz.timezone('America/Sao_Paulo')
    now_br = datetime.now(tz_br)
    
    # Simular previsão salva no banco (sem timezone)
    previsao_banco = datetime(2025, 7, 29, 15, 30, 0)  # 15:30 sem timezone
    print(f"   Previsão no banco (sem timezone): {previsao_banco}")
    print(f"   Horário atual: {now_br}")
    print()
    
    # 2. Testar lógica ANTIGA (problemática)
    print("2️⃣ LÓGICA ANTIGA (PROBLEMÁTICA)")
    previsao_antiga = pytz.utc.localize(previsao_banco).astimezone(tz_br)
    print(f"   Previsão convertida (UTC->BR): {previsao_antiga}")
    print(f"   Comparação: {previsao_antiga} > {now_br} = {previsao_antiga > now_br}")
    print()
    
    # 3. Testar lógica NOVA (corrigida)
    print("3️⃣ LÓGICA NOVA (CORRIGIDA)")
    previsao_nova = tz_br.localize(previsao_banco)
    print(f"   Previsão convertida (assumindo BR): {previsao_nova}")
    print(f"   Comparação: {previsao_nova} > {now_br} = {previsao_nova > now_br}")
    print()
    
    # 4. Testar criação de previsão no webhook
    print("4️⃣ TESTE DE CRIAÇÃO NO WEBHOOK")
    hora, minuto = 15, 30
    previsao_webhook = now_br.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    print(f"   Previsão criada no webhook: {previsao_webhook}")
    print(f"   Comparação webhook: {previsao_webhook} > {now_br} = {previsao_webhook > now_br}")
    print()
    
    # 5. Conclusão
    print("5️⃣ CONCLUSÃO")
    if previsao_nova > now_br:
        print("   ✅ LÓGICA NOVA FUNCIONA: Previsão no futuro")
    else:
        print("   ❌ LÓGICA NOVA FALHA: Previsão no passado")
    
    if previsao_antiga > now_br:
        print("   ✅ LÓGICA ANTIGA FUNCIONA: Previsão no futuro")
    else:
        print("   ❌ LÓGICA ANTIGA FALHA: Previsão no passado")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE LOCAL CONCLUÍDO")

if __name__ == "__main__":
    test_timezone_correction() 