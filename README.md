# Decision Tree Automation

Este repositório contém uma solução modular para automação de decisões baseada em alertas, com integração ao Telegram e interface web para gestão.

---

## Estrutura do Projeto

```
decision-tree-automation/
├─ decision-tree-automation-api/      # Backend (API, lógica, banco, integrações)
│  ├─ backend/
│  │  ├─ controllers/
│  │  ├─ models/
│  │  ├─ views/
│  │  ├─ main.py
│  │  ├─ config.py
│  │  └─ __init__.py
│  ├─ requirements.txt
│  ├─ render.yaml
│  └─ start.sh
├─ decision-tree-automation-ui/       # Frontend (HTML/JS)
│  └─ index.html
└─ README.md
```

---

## Tecnologias Utilizadas

### Backend

- **Python 3.8+**  
  Linguagem principal para lógica de negócio, API e integrações.

- **FastAPI**  
  Framework web moderno e performático para construção de APIs REST.  
  *Motivo:* Simplicidade, performance, tipagem forte e documentação automática.

- **Uvicorn**  
  Servidor ASGI leve e rápido para rodar aplicações FastAPI.  
  *Motivo:* Compatibilidade com FastAPI e alta performance.

- **SQLAlchemy**  
  ORM (Object Relational Mapper) para modelagem e manipulação do banco de dados relacional.  
  *Motivo:* Flexibilidade, integração fácil com múltiplos bancos e abstração de queries SQL.

- **psycopg2-binary**  
  Driver para conexão com bancos PostgreSQL.  
  *Motivo:* Confiável, performático e padrão de mercado para Python + PostgreSQL.

- **python-dotenv**  
  Carrega variáveis de ambiente de arquivos `.env`.  
  *Motivo:* Facilita configuração segura e desacoplada do código.

- **requests**  
  Biblioteca HTTP para integração com APIs externas (ex: Telegram).  
  *Motivo:* Simplicidade e robustez para chamadas HTTP.

- **apscheduler**  
  Agendamento de tarefas (ex: envio automático de mensagens).  
  *Motivo:* Permite automação de fluxos recorrentes.

- **pytz**  
  Manipulação de fusos horários.  
  *Motivo:* Necessário para tratar datas e horários corretamente no contexto brasileiro.

### Frontend

- **HTML5, CSS3, JavaScript (Vanilla)**  
  Interface web leve, sem frameworks, para cadastro e visualização de alertas/líderes.  
  *Motivo:* Simplicidade, fácil manutenção e integração direta com a API.

---

## Armazenamento de Dados

- **Banco de Dados Relacional (PostgreSQL recomendado)**
  - Todas as entidades (alertas, líderes, respostas, estados) são persistidas via SQLAlchemy.
  - A string de conexão é configurada via variável de ambiente `DATABASE_URL`.
  - O modelo de dados é inicializado automaticamente ao subir a aplicação.

- **Configuração**
  - Variáveis sensíveis (tokens, URLs, IDs) são lidas de um arquivo `.env` ou do ambiente do sistema operacional.

---

## Estrutura de Pastas e Arquivos

### Backend (`decision-tree-automation-api/backend/`)

- **main.py**  
  Ponto de entrada da aplicação FastAPI. Inicializa o app, configura CORS, inclui rotas e serve o frontend.

- **config.py**  
  Carrega variáveis de ambiente e configurações globais (ex: tokens do Telegram, IDs de chat).

- **controllers/**  
  - `alerta_controller.py`: Gerencia criação, atualização e listagem de alertas, além de integração com o Telegram.
  - `lider_controller.py`: CRUD de líderes (usuários responsáveis por responder alertas).
  - `telegram_scheduler.py`: Funções para envio automático de mensagens e agendamento.
  - `telegram_webhook.py`: Recebe e processa respostas enviadas ao bot do Telegram.

- **models/**  
  - `alerta_model.py`: Define a estrutura da tabela de alertas.
  - `lider_model.py`: Define a estrutura da tabela de líderes.
  - `responses_model.py`: Define respostas, estado de usuários e inicialização do banco.

- **views/**  
  - `api_router.py`: Define as rotas da API (endpoints REST).
  - `__init__.py`: Inicializa o módulo de views.

- **__init__.py**  
  Inicializa o pacote backend.

### Frontend (`decision-tree-automation-ui/`)

- **index.html**  
  Interface web para cadastro de alertas, visualização de categorias (pendentes, escaladas, atrasadas, encerradas) e gestão de líderes.  
  Consome a API do backend diretamente via JavaScript.

### Outros Arquivos

- **requirements.txt**  
  Lista todas as dependências Python do backend.

- **render.yaml**  
  Configuração para deploy automatizado na plataforma Render.

- **start.sh**  
  Script de inicialização do backend (usado em produção/deploy).

---

## Passo a Passo para Rodar a Aplicação

### 1. Clone o repositório

```sh
git clone <url-do-repositorio>
cd decision-tree-automation/decision-tree-automation-api
```

### 2. Instale as dependências

```sh
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na pasta `decision-tree-automation-api` com o seguinte formato:

```
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
TELEGRAM_BOT_TOKEN=seu_token_do_telegram
CHAT_IDS=123456789,987654321
```

### 4. Inicie o backend

```sh
uvicorn backend.main:app --reload
```

O backend estará disponível em `http://localhost:8000`.

### 5. Inicie o frontend

Abra o arquivo `decision-tree-automation-ui/index.html` no navegador.

---

## O que cada pasta/arquivo faz

- **decision-tree-automation-api/backend/main.py**: Inicializa o backend, configura rotas e serve o frontend.
- **decision-tree-automation-api/backend/config.py**: Gerencia variáveis de ambiente e configurações globais.
- **decision-tree-automation-api/backend/controllers/**: Lógica de negócio, integrações e endpoints principais.
- **decision-tree-automation-api/backend/models/**: Modelos de dados e inicialização do banco.
- **decision-tree-automation-api/backend/views/**: Roteamento e organização dos endpoints da API.
- **decision-tree-automation-ui/index.html**: Interface web para interação com o sistema.
- **requirements.txt**: Dependências do backend.
- **render.yaml**: Configuração de deploy na Render.
- **start.sh**: Script de inicialização para produção.

---

Se precisar de mais detalhes ou quiser incluir as funcionalidades, é só pedir! 

---

## Arquivos-Chave e Funções no Fluxo Central

| Arquivo/Função                                         | Papel no fluxo central                                                                 |
|--------------------------------------------------------|---------------------------------------------------------------------------------------|
| backend/controllers/alerta_controller.py               | Criação, atualização, listagem e categorização dos alertas; envio ao Telegram         |
| backend/controllers/telegram_webhook.py                | Recebe e processa respostas do Telegram                                               |
| backend/controllers/telegram_scheduler.py              | Funções auxiliares para envio de mensagens                                            |
| backend/models/alerta_model.py                         | Estrutura dos alertas                                                                 |
| backend/models/lider_model.py                          | Estrutura dos líderes                                                                 |
| backend/models/responses_model.py                      | Estrutura das respostas e estado do usuário                                           |
| backend/config.py                                      | Configuração de tokens, chat_ids, variáveis de ambiente                               |
| backend/views/api_router.py                            | Roteamento dos endpoints REST                                                         |
| decision-tree-automation-ui/index.html                 | Interface web para cadastro, visualização e acompanhamento dos alertas                |

---

## Por que essas escolhas?

- **FastAPI + Uvicorn:** Modernos, rápidos, fáceis de manter e com excelente suporte a APIs REST.
- **SQLAlchemy:** Abstrai o banco, facilita manutenção e portabilidade.
- **PostgreSQL:** Robusto, seguro e padrão para aplicações críticas.
- **requests:** Simples e eficiente para integrações HTTP.
- **Telegram Bot API:** Canal oficial, seguro e documentado para automação de mensagens.
- **HTML/JS puro:** Interface leve, sem dependências pesadas, fácil de customizar. 