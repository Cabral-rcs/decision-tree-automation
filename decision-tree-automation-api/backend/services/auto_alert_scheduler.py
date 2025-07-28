import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.auto_alert_config_model import AutoAlertConfig
from backend.services.mock_data_generator import MockDataGenerator
from backend.controllers.alerta_controller import criar_alerta
from backend.controllers.auto_alert_controller import ensure_rafael_cabral_exists
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

class AutoAlertScheduler:
    """Scheduler para criação automática de alertas"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Inicia o scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Auto Alert Scheduler iniciado")
    
    def stop(self):
        """Para o scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Auto Alert Scheduler parado")
    
    def schedule_auto_alert(self):
        """Agenda a criação automática de alertas"""
        # Remove jobs existentes
        self.scheduler.remove_all_jobs()
        
        # Adiciona novo job
        self.scheduler.add_job(
            self._create_auto_alert,
            IntervalTrigger(minutes=3),
            id='auto_alert_job',
            name='Criação Automática de Alertas',
            replace_existing=True
        )
        
        logger.info("Job de criação automática de alertas agendado para cada 3 minutos")
    
    def schedule_auto_alert_with_interval(self, interval_minutes: int):
        """Agenda a criação automática de alertas com intervalo específico"""
        # Remove jobs existentes
        self.scheduler.remove_all_jobs()
        
        # Adiciona novo job
        self.scheduler.add_job(
            self._create_auto_alert,
            IntervalTrigger(minutes=interval_minutes),
            id='auto_alert_job',
            name='Criação Automática de Alertas',
            replace_existing=True
        )
        
        logger.info(f"Job de criação automática de alertas agendado para cada {interval_minutes} minutos")
    
    async def _create_auto_alert(self):
        """Executa a criação automática de alertas"""
        db: Session = SessionLocal()
        try:
            # Verifica se a criação automática está ativa
            config = db.query(AutoAlertConfig).first()
            if not config or not config.is_active:
                logger.debug("Criação automática de alertas desativada")
                return
            
            # Verifica se já executou recentemente
            if config.last_execution:
                time_since_last = datetime.now() - config.last_execution
                if time_since_last.total_seconds() < (config.interval_minutes * 60):
                    logger.debug(f"Ainda não é hora de criar novo alerta. Última execução: {config.last_execution}")
                    return
            
            # Garante que Rafael Cabral existe
            ensure_rafael_cabral_exists()
            
            # Gera dados mockados
            alert_data = MockDataGenerator.generate_alert_data()
            
            # Cria o alerta
            alerta_dict = {
                "nome_lider": alert_data["nome_lider"],
                "problema": f"[AUTO] {alert_data['equipamento']} - {alert_data['operacao']} - {alert_data['justificativa']}"
            }
            
            result = criar_alerta(alerta_dict)
            
            # Atualiza última execução
            config.last_execution = datetime.now()
            db.commit()
            
            logger.info(f"Alerta automático criado com sucesso: ID {result['id']}")
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta automático: {str(e)}")
        finally:
            db.close()
    
    def update_interval(self, interval_minutes: int):
        """Atualiza o intervalo de criação de alertas"""
        # Remove job existente
        self.scheduler.remove_job('auto_alert_job')
        
        # Adiciona novo job com intervalo atualizado
        self.scheduler.add_job(
            self._create_auto_alert,
            IntervalTrigger(minutes=interval_minutes),
            id='auto_alert_job',
            name='Criação Automática de Alertas',
            replace_existing=True
        )
        
        logger.info(f"Intervalo de criação automática atualizado para {interval_minutes} minutos")

# Instância global do scheduler
auto_alert_scheduler = AutoAlertScheduler() 