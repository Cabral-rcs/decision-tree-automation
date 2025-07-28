from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.auto_alert_config_model import AutoAlertConfig
from backend.models.lider_model import Lider
from backend.services.mock_data_generator import MockDataGenerator
from backend.controllers.alerta_controller import criar_alerta
from backend.services.auto_alert_scheduler import auto_alert_scheduler
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def ensure_rafael_cabral_exists():
    """Garante que o líder Rafael Cabral existe no sistema"""
    db: Session = SessionLocal()
    try:
        # Verifica se Rafael Cabral já existe
        rafael = db.query(Lider).filter(Lider.nome_lider == "Rafael Cabral").first()
        if not rafael:
            # Cria Rafael Cabral se não existir
            rafael = Lider(nome_lider="Rafael Cabral", chat_id="6435800936")
            db.add(rafael)
            db.commit()
            db.refresh(rafael)
            logger.info("Líder Rafael Cabral criado automaticamente")
        return rafael
    finally:
        db.close()

@router.get('/auto-alert/status')
def get_auto_alert_status():
    """Retorna o status atual da criação automática de alertas"""
    db: Session = SessionLocal()
    try:
        config = db.query(AutoAlertConfig).first()
        if not config:
            # Cria configuração padrão se não existir
            config = AutoAlertConfig(is_active=False, interval_minutes=3)
            db.add(config)
            db.commit()
            db.refresh(config)
        
        return {
            "is_active": config.is_active,
            "interval_minutes": config.interval_minutes,
            "last_execution": config.last_execution.isoformat() if config.last_execution else None
        }
    finally:
        db.close()

@router.post('/auto-alert/toggle')
def toggle_auto_alert():
    """Ativa/desativa a criação automática de alertas"""
    db: Session = SessionLocal()
    try:
        config = db.query(AutoAlertConfig).first()
        if not config:
            config = AutoAlertConfig(is_active=True, interval_minutes=3)
            db.add(config)
        else:
            config.is_active = not config.is_active
            config.updated_at = datetime.now()
        
        db.commit()
        db.refresh(config)
        
        status = "ativada" if config.is_active else "desativada"
        logger.info(f"Criação automática de alertas {status}")
        
        return {
            "is_active": config.is_active,
            "message": f"Criação automática de alertas {status}"
        }
    finally:
        db.close()

@router.post('/auto-alert/create-now')
def create_alert_now():
    """Cria um alerta imediatamente (para teste)"""
    try:
        # Garante que Rafael Cabral existe
        ensure_rafael_cabral_exists()
        
        # Gera dados mockados
        alert_data = MockDataGenerator.generate_alert_data()
        
        # Cria o alerta usando o controller existente
        alerta_dict = {
            "nome_lider": alert_data["nome_lider"],
            "problema": f"[AUTO] {alert_data['equipamento']} - {alert_data['operacao']} - {alert_data['justificativa']}"
        }
        
        result = criar_alerta(alerta_dict)
        
        logger.info(f"Alerta automático criado: {result}")
        
        return {
            "success": True,
            "alert_id": result["id"],
            "alert_data": alert_data,
            "message": "Alerta automático criado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao criar alerta automático: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar alerta: {str(e)}")

@router.post('/auto-alert/update-interval')
def update_interval(interval_minutes: int):
    """Atualiza o intervalo de criação de alertas"""
    if interval_minutes < 1 or interval_minutes > 60:
        raise HTTPException(status_code=400, detail="Intervalo deve estar entre 1 e 60 minutos")
    
    db: Session = SessionLocal()
    try:
        config = db.query(AutoAlertConfig).first()
        if not config:
            config = AutoAlertConfig(interval_minutes=interval_minutes)
            db.add(config)
        else:
            config.interval_minutes = interval_minutes
            config.updated_at = datetime.now()
        
        db.commit()
        db.refresh(config)
        
        # Atualiza o scheduler com o novo intervalo
        auto_alert_scheduler.update_interval(interval_minutes)
        
        return {
            "interval_minutes": config.interval_minutes,
            "message": f"Intervalo atualizado para {interval_minutes} minutos"
        }
    finally:
        db.close() 