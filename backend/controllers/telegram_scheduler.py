# telegram_scheduler.py - Controller para envio de perguntas sob demanda
import requests
from backend.config import TELEGRAM_API_URL
from backend.models.responses_model import set_aguardando_resposta, is_aguardando_resposta

MENSAGEM_INICIAL = 'Automação de previsões'

# Função para enviar mensagem inicial pós-deploy (se necessário)
def enviar_mensagem_inicial(user_id):
    payload = {
        'chat_id': user_id,
        'text': MENSAGEM_INICIAL
    }
    try:
        resp = requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)
        print(f'Mensagem inicial enviada para {user_id}: {resp.status_code}')
    except Exception as e:
        print(f'Erro ao enviar mensagem inicial para {user_id}: {e}')

def enviar_pergunta_para_usuario(user_id):
    if is_aguardando_resposta(str(user_id)):
        print(f'Usuário {user_id} ainda não respondeu a última pergunta.')
        return
    # Não envia mais "Como você está se sentindo agora?" aqui
    pass 