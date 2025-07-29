# Decision Tree Automation

Sistema de gestão de alertas com integração ao Telegram.

## Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o Servidor
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Acessar o Sistema
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Funcionalidades

- ✅ Criação de alertas automáticos
- ✅ Integração com Telegram
- ✅ Atualização em tempo real
- ✅ Interface web responsiva
- ✅ Sistema de notificações

## Estrutura do Projeto

```
decision-tree-automation-api/
├── backend/
│   ├── controllers/     # Controladores da API
│   ├── models/         # Modelos de dados
│   ├── services/       # Serviços
│   ├── views/          # Rotas da API
│   └── main.py         # Aplicação principal
└── requirements.txt    # Dependências
```

## Correções Implementadas

- ✅ Headers anti-cache no frontend
- ✅ Sistema de polling melhorado (3 segundos)
- ✅ Indicador de status visual
- ✅ Botão de forçar atualização
- ✅ Notificações automáticas
- ✅ Endpoint de última atualização melhorado
- ✅ Logs detalhados no webhook do Telegram

## Uso

1. Execute `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
2. Acesse http://localhost:8000
3. Use o sistema de alertas automáticos ou crie alertas manualmente
4. As respostas do Telegram aparecerão automaticamente na interface 