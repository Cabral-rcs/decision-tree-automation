#!/usr/bin/env python3
"""
Script para testar as importações e identificar problemas
"""

def test_imports():
    """Testa todas as importações necessárias"""
    
    print("=== Teste de Importações ===\n")
    
    try:
        print("1. Testando importações básicas...")
        from fastapi import FastAPI
        from sqlalchemy.orm import Session
        print("   ✅ FastAPI e SQLAlchemy OK")
    except Exception as e:
        print(f"   ❌ Erro nas importações básicas: {e}")
        return False
    
    try:
        print("2. Testando modelos...")
        from backend.models.auto_alert_config_model import AutoAlertConfig
        from backend.models.lider_model import Lider
        from backend.models.alerta_model import Alerta
        print("   ✅ Modelos OK")
    except Exception as e:
        print(f"   ❌ Erro nos modelos: {e}")
        return False
    
    try:
        print("3. Testando serviços...")
        from backend.services.mock_data_generator import MockDataGenerator
        print("   ✅ MockDataGenerator OK")
    except Exception as e:
        print(f"   ❌ Erro no MockDataGenerator: {e}")
        return False
    
    try:
        print("4. Testando scheduler...")
        from backend.services.auto_alert_scheduler import auto_alert_scheduler
        print("   ✅ AutoAlertScheduler OK")
    except Exception as e:
        print(f"   ❌ Erro no AutoAlertScheduler: {e}")
        return False
    
    try:
        print("5. Testando controllers...")
        from backend.controllers.auto_alert_controller import ensure_rafael_cabral_exists
        print("   ✅ AutoAlertController OK")
    except Exception as e:
        print(f"   ❌ Erro no AutoAlertController: {e}")
        return False
    
    try:
        print("6. Testando main...")
        from backend.main import app
        print("   ✅ Main app OK")
    except Exception as e:
        print(f"   ❌ Erro no main: {e}")
        return False
    
    print("\n=== Todas as importações OK ===")
    return True

if __name__ == "__main__":
    test_imports() 