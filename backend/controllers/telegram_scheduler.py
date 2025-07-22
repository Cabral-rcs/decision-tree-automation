# telegram_scheduler.py - Controller para envio de perguntas sob demanda
import requests
from backend.config import TELEGRAM_API_URL
from backend.models.responses_model import set_aguardando_resposta, is_aguardando_resposta

PERGUNTA_PADRAO = 'Como você está se sentindo agora?'

def enviar_pergunta_para_usuario(user_id):
    if is_aguardando_resposta(str(user_id)):
        print(f'Usuário {user_id} ainda não respondeu a última pergunta.')
        return
    payload = {
        'chat_id': user_id,
        'text': PERGUNTA_PADRAO
    }
    try:
        resp = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
        print(f'Pergunta enviada para {user_id}: {resp.status_code}')
        set_aguardando_resposta(str(user_id))
    except Exception as e:
        print(f'Erro ao enviar para {user_id}: {e}') 