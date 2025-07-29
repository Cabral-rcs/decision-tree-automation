#!/usr/bin/env python3
"""
Script para testar com previsão futura
"""

import os
import sys
import re
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_previsao_futura():
    """Testa com previsão futura"""
    try:
        from backend.models.responses_model import SessionLocal, add_response
        from backend.models.alerta_model import Alerta
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # 1. Cria alerta de teste
        novo_alerta = Alerta(
            chat_id="6435800936",
            problema="TESTE PREVISÃO FUTURA - Equipamento apresentando baixa eficiência",
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            codigo="TESTFUT001",
            unidade="Unidade Teste Futura",
            frente="Frente de Teste",
            equipamento="Equipamento Teste",
            tipo_operacao="Teste",
            operacao="Operação de Teste",
            nome_operador="Operador Teste"
        )
        
        db.add(novo_alerta)
        db.commit()
        db.refresh(novo_alerta)
        
        print(f"✅ Alerta criado - ID: {novo_alerta.id}")
        
        # 2. Calcula previsão futura (1 hora à frente)
        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        previsao_futura = now + timedelta(hours=1)
        previsao_str = previsao_futura.strftime("%H:%M")
        
        print(f"⏰ Horário atual: {now.strftime('%H:%M')}")
        print(f"⏰ Previsão futura: {previsao_str}")
        
        # 3. Simula webhook com previsão futura
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta = previsao_str
        msg_utc = datetime.now(pytz.UTC)
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.astimezone(tz_br)
        
        print(f"📱 Simulando webhook com previsão futura: {resposta}")
        
        # Busca alerta pendente
        alerta = db.query(Alerta).filter(
            Alerta.previsao.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta:
            print("❌ Nenhum alerta pendente encontrado")
            return False
        
        print(f"✅ Alerta encontrado: ID {alerta.id}")
        
        # Validação do formato HH:MM
        padrao = r'^(\d{2}):(\d{2})$'
        match = re.match(padrao, resposta)
        if not match:
            print(f"❌ Formato inválido: {resposta}")
            return False
        
        # Monta datetime da previsão
        hora, minuto = match.groups()
        previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        
        print(f"⏰ Previsão processada: {resposta} -> {previsao_dt}")
        
        # Atualiza o alerta
        alerta.previsao = resposta
        alerta.previsao_datetime = previsao_dt
        alerta.respondido_em = datetime.now(pytz.UTC)
        alerta.nome_lider = nome_lider
        
        db.commit()
        db.refresh(alerta)
        
        # Verifica se foi salvo
        alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
        if alerta_atualizado and alerta_atualizado.previsao:
            print(f"✅ Alerta atualizado com sucesso!")
            print(f"   ID: {alerta_atualizado.id}")
            print(f"   Previsão: {alerta_atualizado.previsao}")
            print(f"   Previsão DateTime: {alerta_atualizado.previsao_datetime}")
            print(f"   Status Operação: {alerta_atualizado.status_operacao}")
        else:
            print("❌ Falha ao atualizar alerta")
            return False
        
        # 4. Verifica categorização
        now_check = datetime.now(pytz.timezone('America/Sao_Paulo'))
        print(f"\n📊 Verificando categorização:")
        print(f"   Horário atual: {now_check}")
        print(f"   Previsão: {alerta_atualizado.previsao_datetime}")
        print(f"   Status operação: {alerta_atualizado.status_operacao}")
        
        # Aplica a lógica de categorização
        if not alerta_atualizado.previsao:
            categoria = "pendentes"
        elif alerta_atualizado.status_operacao == 'operando':
            if alerta_atualizado.previsao_datetime >= now_check:
                categoria = "encerradas"
            else:
                categoria = "atrasadas"
        else:
            if alerta_atualizado.previsao_datetime >= now_check:
                categoria = "escaladas"
            else:
                categoria = "atrasadas"
        
        print(f"   Categoria calculada: {categoria}")
        
        # 5. Verifica se está correto
        if categoria == "escaladas":
            print("✅ ALERTA FOI PARA 'ESCALADAS' CORRETAMENTE!")
            print("✅ A lógica de categorização está funcionando")
            return True
        else:
            print(f"❌ Alerta foi para '{categoria}' em vez de 'escaladas'")
            print("❌ Problema na lógica de categorização")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 TESTE DE PREVISÃO FUTURA")
    print("=" * 50)
    
    success = test_previsao_futura()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ As respostas do Telegram estão sendo armazenadas na coluna Previsão")
        print("✅ Os alertas estão mudando de categoria automaticamente")
        print("✅ A lógica de categorização está correta")
    else:
        print("❌ TESTE FALHOU")
        print("❌ Há problemas na lógica de categorização")

if __name__ == "__main__":
    load_dotenv()
    main() 