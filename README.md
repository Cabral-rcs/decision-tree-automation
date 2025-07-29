# Decision Tree Automation - Prova de Conceito

Sistema de automação de decisões baseado em alertas operacionais, com integração ao Telegram para comunicação com líderes e interface web para gestão. Este projeto é uma **prova de conceito** que demonstra a viabilidade de automatizar processos de tomada de decisão em ambientes operacionais.

##  Funcionalidades

### **Gestão de Alertas**
- **Criação Manual**: Interface web para criar alertas operacionais
- **Criação Automática**: Scheduler que gera alertas automaticamente com dados mockados
- **Categorização Inteligente**: Sistema automático de categorização baseado em previsões e status
- **Controle de Status**: Mudança de status operacional (operando/não operando)

### **Integração Telegram**
- **Webhook Automático**: Recebimento de mensagens em tempo real
- **Validação de Usuário**: Apenas líderes autorizados podem responder
- **Processamento de Previsões**: Conversão automática de respostas HH:MM em previsões
- **Confirmação**: Feedback automático para o líder

### **Interface Web**
- **Visualização em Tempo Real**: Auto-refresh a cada 3 segundos
- **Categorização Visual**: Cores diferenciadas por status e origem
- **Controle de Scheduler**: Ativação/desativação de alertas automáticos
- **Ações Administrativas**: Limpeza de dados e configurações

### **Sistema de Categorização**
- **Pendentes**: Alertas aguardando previsão do líder
- **Escaladas**: Alertas com previsão futura e equipamento não operando
- **Atrasadas**: Alertas com previsão expirada e equipamento não operando
- **Encerradas**: Alertas com equipamento operando (independente da previsão)

## 🛠️ Tecnologias Envolvidas

### **Backend**
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.8+ | Linguagem principal do backend |
| **FastAPI** | 0.104.0+ | Framework web moderno e rápido |
| **Uvicorn** | 0.24.0+ | Servidor ASGI para FastAPI |
| **SQLAlchemy** | 2.0.0+ | ORM para manipulação de banco de dados |
| **SQLite** | - | Banco de dados em memória (dados zerados a cada deploy) |
| **python-dotenv** | 1.0.0+ | Gerenciamento de variáveis de ambiente |
| **requests** | 2.31.0+ | Cliente HTTP para integrações externas |
| **pytz** | 2023.3+ | Manipulação de fusos horários |

### **Frontend**
| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **HTML5** | - | Estrutura da interface web |
| **CSS3** | - | Estilização e responsividade |
| **JavaScript (ES6+)** | - | Interatividade e comunicação com API |

### **Infraestrutura**
| Tecnologia | Propósito |
|------------|-----------|
| **Render.com** | Deploy e hospedagem em nuvem |
| **Telegram Bot API** | Integração de mensagens |
| **Webhooks** | Comunicação em tempo real |

## 🔧 Papel de Cada Tecnologia

### **Python 3.8+**
- **Função**: Linguagem base para todo o backend
- **Onde é usado**: Todos os arquivos `.py` do projeto
- **Como é usado**: 
  - Lógica de negócio nos controllers
  - Modelagem de dados com SQLAlchemy
  - Integração com APIs externas
  - Processamento de webhooks do Telegram

### **FastAPI**
- **Função**: Framework web para construção da API REST
- **Onde é usado**: `main.py`, `api_router.py`, todos os controllers
- **Como é usado**:
  - Criação de endpoints REST (`/alertas`, `/auto-alert`, `/telegram-webhook`)
  - Validação automática de dados de entrada
  - Documentação automática da API (Swagger/OpenAPI)
  - Middleware para CORS e autenticação

### **Uvicorn**
- **Função**: Servidor ASGI para rodar aplicações FastAPI
- **Onde é usado**: `start.sh`, linha de comando para desenvolvimento
- **Como é usado**:
  - Servidor de desenvolvimento local
  - Servidor de produção no Render
  - Configuração de host, porta e workers

### **SQLAlchemy**
- **Função**: ORM para manipulação do banco de dados
- **Onde é usado**: Todos os arquivos em `models/`
- **Como é usado**:
  - Definição de modelos de dados (Alerta, AutoAlertConfig, Response)
  - Criação automática de tabelas
  - Queries complexas e filtros
  - Gerenciamento de sessões de banco

### **SQLite**
- **Função**: Banco de dados em memória
- **Onde é usado**: `config.py`, todos os models
- **Como é usado**:
  - Armazenamento temporário de dados
  - Dados zerados a cada deploy (prova de conceito)
  - Configuração simples sem dependências externas

### **python-dotenv**
- **Função**: Carregamento de variáveis de ambiente
- **Onde é usado**: `config.py`
- **Como é usado**:
  - Carrega configurações de arquivo `.env`
  - Configura tokens do Telegram
  - Configura IDs de chat
  - Configura string de conexão do banco

### **requests**
- **Função**: Cliente HTTP para integrações externas
- **Onde é usado**: `alerta_controller.py`, `telegram_webhook.py`, `auto_alert_scheduler.py`
- **Como é usado**:
  - Envio de mensagens para API do Telegram
  - Recebimento de webhooks
  - Chamadas HTTP para APIs externas

### **pytz**
- **Função**: Manipulação de fusos horários
- **Onde é usado**: `alerta_controller.py`, `telegram_webhook.py`
- **Como é usado**:
  - Conversão de UTC para horário de Brasília
  - Validação de previsões de horário
  - Armazenamento de timestamps corretos

### **HTML5/CSS3/JavaScript**
- **Função**: Interface web do usuário
- **Onde é usado**: `decision-tree-automation-ui/index.html`
- **Como é usado**:
  - Formulários para cadastro de alertas
  - Tabelas para visualização de categorias
  - Consumo da API via Fetch
  - Atualização automática de dados

### **Render.com**
- **Função**: Plataforma de deploy e hospedagem
- **Onde é usado**: `render.yaml`, `start.sh`
- **Como é usado**:
  - Deploy automático do código
  - Hospedagem da aplicação
  - Configuração de variáveis de ambiente
  - Health checks automáticos

### **Telegram Bot API**
- **Função**: Integração de mensagens
- **Onde é usado**: Controllers e services
- **Como é usado**:
  - Envio de mensagens para líderes
  - Recebimento de respostas via webhook
  - Validação de usuários autorizados
  - Processamento de previsões

##  Modularidade do Código

### **Separação de Responsabilidades**

O projeto segue o padrão **MVC (Model-View-Controller)** com modularidade bem definida:

#### **Backend (`decision-tree-automation-api/backend/`)**
```
backend/
├── controllers/           # Lógica de negócio e integrações
│   ├── alerta_controller.py      # Gestão de alertas
│   ├── auto_alert_controller.py  # Controle de alertas automáticos
│   ├── telegram_scheduler.py     # Agendamento de mensagens
│   └── telegram_webhook.py       # Processamento de respostas
├── models/               # Estruturas de dados
│   ├── alerta_model.py           # Modelo de alertas
│   ├── auto_alert_config_model.py # Configuração de alertas automáticos
│   └── responses_model.py        # Modelo de respostas
├── services/             # Serviços auxiliares
│   ├── auto_alert_scheduler.py   # Scheduler de alertas automáticos
│   └── mock_data_generator.py    # Geração de dados mockados
├── views/                # Roteamento e apresentação
│   └── api_router.py             # Definição de endpoints
├── main.py              # Ponto de entrada da aplicação
├── config.py            # Configurações globais
└── __init__.py          # Inicialização do pacote
```

#### **Frontend (`decision-tree-automation-ui/`)**
```
decision-tree-automation-ui/
└── index.html           # Interface web completa
```

### **Benefícios da Modularidade**

- **Manutenibilidade**: Cada módulo tem responsabilidade específica
- **Testabilidade**: Componentes isolados facilitam testes unitários
- **Escalabilidade**: Novos módulos podem ser adicionados sem afetar existentes
- **Reutilização**: Módulos podem ser reutilizados em outros projetos


##  Integração Telegram

### **Configuração do Bot**
- **Token**: Configurado via variável de ambiente `TELEGRAM_BOT_TOKEN`
- **Webhook**: Configurado automaticamente na inicialização
- **URL**: `https://decision-tree-automation-1.onrender.com/telegram-webhook`

### **Fluxo de Mensagens**
1. **Alerta Criado**: Sistema envia mensagem para o líder
2. **Líder Responde**: Formato HH:MM (ex: 15:30)
3. **Webhook Recebe**: Processa a resposta automaticamente
4. **Validação**: Verifica se é usuário autorizado (Rafael Cabral)
5. **Processamento**: Converte resposta em previsão
6. **Atualização**: Atualiza alerta no banco de dados
7. **Confirmação**: Envia confirmação para o líder

### **Validações**
- **Usuário Autorizado**: Apenas Rafael Cabral (ID: 6435800936)
- **Formato de Resposta**: Deve ser HH:MM
- **Alerta Pendente**: Deve existir alerta aguardando previsão
- **Timezone**: Conversão automática para horário de Brasília

### **Endpoints Telegram**
- `POST /telegram-webhook` - Recebe mensagens do Telegram
- `POST /telegram-set-webhook` - Configura webhook
- `GET /telegram-webhook-info` - Status do webhook
- `POST /telegram-force-setup` - Força reconfiguração

##  Fluxo Geral do Sistema

### **1. Criação de Alertas**

#### **Criação Manual**
1. **Frontend** → Usuário preenche formulário
2. **JavaScript** → Envia dados via Fetch para `/alertas`
3. **Controller** → Valida dados e cria alerta no banco
4. **Telegram** → Envia mensagem para o líder
5. **Frontend** → Atualiza interface automaticamente

#### **Criação Automática**
1. **Scheduler** → Executa a cada X minutos (configurável)
2. **Mock Generator** → Gera dados realistas de alertas
3. **Controller** → Cria alerta automaticamente
4. **Telegram** → Envia mensagem para o líder
5. **Configuração** → Atualiza última execução

### **2. Processamento de Respostas**

#### **Recebimento via Webhook**
1. **Telegram** → Envia mensagem para webhook
2. **Controller** → Valida usuário e formato
3. **Banco** → Busca alerta mais antigo sem previsão
4. **Processamento** → Converte HH:MM em datetime
5. **Atualização** → Salva previsão e timestamps
6. **Confirmação** → Envia confirmação para líder

### **3. Categorização Automática**

#### **Regras de Negócio**
```python
# 1. Pendentes: Alertas sem previsão
if not alerta.previsao:
    pendentes.append(alerta)

# 2. Encerradas: Status operando (independente da previsão)
elif alerta.status_operacao == 'operando':
    encerradas.append(alerta)

# 3. Escaladas: Previsão não excedida + status não operando
elif previsao_datetime >= now:
    escaladas.append(alerta)

# 4. Atrasadas: Previsão excedida + status não operando
else:
    atrasadas.append(alerta)
```

#### **Fluxo de Categorização**
1. **Pendente** → Aguarda resposta do líder
2. **Escalada** → Previsão futura, equipamento não operando
3. **Atrasada** → Previsão expirada, equipamento não operando
4. **Encerrada** → Equipamento operando (independente da previsão)

### **4. Mudança de Status**

#### **Fluxo de Transição**
1. **Usuário** → Clica no botão de status no frontend
2. **JavaScript** → Envia requisição PUT para `/alertas/{id}/status`
3. **Controller** → Atualiza status_operacao no banco
4. **Rastreamento** → Salva origem do encerramento (escalada/atrasada)
5. **Categorização** → Alerta é recategorizado automaticamente
6. **Interface** → Frontend atualiza visualização

### **5. Visualização em Tempo Real**

#### **Auto-refresh**
- **Frequência**: A cada 3 segundos
- **Verificação**: Endpoint `/alertas/ultima-atualizacao`
- **Atualização**: Recarrega dados se houver mudanças
- **Notificação**: Mostra alertas visuais de atualizações

#### **Cores Diferenciadas**
- **Pendentes**: Texto cinza "Aguardando resposta"
- **Escaladas**: Texto azul com previsão
- **Atrasadas**: Texto vermelho com previsão
- **Encerradas**: 
  - Verde (veio de escaladas)
  - Vermelho (veio de atrasadas)

##  Como Executar

### **1. Configuração Local**
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd decision-tree-automation

# Configure as variáveis de ambiente
cd decision-tree-automation-api
# Crie arquivo .env com:
# DATABASE_URL=sqlite:///temp_database.db
# TELEGRAM_BOT_TOKEN=seu_token_do_bot
# CHAT_IDS=6435800936
```

### **2. Instalação**
```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a migração do banco
python migrate_database.py
```

### **3. Execução**
```bash
# Inicie o backend
uvicorn backend.main:app --reload

# Abra o frontend
# Arquivo: decision-tree-automation-ui/index.html
```

### **4. Deploy no Render**
- **Configuração**: `render.yaml` já configurado
- **Script**: `start.sh` executa automaticamente
- **Variáveis**: Configure no painel do Render
- **URL**: https://decision-tree-automation-1.onrender.com


## Endpoints da API

### **Alertas**
- `GET /alertas` - Lista alertas categorizados
- `POST /alertas` - Cria novo alerta
- `PUT /alertas/{id}/status` - Atualiza status operacional
- `DELETE /alertas/all` - Apaga todos os alertas

### **Alertas Automáticos**
- `GET /auto-alert/status` - Status do scheduler
- `POST /auto-alert/toggle` - Ativa/desativa criação automática
- `POST /auto-alert/create-now` - Cria alerta manualmente
- `POST /auto-alert/update-interval?interval_minutes=X` - Configura intervalo

### **Telegram**
- `POST /telegram-webhook` - Recebe mensagens
- `POST /telegram-set-webhook` - Configura webhook
- `GET /telegram-webhook-info` - Status do webhook

### **Sistema**
- `GET /health` - Health check
- `GET /debug` - Informações do ambiente
- `GET /database-status` - Status do banco


**Prova de Conceito** - Este projeto demonstra a viabilidade de automatizar processos de tomada de decisão em ambientes operacionais através de integração com mensageiros e interface web responsiva.