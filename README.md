# Sistema de Coleta e Exibição de Respostas do Telegram

Este sistema recebe respostas de usuários enviadas por um bot do Telegram, armazena em um banco de dados SQLite e exibe as respostas em um frontend web.

## Como rodar o sistema!

### 1. Instale as dependências do backend!!
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure o token do bot e os chat_ids!
Edite o arquivo `bot/backend/config.py` e coloque o token do seu bot do Telegram e os IDs dos chats que devem receber as perguntas:
```python
TELEGRAM_BOT_TOKEN = 'SEU_TOKEN_AQUI'
CHAT_IDS = [123456789, 987654321]  # IDs dos usuários ou grupos
```

### 3. Rode o backend
```bash
uvicorn backend.main:app --reload
```

### 4. Configure o webhook do Telegram
Execute o comando abaixo (substitua pelo seu token e URL pública, use ngrok para testes locais):
```
https://api.telegram.org/botSEU_TOKEN_AQUI/setWebhook?url=https://SUA_URL/webhook/telegram
```

### 5. Rode o frontend
Abra o arquivo `bot/frontend/index.html` no navegador.

## Observações
- O backend envia perguntas automaticamente a cada 10 minutos para os chats configurados.
- As respostas dos usuários são recebidas via webhook e armazenadas no banco.
- O frontend exibe as respostas em tempo real.
- Para rodar localmente e receber webhooks, use [ngrok](https://ngrok.com/) para expor sua porta 8000:
```bash
ngrok http 8000
``` 