from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.models.responses_model import SessionLocal
from backend.models.auto_alert_config_model import AutoAlertConfig

from backend.models.alerta_model import Alerta
from backend.services.mock_data_generator import MockDataGenerator
from datetime import datetime
import logging
import requests
from backend.config import TELEGRAM_API_URL

router = APIRouter()
logger = logging.getLogger(__name__)

def ensure_rafael_cabral_exists():
    """Garante que o líder Rafael Cabral existe no sistema"""
    # Rafael Cabral é o líder fixo, não precisa verificar no banco
    logger.info("Usando Rafael Cabral como líder fixo (Chat ID: 6435800936)")
    return {"nome_lider": "Rafael Cabral", "chat_id": "6435800936"}

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
    except Exception as e:
        logger.error(f"Erro ao obter status dos alertas automáticos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
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
        
        # Atualiza o scheduler
        from backend.services.auto_alert_scheduler import auto_alert_scheduler
        
        if config.is_active:
            # Se foi ativado, reinicia o scheduler
            if not auto_alert_scheduler.is_running:
                auto_alert_scheduler.start()
            else:
                auto_alert_scheduler.restart()
            logger.info("Scheduler de alertas automáticos ativado e reiniciado")
        else:
            # Se foi desativado, para o scheduler
            if auto_alert_scheduler.is_running:
                auto_alert_scheduler.stop()
            logger.info("Scheduler de alertas automáticos desativado")
        
        status = "ativada" if config.is_active else "desativada"
        logger.info(f"Criação automática de alertas {status}")
        
        return {
            "is_active": config.is_active,
            "message": f"Criação automática de alertas {status}"
        }
    except Exception as e:
        logger.error(f"Erro ao alternar status dos alertas automáticos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close()

@router.post('/auto-alert/create-now')
def create_alert_now():
    """Cria um alerta imediatamente (para teste)"""
    db: Session = SessionLocal()
    try:
        # Garante que Rafael Cabral existe
        ensure_rafael_cabral_exists()
        
        # Gera dados mockados
        alert_data = MockDataGenerator.generate_alert_data()
        
        # Usar Rafael Cabral como líder fixo
        nome_lider = "Rafael Cabral"
        chat_id = "6435800936"
        
        # Criar alerta com todos os dados
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
            prazo=None  # Campo preenchido pelo líder via Telegram
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
        
        return {
            "success": True,
            "alert_id": novo_alerta.id,
            "alert_data": alert_data,
            "message": "Alerta automático criado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar alerta automático: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar alerta: {str(e)}")
    finally:
        db.close()

@router.post('/auto-alert/force-create')
def force_create_alert():
    """Força a criação de um alerta (para debug)"""
    from backend.services.auto_alert_scheduler import auto_alert_scheduler
    
    try:
        # Chama diretamente o método de criação
        auto_alert_scheduler._create_auto_alert()
        
        return {
            "success": True,
            "message": "Alerta criado forçadamente (debug)"
        }
    except Exception as e:
        logger.error(f"Erro ao forçar criação de alerta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar alerta: {str(e)}")

@router.get('/auto-alert/scheduler-status')
def get_scheduler_status():
    """Retorna o status detalhado do scheduler"""
    from backend.services.auto_alert_scheduler import auto_alert_scheduler
    
    return {
        "scheduler_running": auto_alert_scheduler.is_running,
        "current_interval_minutes": auto_alert_scheduler.interval_minutes,
        "thread_alive": auto_alert_scheduler.thread.is_alive() if auto_alert_scheduler.thread else False,
        "stop_event_set": auto_alert_scheduler.stop_event.is_set(),
        "timestamp": datetime.now().isoformat()
    }

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
        from backend.services.auto_alert_scheduler import auto_alert_scheduler
        auto_alert_scheduler.update_interval(interval_minutes)
        
        logger.info(f"Intervalo atualizado para {interval_minutes} minutos e scheduler reiniciado")
        
        return {
            "interval_minutes": config.interval_minutes,
            "message": f"Intervalo atualizado para {interval_minutes} minutos"
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar intervalo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        db.close() 