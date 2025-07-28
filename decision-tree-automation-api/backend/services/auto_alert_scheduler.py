import logging
import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.auto_alert_config_model import AutoAlertConfig
from backend.services.mock_data_generator import MockDataGenerator
# Importações movidas para dentro da função para evitar importação circular

logger = logging.getLogger(__name__)

class AutoAlertScheduler:
    """Scheduler para criação automática de alertas usando threading"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.interval_minutes = 3
        self.stop_event = threading.Event()
    
    def start(self):
        """Inicia o scheduler"""
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            logger.info("Auto Alert Scheduler iniciado")
    
    def stop(self):
        """Para o scheduler"""
        if self.is_running:
            self.is_running = False
            self.stop_event.set()
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("Auto Alert Scheduler parado")
    
    def schedule_auto_alert(self):
        """Agenda a criação automática de alertas com intervalo padrão"""
        self.interval_minutes = 3
        logger.info("Job de criação automática de alertas agendado para cada 3 minutos")
    
    def schedule_auto_alert_with_interval(self, interval_minutes: int):
        """Agenda a criação automática de alertas com intervalo específico"""
        self.interval_minutes = interval_minutes
        logger.info(f"Job de criação automática de alertas agendado para cada {interval_minutes} minutos")
    
    def _run_scheduler(self):
        """Executa o loop principal do scheduler"""
        while self.is_running and not self.stop_event.is_set():
            try:
                self._create_auto_alert()
                # Aguarda o intervalo especificado
                self.stop_event.wait(timeout=self.interval_minutes * 60)
            except Exception as e:
                logger.error(f"Erro no scheduler: {str(e)}")
                # Aguarda 1 minuto antes de tentar novamente
                self.stop_event.wait(timeout=60)
    
    def _create_auto_alert(self):
        """Executa a criação automática de alertas"""
        # Importações locais para evitar importação circular
        from backend.controllers.alerta_controller import criar_alerta
        from backend.controllers.auto_alert_controller import ensure_rafael_cabral_exists
        
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
            
            # Cria o alerta com todos os dados
            alerta_dict = {
                "nome_lider": alert_data["nome_lider"],
                "problema": f"[AUTO] {alert_data['equipamento']} - {alert_data['operacao']} - {alert_data['justificativa']}",
                "codigo": alert_data["codigo"],
                "unidade": alert_data["unidade"],
                "frente": alert_data["frente"],
                "equipamento": alert_data["equipamento"],
                "codigo_equipamento": alert_data["codigo_equipamento"],
                "tipo_operacao": alert_data["tipo_operacao"],
                "operacao": alert_data["operacao"],
                "nome_operador": alert_data["nome_operador"],
                "data_operacao": alert_data["data_operacao"],
                "tempo_abertura": alert_data["tempo_abertura"],
                "tipo_arvore": alert_data["tipo_arvore"],
                "justificativa": alert_data["justificativa"],
                "prazo": alert_data["prazo"]
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
        self.interval_minutes = interval_minutes
        logger.info(f"Intervalo de criação automática atualizado para {interval_minutes} minutos")

# Instância global do scheduler
auto_alert_scheduler = AutoAlertScheduler() 