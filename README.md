# Decision Tree Automation

Este repositório contém a solução modularizada para automação de decisões baseada em alertas, com integração ao Telegram.

## Estrutura do Projeto Automação da Árvore de decisão

```
decision-tree-automation/
├─ decision-tree-automation-api/      # Backend FastAPI, banco, integrações
├─ decision-tree-automation-ui/       # Frontend (HTML/JS)
├─ decision-tree-automation-engine/   # (opcional, lógica de automação/worker)
├─ decision-tree-automation-infra/    # Infraestrutura, scripts, pipelines
```

## Como rodar o projeto

### 1. decision-tree-automation-api
- Entre na pasta `decision-tree-automation-api`
- Instale as dependências:
  ```
  pip install -r requirements.txt
  ```
- Configure o arquivo `.env` (veja `.env.example`)
- Execute o backend:
  ```
  uvicorn backend.main:app --reload
  ```
- O backend estará disponível em `http://localhost:8000`

### 2. decision-tree-automation-ui
- Entre na pasta `decision-tree-automation-ui`
- Abra o arquivo `index.html` no navegador
- O frontend consome a API do backend

### 3. decision-tree-automation-engine
- (Opcional) Use para automações, workers, processamento assíncrono

### 4. decision-tree-automation-infra
- (Opcional) Scripts de infraestrutura, pipelines, deploy

## Funcionalidades principais
- Cadastro e gerenciamento de líderes (nome e ID do chat do Telegram)
- Criação manual de alertas associando ao nome do líder
- Envio automático de mensagem ao líder via Telegram solicitando previsão
- Recebimento e validação da resposta do líder (horário no formato HH:MM)
- Categorização automática dos alertas
- Botão para alterar status do alerta (Operando/Não operando)
- Visualização de todos os alertas e líderes no frontend

Consulte o README de cada módulo para detalhes específicos. 