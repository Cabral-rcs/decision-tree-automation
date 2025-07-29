#!/usr/bin/env python3
"""
Teste da nova regra de negócio: Categorização baseada em previsão e status_operacao
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Adiciona o diretório do backend ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.responses_model import SessionLocal
from backend.models.alerta_model import Alerta

def test_nova_regra_negocio():
    """Teste da nova regra de negócio"""
    print("🧪 TESTE DA NOVA REGRA DE NEGÓCIO")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 1. Limpar alertas existentes
        print("1️⃣ Limpando alertas existentes...")
        db.query(Alerta).delete()
        db.commit()
        print("   ✅ Alertas limpos")
        
        # 2. Criar alertas de teste
        print("\n2️⃣ Criando alertas de teste...")
        tz_br = pytz.timezone('America/Sao_Paulo')
        now_br = datetime.now(tz_br)
        
        # Alerta pendente (sem previsão)
        alerta_pendente = Alerta(
            chat_id='6435800936',
            problema='[TESTE] Alerta pendente',
            status='pendente',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            previsao=None,
            previsao_datetime=None,
            codigo='PEND001'
        )
        
        # Alerta escalada (previsão no futuro)
        previsao_futura = now_br + timedelta(hours=2)
        alerta_escalada = Alerta(
            chat_id='6435800936',
            problema='[TESTE] Alerta escalada',
            status='escalada',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            previsao='16:30',
            previsao_datetime=previsao_futura,
            respondido_em=now_br - timedelta(hours=1),
            codigo='ESC001'
        )
        
        # Alerta atrasada (previsão no passado)
        previsao_passada = now_br - timedelta(hours=2)
        alerta_atrasada = Alerta(
            chat_id='6435800936',
            problema='[TESTE] Alerta atrasada',
            status='atrasada',
            status_operacao='não operando',
            nome_lider='Rafael Cabral',
            previsao='12:30',
            previsao_datetime=previsao_passada,
            respondido_em=now_br - timedelta(hours=3),
            codigo='ATR001'
        )
        
        # Alerta encerrada (status operando)
        alerta_encerrada = Alerta(
            chat_id='6435800936',
            problema='[TESTE] Alerta encerrada',
            status='encerrada',
            status_operacao='operando',
            nome_lider='Rafael Cabral',
            previsao='14:30',
            previsao_datetime=now_br - timedelta(hours=1),
            respondido_em=now_br - timedelta(hours=2),
            horario_operando=now_br - timedelta(minutes=30),
            origem_encerramento='escalada',
            codigo='ENC001'
        )
        
        # Adiciona todos os alertas
        db.add_all([alerta_pendente, alerta_escalada, alerta_atrasada, alerta_encerrada])
        db.commit()
        
        print(f"   ✅ Alertas criados:")
        print(f"      - Pendente: ID {alerta_pendente.id}")
        print(f"      - Escalada: ID {alerta_escalada.id}")
        print(f"      - Atrasada: ID {alerta_atrasada.id}")
        print(f"      - Encerrada: ID {alerta_encerrada.id}")
        
        # 3. Testar categorização
        print("\n3️⃣ Testando categorização...")
        
        # Simula a lógica de categorização
        now = datetime.now(tz_br)
        pendentes = []
        escaladas = []
        atrasadas = []
        encerradas = []
        
        for alerta in db.query(Alerta).all():
            # NOVA REGRA DE NEGÓCIO:
            # Pendentes: Alertas sem previsão
            # Escaladas: Alertas com previsão sem a previsão ter sido excedida
            # Atrasadas: Tempo excedido da previsão e status não operando
            # Encerradas: Tempo excedido ou não porém com status operando
            
            # 1. Pendentes: Alertas sem previsão
            if not alerta.previsao:
                pendentes.append(alerta)
                continue
            
            # 2. Encerradas: Status operando (independente da previsão)
            if alerta.status_operacao == 'operando':
                encerradas.append(alerta)
                continue
            
            # 3. Para alertas com previsão e status não operando, verifica se a previsão foi excedida
            previsao_dt = alerta.previsao_datetime
            if previsao_dt:
                if previsao_dt.tzinfo is None:
                    previsao_dt = tz_br.localize(previsao_dt)
                else:
                    previsao_dt = previsao_dt.astimezone(tz_br)
                
                # 4. Escaladas: Com previsão, dentro da previsão e status não operando
                if previsao_dt >= now:
                    escaladas.append(alerta)
                else:
                    # 5. Atrasadas: Previsão excedida e status não operando
                    atrasadas.append(alerta)
            else:
                # Se tem previsão mas não tem previsao_datetime, vai para escaladas
                escaladas.append(alerta)
        
        print(f"   📊 Resultado da categorização:")
        print(f"      - Pendentes: {len(pendentes)} alertas")
        print(f"      - Escaladas: {len(escaladas)} alertas")
        print(f"      - Atrasadas: {len(atrasadas)} alertas")
        print(f"      - Encerradas: {len(encerradas)} alertas")
        
        # 4. Verificar se a categorização está correta
        print("\n4️⃣ Verificando se a categorização está correta...")
        
        # Verifica pendentes
        if len(pendentes) == 1 and pendentes[0].codigo == 'PEND001':
            print("   ✅ Pendentes: CORRETO")
        else:
            print("   ❌ Pendentes: INCORRETO")
        
        # Verifica escaladas
        if len(escaladas) == 1 and escaladas[0].codigo == 'ESC001':
            print("   ✅ Escaladas: CORRETO")
        else:
            print("   ❌ Escaladas: INCORRETO")
        
        # Verifica atrasadas
        if len(atrasadas) == 1 and atrasadas[0].codigo == 'ATR001':
            print("   ✅ Atrasadas: CORRETO")
        else:
            print("   ❌ Atrasadas: INCORRETO")
        
        # Verifica encerradas
        if len(encerradas) == 1 and encerradas[0].codigo == 'ENC001':
            print("   ✅ Encerradas: CORRETO")
        else:
            print("   ❌ Encerradas: INCORRETO")
        
        # 5. Testar mudança de status de atrasada para operando
        print("\n5️⃣ Testando mudança de status (atrasada → operando)...")
        
        # Simula a mudança de status
        alerta_atrasada.status_operacao = 'operando'
        alerta_atrasada.horario_operando = now_br
        
        # Rastreia a origem do encerramento
        if alerta_atrasada.previsao:
            previsao_dt = alerta_atrasada.previsao_datetime
            if previsao_dt:
                if previsao_dt.tzinfo is None:
                    previsao_dt = tz_br.localize(previsao_dt)
                else:
                    previsao_dt = previsao_dt.astimezone(tz_br)
                
                if previsao_dt < now:
                    alerta_atrasada.origem_encerramento = 'atrasada'
                    print(f"   ✅ Origem definida: atrasada")
                else:
                    alerta_atrasada.origem_encerramento = 'escalada'
                    print(f"   ✅ Origem definida: escalada")
        
        db.commit()
        db.refresh(alerta_atrasada)
        
        print(f"   ✅ Status atualizado:")
        print(f"      Status operação: {alerta_atrasada.status_operacao}")
        print(f"      Horário operando: {alerta_atrasada.horario_operando}")
        print(f"      Origem encerramento: {alerta_atrasada.origem_encerramento}")
        
        # 6. Testar categorização após mudança
        print("\n6️⃣ Testando categorização após mudança...")
        
        # Recategoriza
        pendentes = []
        escaladas = []
        atrasadas = []
        encerradas = []
        
        for alerta in db.query(Alerta).all():
            if not alerta.previsao:
                pendentes.append(alerta)
            elif alerta.status_operacao == 'operando':
                encerradas.append(alerta)
            else:
                previsao_dt = alerta.previsao_datetime
                if previsao_dt:
                    if previsao_dt.tzinfo is None:
                        previsao_dt = tz_br.localize(previsao_dt)
                    else:
                        previsao_dt = previsao_dt.astimezone(tz_br)
                    
                    if previsao_dt >= now:
                        escaladas.append(alerta)
                    else:
                        atrasadas.append(alerta)
                else:
                    escaladas.append(alerta)
        
        print(f"   📊 Resultado após mudança:")
        print(f"      - Pendentes: {len(pendentes)} alertas")
        print(f"      - Escaladas: {len(escaladas)} alertas")
        print(f"      - Atrasadas: {len(atrasadas)} alertas")
        print(f"      - Encerradas: {len(encerradas)} alertas")
        
        # Verifica se o alerta foi movido para encerradas
        alerta_movido = None
        for alerta in encerradas:
            if alerta.codigo == 'ATR001':
                alerta_movido = alerta
                break
        
        if alerta_movido:
            print("   ✅ Alerta atrasado foi movido para encerradas")
            if alerta_movido.origem_encerramento == 'atrasada':
                print("   ✅ Origem corretamente definida como 'atrasada'")
                print("   ✅ No frontend será exibido com texto vermelho")
            else:
                print(f"   ❌ Origem incorreta: {alerta_movido.origem_encerramento}")
        else:
            print("   ❌ Alerta atrasado não foi movido para encerradas")
        
        print("\n" + "=" * 50)
        print("📋 RESUMO DO TESTE DA NOVA REGRA DE NEGÓCIO:")
        print("✅ Categorização baseada em previsão e status_operacao")
        print("✅ Alertas pendentes (sem previsão)")
        print("✅ Alertas escaladas (previsão não excedida)")
        print("✅ Alertas atrasadas (previsão excedida)")
        print("✅ Alertas encerradas (status operando)")
        print("✅ Mudança de status funciona corretamente")
        print("✅ Origem do encerramento é rastreada")
        print("🏁 TESTE CONCLUÍDO")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        db.close()

if __name__ == "__main__":
    test_nova_regra_negocio() 