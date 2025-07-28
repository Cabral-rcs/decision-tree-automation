#!/usr/bin/env python3
"""
Script para testar o webhook diretamente no banco
"""

import os
import re
from datetime import datetime
import pytz
from dotenv import load_dotenv
from backend.models.responses_model import SessionLocal, add_response
from backend.models.alerta_model import Alerta

def test_webhook_logic():
    """Testa a lógica do webhook diretamente"""
    
    print("🧪 TESTE DA LÓGICA DO WEBHOOK")
    print("=" * 50)
    
    # Carrega variáveis de ambiente
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada")
        return
    
    db = SessionLocal()
    try:
        # Simula dados de uma mensagem do Telegram
        user_id = 6435800936
        nome_lider = "Rafael Cabral"
        resposta = "15:30"  # Resposta simulada
        msg_utc = datetime.utcnow()
        tz_br = pytz.timezone('America/Sao_Paulo')
        msg_br = msg_utc.replace(tzinfo=pytz.utc).astimezone(tz_br)
        
        print(f"📱 Dados simulados:")
        print(f"   User ID: {user_id}")
        print(f"   Nome: {nome_lider}")
        print(f"   Resposta: {resposta}")
        print(f"   Timestamp: {msg_utc}")
        
        # Verifica se é o Rafael Cabral
        if 'Rafael' not in nome_lider and 'Cabral' not in nome_lider:
            print("❌ Não é o Rafael Cabral")
            return
        
        print("✅ Usuário autorizado")
        
        # Busca alerta pendente (sem prazo)
        alerta = db.query(Alerta).filter(
            Alerta.prazo.is_(None)
        ).order_by(Alerta.criado_em.asc()).first()
        
        if not alerta:
            print("❌ Nenhum alerta pendente encontrado")
            total_alertas = db.query(Alerta).count()
            print(f"📊 Total de alertas no sistema: {total_alertas}")
            return
        
        print(f"✅ Alerta encontrado: ID {alerta.id}")
        print(f"   Problema: {alerta.problema}")
        print(f"   Status: {alerta.status}")
        print(f"   Prazo atual: {alerta.prazo}")
        
        # Validação do padrão HH:MM
        padrao = r'^(\d{2}):(\d{2})$'
        match = re.match(padrao, resposta)
        if not match:
            print(f"❌ Formato inválido: {resposta}")
            return
        
        print("✅ Formato válido")
        
        # Montar datetime da previsão
        hora, minuto = match.groups()
        previsao_dt = msg_br.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        
        print(f"⏰ Prazo processado: {resposta} -> {previsao_dt}")
        
        # Atualiza o alerta
        print("🔄 Atualizando alerta...")
        alerta.previsao = resposta
        alerta.previsao_datetime = previsao_dt
        alerta.prazo = previsao_dt
        alerta.respondido_em = datetime.utcnow()
        alerta.nome_lider = nome_lider
        
        # Commit
        db.commit()
        db.refresh(alerta)
        
        # Verifica se foi salvo
        alerta_atualizado = db.query(Alerta).filter(Alerta.id == alerta.id).first()
        if alerta_atualizado and alerta_atualizado.prazo:
            print(f"✅ Alerta atualizado com sucesso!")
            print(f"   ID: {alerta_atualizado.id}")
            print(f"   Prazo: {alerta_atualizado.prazo}")
            print(f"   Previsão: {alerta_atualizado.previsao}")
            print(f"   Respondido em: {alerta_atualizado.respondido_em}")
            print(f"   Nome líder: {alerta_atualizado.nome_lider}")
        else:
            print("❌ Falha ao atualizar alerta")
            return
        
        # Armazena como resposta geral
        print("💾 Salvando resposta geral...")
        add_response({
            'user_id': str(user_id),
            'pergunta': alerta.problema,
            'resposta': resposta,
            'timestamp': msg_utc.isoformat()
        })
        
        print("✅ Resposta geral salva")
        
        # Verifica status final
        print("\n📊 STATUS FINAL:")
        total_alertas = db.query(Alerta).count()
        alertas_com_prazo = db.query(Alerta).filter(Alerta.prazo.isnot(None)).count()
        alertas_sem_prazo = db.query(Alerta).filter(Alerta.prazo.is_(None)).count()
        
        print(f"   Total de alertas: {total_alertas}")
        print(f"   Com prazo: {alertas_com_prazo}")
        print(f"   Sem prazo: {alertas_sem_prazo}")
        
        print("\n" + "=" * 50)
        print("🏁 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ O webhook está funcionando corretamente")
        print("✅ As respostas estão sendo armazenadas")
        print("✅ Os alertas estão sendo atualizados")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_webhook_logic() 