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

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd decision-tree-automation
   ```

2. **Configure as variáveis de ambiente**:
   Crie um arquivo `.env` na pasta `decision-tree-automation-api` com:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
   TELEGRAM_BOT_TOKEN=seu_token_do_bot
   CHAT_IDS=123456789,987654321
   ```

3. **Instale as dependências**:
   ```bash
   cd decision-tree-automation-api
   pip install -r requirements.txt
   ```

4. **Migre a base de dados** (IMPORTANTE):
   ```bash
   python migrate_database.py
   ```

5. **Execute o backend**:
   ```bash
   uvicorn backend.main:app --reload
   ```

6. **Abra o frontend**:
   Abra o arquivo `decision-tree-automation-ui/index.html` no navegador.

7. **Teste os alertas automáticos**:
   ```bash
   python test_scheduler.py
   ```

## Testando o Scheduler de Alertas Automáticos

### Verificação Manual
1. Acesse a aba "Alertas Automáticos" na interface web
2. Clique em "Ativar" para ativar a criação automática
3. Configure o intervalo desejado (ex: 1 minuto para teste)
4. Aguarde o tempo configurado e verifique se novos alertas aparecem

### Debug e Testes
1. **Teste do Scheduler**:
   ```bash
   python test_scheduler.py
   ```

2. **Endpoints de Debug**:
   - `GET /auto-alert/status` - Status da configuração
   - `GET /auto-alert/scheduler-status` - Status detalhado do scheduler
   - `POST /auto-alert/force-create` - Força criação de alerta (debug)
   - `POST /auto-alert/create-now` - Cria alerta manual

3. **Logs do Sistema**:
   - Verifique os logs do console para mensagens do scheduler
   - Procure por mensagens como "Alerta automático criado com sucesso"

### Solução de Problemas

#### Scheduler não está criando alertas:
1. Verifique se está ativo na interface web
2. Confirme o intervalo configurado
3. Use o botão "Forçar Criação (Debug)" para testar
4. Verifique os logs do sistema
5. Execute `python test_scheduler.py` para diagnóstico

#### Alertas não aparecem no frontend:
1. Use Ctrl+F5 para forçar refresh
2. Verifique se o auto-refresh está funcionando (a cada 10s)
3. Confirme se os alertas estão no banco de dados
4. Verifique a categoria "Aguardando Previsão"

#### Scheduler não inicia:
1. Verifique se a configuração existe no banco
2. Confirme se as variáveis de ambiente estão corretas
3. Execute a migração do banco novamente
4. Reinicie o servidor

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

## Alertas Automáticos

### Funcionalidade
O sistema agora inclui criação automática de alertas com dados mockados para demonstração:

- **Geração Automática**: Alertas são criados automaticamente a cada 3 minutos (configurável)
- **Dados Mockados**: Inclui informações realistas como equipamentos, operações e problemas
- **Líder Fixo**: Todos os alertas automáticos são atribuídos ao "Rafael Cabral" (Chat ID: 6435800936)
- **Controle Manual**: Interface para ativar/desativar e criar alertas manualmente

### Endpoints da API

#### GET `/auto-alert/status`
Retorna o status atual da criação automática de alertas.

#### POST `/auto-alert/toggle`
Ativa/desativa a criação automática de alertas.

#### POST `/auto-alert/create-now`
Cria um alerta imediatamente (para teste).

#### POST `/auto-alert/update-interval?interval_minutes=X`
Atualiza o intervalo de criação de alertas (1-60 minutos).

### Interface Web
A aba "Alertas Automáticos" permite:
- Visualizar status atual
- Ativar/desativar criação automática
- Criar alertas manualmente
- Configurar intervalo de criação
- Ver informações sobre a funcionalidade

### Dados Gerados
Os alertas automáticos incluem:
- **Equipamentos**: Colheitadeiras, tratores, plantadeiras, etc.
- **Operações**: Manutenção, troca de filtros, ajustes, etc.
- **Unidades**: Diferentes unidades da empresa
- **Frentes**: Frentes de trabalho variadas
- **Problemas**: Descrições realistas de problemas operacionais

---



## Fluxograma Completo do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FLUXO COMPLETO DO SISTEMA                                │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: CRIAÇÃO DE ALERTA                                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Frontend      │    │   FastAPI       │    │   SQLAlchemy    │    │   PostgreSQL    │ │
│  │   (HTML/JS)     │───▶│   (Controller)  │───▶│   (Model)       │───▶│   (Database)    │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Formulário    │    │ • Validação     │    │ • Criação       │    │ • Persistência  │ │
│  │ • Fetch API     │    │ • Lógica        │    │ • Estrutura     │    │ • Tabela        │ │
│  │ • JavaScript    │    │ • Endpoint      │    │ • Relacionamento│    │ • Constraints   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: HTML5, CSS3, JavaScript (ES6+), FastAPI, SQLAlchemy, PostgreSQL            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ALERTA CRIADO EM "AGUARDANDO PREVISÃO"                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   PostgreSQL    │    │   SQLAlchemy    │    │   FastAPI       │    │   Frontend      │ │
│  │   (Database)    │───▶│   (Model)       │───▶│   (Controller)  │───▶│   (HTML/JS)     │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Status:       │    │ • Query         │    │ • Listagem      │    │ • Tabela        │ │
│  │   "pendente"    │    │ • Filtro        │    │ • Categorização │    │ • Atualização   │ │
│  │ • Timestamp     │    │ • Serialização  │    │ • Endpoint      │    │ • JavaScript    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: PostgreSQL, SQLAlchemy, FastAPI, HTML5, CSS3, JavaScript                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: ENVIO DE MENSAGEM AO TELEGRAM                                                    │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   FastAPI       │    │   requests      │    │   python-dotenv │    │   Telegram      │ │
│  │   (Controller)  │───▶│   (HTTP Client) │───▶│   (Config)      │───▶│   Bot API       │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Lógica        │    │ • POST Request  │    │ • Token         │    │ • Webhook       │ │
│  │ • Payload       │    │ • Headers       │    │ • Chat IDs      │    │ • Message       │ │
│  │ • Validação     │    │ • JSON Data     │    │ • Environment   │    │ • Delivery      │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: FastAPI, requests, python-dotenv, Telegram Bot API                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: LÍDER RECEBE MENSAGEM NO TELEGRAM                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Telegram      │    │   Telegram      │    │   Telegram      │    │   Telegram      │ │
│  │   Bot API       │───▶│   App           │───▶│   User          │───▶│   Interface     │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Message       │    │ • Notification  │    │ • Reading       │    │ • Response      │ │
│  │ • Delivery      │    │ • Alert         │    │ • Analysis      │    │ • Input         │ │
│  │ • Status        │    │ • Sound         │    │ • Decision      │    │ • Send          │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: Telegram Bot API, Telegram App, Telegram Interface                          │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: LÍDER RESPONDE COM PREVISÃO (HH:MM)                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Telegram      │    │   Telegram      │    │   Telegram      │    │   Telegram      │ │
│  │   Interface     │───▶│   App           │───▶│   Bot API       │───▶│   Webhook       │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Text Input    │    │ • Message       │    │ • Update        │    │ • HTTP POST     │ │
│  │ • Send Button   │    │ • Transmission  │    │ • Processing    │    │ • Payload       │ │
│  │ • Validation    │    │ • Encryption    │    │ • Routing       │    │ • Endpoint      │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: Telegram Interface, Telegram App, Telegram Bot API, HTTP Webhook            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: WEBHOOK RECEBE RESPOSTA                                                           │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Telegram      │    │   FastAPI       │    │   pytz          │    │   Python        │ │
│  │   Webhook       │───▶│   (Webhook)     │───▶│   (Timezone)    │───▶│   (Validation)  │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • HTTP POST     │    │ • Endpoint      │    │ • UTC to        │    │ • Time Format   │ │
│  │ • JSON Data     │    │ • JSON Parse    │    │   Brasília      │    │ • HH:MM Check   │ │
│  │ • User Info     │    │ • User ID       │    │ • Conversion    │    │ • Validation    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: HTTP Webhook, FastAPI, pytz, Python 3.8+                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: VALIDAÇÃO E PROCESSAMENTO DA RESPOSTA                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Python        │    │   SQLAlchemy    │    │   PostgreSQL    │    │   FastAPI        │ │
│  │   (Logic)       │───▶│   (Model)       │───▶│   (Database)    │───▶│   (Controller)   │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Time Parse    │    │ • Update Alert  │    │ • Save Response │    │ • Status Update  │ │
│  │ • Format Check  │    │ • Save Response │    │ • Update Alert  │    │ • Logic          │ │
│  │ • Validation    │    │ • Relationship  │    │ • Transaction   │    │ • Categorization │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: Python 3.8+, SQLAlchemy, PostgreSQL, FastAPI                                │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: ATUALIZAÇÃO DE STATUS DO ALERTA                                                   │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   PostgreSQL    │    │   SQLAlchemy    │    │   FastAPI       │    │   Frontend      │ │
│  │   (Database)    │───▶│   (Model)       │───▶│   (Controller)  │───▶│   (HTML/JS)     │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Status Update │    │ • Query         │    │ • Listagem      │    │ • Tabela        │ │
│  │ • Previsão      │    │ • Filtro        │    │ • Categorização │    │ • Atualização   │ │
│  │ • Timestamp     │    │ • Serialização  │    │ • Endpoint      │    │ • JavaScript    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: PostgreSQL, SQLAlchemy, FastAPI, HTML5, CSS3, JavaScript                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: CATEGORIZAÇÃO AUTOMÁTICA DO ALERTA                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Python        │    │   pytz          │    │   SQLAlchemy    │    │   PostgreSQL    │ │
│  │   (Logic)       │───▶│   (Timezone)    │───▶│   (Model)       │───▶│   (Database)    │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Time Compare  │    │ • Current Time  │    │ • Status Update │    │ • Save Status   │ │
│  │ • Business      │    │ • Brasília      │    │ • Category      │    │ • Transaction   │ │
│  │   Rules         │    │ • Conversion    │    │ • Logic         │    │ • Persistence   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: Python 3.8+, pytz, SQLAlchemy, PostgreSQL                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 10: ATUALIZAÇÃO DA INTERFACE FRONTEND                                                │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   PostgreSQL    │    │   SQLAlchemy    │    │   FastAPI       │    │   Frontend      │ │
│  │   (Database)    │───▶│   (Model)       │───▶│   (Controller)  │───▶│   (HTML/JS)     │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Data Query    │    │ • Fetch Data    │    │ • API Response  │    │ • DOM Update    │ │
│  │ • Categories    │    │ • Serialize     │    │ • JSON Format   │    │ • Table Refresh │ │
│  │ • Status Info   │    │ • Filter        │    │ • HTTP Response │    │ • JavaScript    │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: PostgreSQL, SQLAlchemy, FastAPI, HTML5, CSS3, JavaScript                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  STEP 11: VISUALIZAÇÃO DAS CATEGORIAS NO FRONTEND                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   JavaScript    │    │   HTML5         │    │   CSS3          │    │   Browser       │ │
│  │   (Logic)       │───▶│   (Structure)   │───▶│   (Styling)     │───▶│   (Rendering)   │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Data Process  │    │ • Table         │    │ • Colors        │    │ • Display       │ │
│  │ • Category      │    │ • Structure     │    │ • Layout        │    │ • User          │ │
│  │   Logic         │    │ • Elements      │    │ • Responsive    │    │   Interface     │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
│  Tecnologias: JavaScript (ES6+), HTML5, CSS3, Browser Engine                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CATEGORIAS FINAIS                                        │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   Pendentes     │    │   Escaladas     │    │   Atrasadas     │    │   Encerradas    │ │
│  │                 │    │                 │    │                 │    │                 │ │
│  │ • Aguardando    │    │ • Previsão      │    │ • Previsão      │    │ • Previsão      │ │
│  │   Previsão      │    │   fornecida     │    │   Excedida      │    │   Não excedida  │ │
│  │                 │    │ • Não excedida  │    │ • Não operando  │    │ • Operando      │ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### **Resumo das Tecnologias por Etapa:**

#### **Step 1 - Criação de Alerta**
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL

#### **Step 2 - Alerta em "Aguardando Previsão"**
- **Database**: PostgreSQL, SQLAlchemy
- **API**: FastAPI
- **Frontend**: HTML5, CSS3, JavaScript

#### **Step 3 - Envio ao Telegram**
- **Backend**: FastAPI, requests, python-dotenv
- **External**: Telegram Bot API

#### **Step 4 - Recebimento no Telegram**
- **External**: Telegram Bot API, Telegram App, Telegram Interface

#### **Step 5 - Resposta do Líder**
- **External**: Telegram Interface, Telegram App, Telegram Bot API, HTTP Webhook

#### **Step 6 - Processamento do Webhook**
- **Backend**: FastAPI, pytz, Python 3.8+
- **External**: HTTP Webhook

#### **Step 7 - Validação e Processamento**
- **Backend**: Python 3.8+, SQLAlchemy, PostgreSQL, FastAPI

#### **Step 8 - Atualização de Status**
- **Database**: PostgreSQL, SQLAlchemy
- **API**: FastAPI
- **Frontend**: HTML5, CSS3, JavaScript

#### **Step 9 - Categorização Automática**
- **Backend**: Python 3.8+, pytz, SQLAlchemy, PostgreSQL

#### **Step 10 - Atualização Frontend**
- **Database**: PostgreSQL, SQLAlchemy
- **API**: FastAPI
- **Frontend**: HTML5, CSS3, JavaScript

#### **Step 11 - Visualização Final**
- **Frontend**: JavaScript (ES6+), HTML5, CSS3, Browser Engine

## Como Executar

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd decision-tree-automation
   ```

2. **Configure as variáveis de ambiente**:
   Crie um arquivo `.env` na pasta `decision-tree-automation-api` com:
   ```
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
   TELEGRAM_BOT_TOKEN=seu_token_do_bot
   CHAT_IDS=123456789,987654321
   ```

3. **Instale as dependências**:
   ```bash
   cd decision-tree-automation-api
   pip install -r requirements.txt
   ```

4. **Migre a base de dados** (IMPORTANTE):
   ```bash
   python migrate_database.py
   ```

5. **Execute o backend**:
   ```bash
   uvicorn backend.main:app --reload
   ```

6. **Abra o frontend**:
   Abra o arquivo `decision-tree-automation-ui/index.html` no navegador.

7. **Teste os alertas automáticos**:
   ```bash
   python test_scheduler.py
   ```

## Funcionalidades dos Alertas Automáticos

### Controles Disponíveis:
- **Ativar/Desativar**: Botão para ligar/desligar a criação automática
- **Criar Agora**: Botão para criar um alerta imediatamente (teste)
- **Intervalo**: Configuração do tempo entre alertas (padrão: 3 minutos)

### Dados Gerados Automaticamente:
- **Código**: Número único do alerta
- **Unidade**: Unidade operacional (Barra Bonita, Lençóis Paulista, etc.)
- **Frente**: Frente de trabalho (Colheita, Plantio, Manutenção, etc.)
- **Equipamento**: Nome e código do equipamento
- **Tipo de Operação**: Categoria da operação
- **Operação**: Operação específica
- **Operador**: Nome do operador (sempre "Rafael Cabral")
- **Data da Operação**: Data/hora da operação
- **Tempo de Abertura**: Tempo desde a abertura
- **Tipo da Árvore**: Tipo da árvore de decisão
- **Justificativa**: Descrição do problema
- **Prazo**: Prazo para resolução

### Interface Atualizada:
- Todas as categorias (Pendentes, Escaladas, Atrasadas, Encerradas) mostram os novos campos
- Tabelas responsivas com scroll horizontal
- Dados organizados cronologicamente
- Status visual com cores diferenciadas