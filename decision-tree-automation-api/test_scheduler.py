#!/usr/bin/env python3
"""
Script de teste para verificar se o scheduler de alertas automáticos está funcionando
"""

import os
import sys
import time
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(__file__))

def test_scheduler():
    """Testa o scheduler de alertas automáticos"""
    
    print("=== TESTE DO SCHEDULER DE ALERTAS AUTOMÁTICOS ===\n")
    
    try:
        # Importa os módulos necessários
        from backend.services.auto_alert_scheduler import auto_alert_scheduler
        from backend.models.responses_model import SessionLocal
        from backend.models.auto_alert_config_model import AutoAlertConfig
        from backend.models.alerta_model import Alerta
        
        print("1. Verificando configuração do banco...")
        db = SessionLocal()
        
        config = db.query(AutoAlertConfig).first()
        if not config:
            print("   ❌ Configuração não encontrada")
            return False
        
        print(f"   ✅ Configuração encontrada:")
        print(f"      - Ativo: {config.is_active}")
        print(f"      - Intervalo: {config.interval_minutes} minutos")
        print(f"      - Última execução: {config.last_execution}")
        
        print("\n2. Verificando status do scheduler...")
        print(f"   - Scheduler rodando: {auto_alert_scheduler.is_running}")
        print(f"   - Intervalo atual: {auto_alert_scheduler.interval_minutes} minutos")
        print(f"   - Thread viva: {auto_alert_scheduler.thread.is_alive() if auto_alert_scheduler.thread else False}")
        
        print("\n3. Contando alertas existentes...")
        alertas_count = db.query(Alerta).count()
        print(f"   - Total de alertas: {alertas_count}")
        
        print("\n4. Testando criação manual de alerta...")
        try:
            auto_alert_scheduler._create_auto_alert()
            print("   ✅ Alerta criado com sucesso")
            
            # Conta novamente
            new_count = db.query(Alerta).count()
            print(f"   - Novo total de alertas: {new_count}")
            print(f"   - Alertas criados: {new_count - alertas_count}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar alerta: {e}")
            return False
        
        print("\n5. Verificando se o scheduler está ativo...")
        if not auto_alert_scheduler.is_running:
            print("   ⚠️  Scheduler não está rodando")
            if config.is_active:
                print("   🔄 Iniciando scheduler...")
                auto_alert_scheduler.start()
                time.sleep(2)
                print(f"   - Scheduler rodando: {auto_alert_scheduler.is_running}")
                print(f"   - Thread viva: {auto_alert_scheduler.thread.is_alive() if auto_alert_scheduler.thread else False}")
            else:
                print("   ℹ️  Scheduler desativado na configuração")
        else:
            print("   ✅ Scheduler está rodando")
        
        db.close()
        
        print("\n=== TESTE CONCLUÍDO ===")
        print("Se o scheduler estiver ativo, os alertas devem ser criados automaticamente.")
        print("Verifique a interface web para ver os novos alertas.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_scheduler() 