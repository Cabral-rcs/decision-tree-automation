import logging
import threading
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.auto_alert_config_model import AutoAlertConfig

from backend.services.mock_data_generator import MockDataGenerator

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
    
    def restart(self):
        """Reinicia o scheduler"""
        logger.info("Reiniciando Auto Alert Scheduler...")
        self.stop()
        time.sleep(1)  # Aguarda um pouco antes de reiniciar
        self.start()
    
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
        logger.info(f"Scheduler iniciado com intervalo de {self.interval_minutes} minutos")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Executa a criação de alerta
                self._create_auto_alert()
                
                # Aguarda o intervalo especificado
                logger.debug(f"Aguardando {self.interval_minutes} minutos até próxima execução...")
                self.stop_event.wait(timeout=self.interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Erro no scheduler: {str(e)}")
                # Aguarda 1 minuto antes de tentar novamente
                self.stop_event.wait(timeout=60)
    
    def _create_auto_alert(self):
        """Executa a criação automática de alertas"""
        db: Session = SessionLocal()
        try:
            # Verifica se a criação automática está ativa
            config = db.query(AutoAlertConfig).first()
            if not config:
                # Cria configuração padrão se não existir
                config = AutoAlertConfig(is_active=False, interval_minutes=3)
                db.add(config)
                db.commit()
                db.refresh(config)
                logger.info("Configuração padrão criada (desativada)")
                return
            
            if not config.is_active:
                logger.debug("Criação automática de alertas desativada")
                return
            
            # Atualiza o intervalo do scheduler com o valor do banco
            if config.interval_minutes != self.interval_minutes:
                self.interval_minutes = config.interval_minutes
                logger.info(f"Intervalo atualizado para {self.interval_minutes} minutos")
            
            # Garante que Rafael Cabral existe
            self._ensure_rafael_cabral_exists(db)
            
            # Gera dados mockados
            alert_data = MockDataGenerator.generate_alert_data()
            
            # Cria o alerta diretamente no banco para evitar importação circular
            novo_alerta = self._create_alert_directly(db, alert_data)
            
            # Atualiza última execução
            config.last_execution = datetime.now()
            db.commit()
            
            logger.info(f"Alerta automático criado com sucesso - ID: {novo_alerta.id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta automático: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    def _ensure_rafael_cabral_exists(self, db: Session):
        """Garante que o líder Rafael Cabral existe no sistema"""
        # Rafael Cabral é o líder fixo, não precisa verificar no banco
        logger.debug("Usando Rafael Cabral como líder fixo (Chat ID: 6435800936)")
        return {"nome_lider": "Rafael Cabral", "chat_id": "6435800936"}
    
    def _create_alert_directly(self, db: Session, alert_data: dict):
        """Cria alerta diretamente no banco para evitar importação circular"""
        try:
            from backend.models.alerta_model import Alerta
            import requests
            from backend.config import TELEGRAM_API_URL
            
            # Usar Rafael Cabral como líder fixo
            nome_lider = "Rafael Cabral"
            chat_id = "6435800936"
            
            # Criar alerta com todos os campos disponíveis
            novo_alerta = Alerta(
                chat_id=chat_id,
                problema=alert_data['problema'],
                status='pendente',
                nome_lider=nome_lider,
                codigo=alert_data.get('codigo'),
                unidade=alert_data.get('unidade'),
                frente=alert_data.get('frente'),
                equipamento=alert_data.get('equipamento'),
                codigo_equipamento=alert_data.get('codigo_equipamento'),
                tipo_operacao=alert_data.get('tipo_operacao'),
                operacao=alert_data.get('operacao'),
                nome_operador=alert_data.get('nome_operador'),
                data_operacao=datetime.fromisoformat(alert_data.get('data_operacao')) if alert_data.get('data_operacao') else None,
                tempo_abertura=alert_data.get('tempo_abertura'),
                tipo_arvore=alert_data.get('tipo_arvore'),
                justificativa=None,  # Campo não preenchido automaticamente
                prazo=None  # Campo não preenchido automaticamente
            )
            db.add(novo_alerta)
            db.commit()
            db.refresh(novo_alerta)
            
            # Envia mensagem ao líder no Telegram
            try:
                mensagem = f"Qual o prazo para {novo_alerta.operacao} da máquina {novo_alerta.equipamento}?\n\n(Responda apenas o horário no formato HH:MM)"
                payload = {
                    'chat_id': novo_alerta.chat_id,
                    'text': mensagem
                }
                resp = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload, timeout=10)
                if resp.ok:
                    mensagem_id = resp.json().get('result', {}).get('message_id')
                    novo_alerta.mensagem_id = mensagem_id
                    db.commit()
                    logger.info(f"Mensagem enviada ao Telegram para chat_id {novo_alerta.chat_id}")
                else:
                    logger.warning(f'Erro ao enviar mensagem ao Telegram: {resp.status_code} - {resp.text}')
            except Exception as e:
                logger.error(f'Erro ao enviar mensagem ao Telegram: {str(e)}')
                # Continua mesmo se falhar o envio da mensagem
            
            logger.info(f"Alerta automático criado: ID {novo_alerta.id}")
            return novo_alerta
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta diretamente: {str(e)}")
            raise
    
    def update_interval(self, interval_minutes: int):
        """Atualiza o intervalo de criação de alertas"""
        old_interval = self.interval_minutes
        self.interval_minutes = interval_minutes
        logger.info(f"Intervalo de criação automática atualizado de {old_interval} para {interval_minutes} minutos")
        
        # Reinicia o scheduler para aplicar o novo intervalo
        if self.is_running:
            logger.info("Reiniciando scheduler para aplicar novo intervalo...")
            self.restart()

# Instância global do scheduler
auto_alert_scheduler = AutoAlertScheduler() 