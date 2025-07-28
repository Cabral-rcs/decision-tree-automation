# Decision Tree Automation

Sistema de automação de decisões baseado em alertas operacionais, com integração ao Telegram para comunicação com líderes e interface web para gestão.

---

## Arquitetura de Software

### Padrão Arquitetural: Model-View-Controller (MVC)

O projeto segue o padrão MVC, separando claramente as responsabilidades:

- **Models**: Definem a estrutura dos dados e regras de negócio
- **Views**: Gerenciam a apresentação e roteamento das APIs
- **Controllers**: Contêm a lógica de negócio e integrações

### Estrutura de Camadas

```
┌─────────────────────────────────────┐
│           Frontend (UI)             │
│      HTML/CSS/JavaScript            │
└─────────────────┬───────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────┐
│           Backend (API)             │
│  ┌─────────────┬─────────────────┐  │
│  │ Controllers │ Business Logic  │  │
│  └─────────────┼─────────────────┤  │
│  │    Views    │ API Routing     │  │
│  └─────────────┼─────────────────┤  │
│    Models      │ Data Structure  │  │
│  └─────────────┴─────────────────┘  │
└─────────────────┬───────────────────┘
                  │ Database
┌─────────────────▼───────────────────┐
│         PostgreSQL Database         │
└─────────────────────────────────────┘
```

### Fluxo de Dados

1. **Frontend** → **Controllers** (via HTTP/REST)
2. **Controllers** → **Models** (manipulação de dados)
3. **Models** → **Database** (persistência)
4. **External APIs** → **Controllers** (integrações)

---

## Modularidade de Códigos

### Separação de Responsabilidades

O código está organizado em módulos bem definidos:

#### Backend (`decision-tree-automation-api/backend/`)

```
backend/
├── controllers/           # Lógica de negócio e integrações
│   ├── alerta_controller.py      # Gestão de alertas
│   ├── lider_controller.py       # CRUD de líderes
│   ├── telegram_scheduler.py     # Agendamento de mensagens
│   └── telegram_webhook.py       # Processamento de respostas
├── models/               # Estruturas de dados
│   ├── alerta_model.py           # Modelo de alertas
│   ├── lider_model.py            # Modelo de líderes
│   └── responses_model.py        # Modelo de respostas
├── views/                # Roteamento e apresentação
│   └── api_router.py             # Definição de endpoints
├── main.py              # Ponto de entrada da aplicação
├── config.py            # Configurações globais
└── __init__.py          # Inicialização do pacote
```

#### Frontend (`decision-tree-automation-ui/`)

```
decision-tree-automation-ui/
└── index.html           # Interface web completa
```

### Benefícios da Modularidade

- **Manutenibilidade**: Cada módulo tem responsabilidade específica
- **Testabilidade**: Componentes isolados facilitam testes unitários
- **Escalabilidade**: Novos módulos podem ser adicionados sem afetar existentes
- **Reutilização**: Módulos podem ser reutilizados em outros projetos

---

## Tecnologias Envolvidas

### Backend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| Python | 3.8+ | Linguagem principal |
| FastAPI | Latest | Framework web |
| Uvicorn | Latest | Servidor ASGI |
| SQLAlchemy | Latest | ORM |
| psycopg2-binary | Latest | Driver PostgreSQL |
| python-dotenv | Latest | Variáveis de ambiente |
| requests | Latest | HTTP client |
| pytz | Latest | Fusos horários |

### Frontend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| HTML5 | - | Estrutura da interface |
| CSS3 | - | Estilização |
| JavaScript (ES6+) | - | Interatividade |

### Infraestrutura

| Tecnologia | Propósito |
|------------|-----------|
| PostgreSQL | Banco de dados |
| Telegram Bot API | Integração de mensagens |
| Render | Deploy e hospedagem |

---

## Papel das Tecnologias no Projeto

### Python 3.8+
**Função**: Linguagem base para todo o backend
- **Onde é usado**: Todos os arquivos `.py` do projeto
- **Como é usado**: 
  - Lógica de negócio nos controllers
  - Modelagem de dados com SQLAlchemy
  - Integração com APIs externas
  - Processamento de webhooks do Telegram
- **Exemplo prático**: `alerta_controller.py` usa Python para criar alertas, enviar mensagens e categorizar status

### FastAPI
**Função**: Framework web para construção da API REST
- **Onde é usado**: `main.py`, `api_router.py`, todos os controllers
- **Como é usado**:
  - Criação de endpoints REST (`/alertas`, `/lideres`, `/webhook/telegram`)
  - Validação automática de dados de entrada
  - Documentação automática da API (Swagger/OpenAPI)
  - Middleware para CORS e autenticação
- **Exemplo prático**: `@router.post('/alertas')` cria endpoint para cadastro de alertas

### Uvicorn
**Função**: Servidor ASGI para rodar aplicações FastAPI
- **Onde é usado**: `start.sh`, linha de comando para desenvolvimento
- **Como é usado**:
  - Servidor de desenvolvimento local
  - Servidor de produção no Render
  - Configuração de host, porta e workers
- **Exemplo prático**: `uvicorn backend.main:app --reload` inicia o servidor

### SQLAlchemy
**Função**: ORM para manipulação do banco de dados
- **Onde é usado**: Todos os arquivos em `models/`, `responses_model.py`
- **Como é usado**:
  - Definição de modelos de dados (Alerta, Lider, Resposta)
  - Criação automática de tabelas
  - Queries complexas e filtros
  - Gerenciamento de sessões de banco
- **Exemplo prático**: `class Alerta(Base)` define a estrutura da tabela de alertas

### psycopg2-binary
**Função**: Driver para conexão com PostgreSQL
- **Onde é usado**: `responses_model.py`, `alerta_model.py`
- **Como é usado**:
  - Conexão com banco PostgreSQL
  - Execução de queries SQL
  - Pool de conexões
- **Exemplo prático**: `create_engine(DATABASE_URL)` estabelece conexão

### python-dotenv
**Função**: Carregamento de variáveis de ambiente
- **Onde é usado**: `config.py`, `responses_model.py`
- **Como é usado**:
  - Carrega configurações de arquivo `.env`
  - Configura tokens do Telegram
  - Configura string de conexão do banco
  - Configura IDs de chat
- **Exemplo prático**: `load_dotenv()` carrega `TELEGRAM_BOT_TOKEN`

### requests
**Função**: Cliente HTTP para integrações externas
- **Onde é usado**: `alerta_controller.py`, `telegram_scheduler.py`, `telegram_webhook.py`
- **Como é usado**:
  - Envio de mensagens para API do Telegram
  - Recebimento de webhooks
  - Chamadas HTTP para APIs externas
- **Exemplo prático**: `requests.post(f'{TELEGRAM_API_URL}/sendMessage', data=payload)`

### pytz
**Função**: Manipulação de fusos horários
- **Onde é usado**: `alerta_controller.py`, `telegram_webhook.py`
- **Como é usado**:
  - Conversão de UTC para horário de Brasília
  - Validação de previsões de horário
  - Armazenamento de timestamps corretos
- **Exemplo prático**: `pytz.timezone('America/Sao_Paulo')` define fuso brasileiro

### HTML5/CSS3/JavaScript
**Função**: Interface web do usuário
- **Onde é usado**: `decision-tree-automation-ui/index.html`
- **Como é usado**:
  - Formulários para cadastro de alertas e líderes
  - Tabelas para visualização de categorias
  - Consumo da API via Fetch
  - Atualização automática de dados
- **Exemplo prático**: `fetch('/alertas')` consome endpoint para listar alertas

---

## Razões das Escolhas Tecnológicas

### Python 3.8+
**Por que escolhemos**:
- **Maturidade**: Linguagem estável e amplamente testada
- **Ecossistema**: Vastas bibliotecas para web, banco de dados e integrações
- **Produtividade**: Sintaxe clara e desenvolvimento rápido
- **Comunidade**: Grande suporte e documentação disponível

### FastAPI
**Por que escolhemos**:
- **Performance**: Um dos frameworks Python mais rápidos
- **Tipagem**: Validação automática de dados com Pydantic
- **Documentação**: Gera automaticamente documentação da API
- **Modernidade**: Suporte nativo a async/await
- **Simplicidade**: Curva de aprendizado baixa

### Uvicorn
**Por que escolhemos**:
- **Compatibilidade**: Servidor oficial recomendado para FastAPI
- **Performance**: Implementação ASGI otimizada
- **Configuração**: Fácil configuração para desenvolvimento e produção
- **Estabilidade**: Amplamente testado em produção

### SQLAlchemy
**Por que escolhemos**:
- **Flexibilidade**: Suporte a múltiplos bancos de dados
- **Abstração**: Não trava o projeto em um banco específico
- **Produtividade**: ORM reduz código boilerplate
- **Segurança**: Proteção contra SQL injection
- **Migração**: Facilita mudanças no esquema do banco

### PostgreSQL
**Por que escolhemos**:
- **Confiabilidade**: Banco robusto e testado em produção
- **Recursos**: Suporte a JSON, transações, constraints
- **Performance**: Excelente para aplicações web
- **Comunidade**: Grande suporte e documentação
- **Compatibilidade**: Funciona bem com SQLAlchemy

### psycopg2-binary
**Por que escolhemos**:
- **Padrão**: Driver mais usado para Python + PostgreSQL
- **Performance**: Implementação otimizada em C
- **Estabilidade**: Amplamente testado em produção
- **Compatibilidade**: Funciona perfeitamente com SQLAlchemy

### python-dotenv
**Por que escolhemos**:
- **Segurança**: Separa configurações sensíveis do código
- **Flexibilidade**: Fácil mudança entre ambientes
- **Padrão**: Prática comum em projetos Python
- **Simplicidade**: API simples e intuitiva

### requests
**Por que escolhemos**:
- **Simplicidade**: API muito fácil de usar
- **Confiabilidade**: Biblioteca estável e bem mantida
- **Compatibilidade**: Funciona bem com APIs REST
- **Documentação**: Excelente documentação e exemplos

### pytz
**Por que escolhemos**:
- **Precisão**: Implementação correta de fusos horários
- **Padrão**: Biblioteca padrão para timezone em Python
- **Compatibilidade**: Funciona bem com datetime
- **Manutenção**: Atualizações regulares para mudanças de DST

### HTML5/CSS3/JavaScript (Vanilla)
**Por que escolhemos**:
- **Simplicidade**: Sem dependências externas
- **Performance**: Carregamento rápido
- **Manutenção**: Fácil de entender e modificar
- **Compatibilidade**: Funciona em qualquer navegador moderno
- **Integração**: Consome APIs REST diretamente

---

## Fluxo Principal da Aplicação

1. **Criação de Alerta**: Frontend → Controller → Model → Database
2. **Envio ao Telegram**: Controller → Telegram API (via requests)
3. **Resposta do Líder**: Telegram → Webhook → Controller → Model
4. **Atualização de Status**: Model → Database → Frontend (via API)

---

## Como Executar

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd decision-tree-automation/decision-tree-automation-api

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure variáveis de ambiente
# Crie arquivo .env com:
# DATABASE_URL=postgresql://usuario:senha@host:porta/banco
# TELEGRAM_BOT_TOKEN=seu_token_do_telegram
# CHAT_IDS=123456789,987654321

# 4. Execute o backend
uvicorn backend.main:app --reload

# 5. Abra o frontend
# Abra decision-tree-automation-ui/index.html no navegador
```

---

## Estrutura de Dados

### Alertas
- **Status**: pendente, escalada, atrasada, encerrada
- **Campos**: id, chat_id, problema, previsao, status, nome_lider, timestamps

### Líderes
- **Campos**: id, nome_lider, chat_id

### Respostas
- **Campos**: id, user_id, pergunta, resposta, timestamp

---

## Integrações

### Telegram Bot API
- **Webhook**: `/webhook/telegram` recebe mensagens
- **Envio**: POST para `https://api.telegram.org/bot{token}/sendMessage`
- **Formato**: Respostas devem ser no formato HH:MM

### Banco de Dados
- **Tipo**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migração**: Automática na inicialização

---

## Deploy

### Render
- **Configuração**: `render.yaml`
- **Comando**: `bash start.sh`
- **Variáveis**: Configuradas no painel do Render

---
