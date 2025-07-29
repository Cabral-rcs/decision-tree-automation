# Correção: Alertas de Atrasadas → Encerradas

## 🎯 Objetivo
Implementar a funcionalidade para permitir que alertas da categoria "Atrasadas" possam ser movidos para "Encerradas" quando o status de operação mudar de "não operando" para "operando", e identificar visualmente esses alertas com texto vermelho.

## ✅ Correções Implementadas

### 1. **Novo Campo no Modelo de Dados**
**Arquivo**: `backend/models/alerta_model.py`

Adicionado campo `origem_encerramento` para rastrear a origem do alerta quando encerrado:

```python
origem_encerramento = Column(String, nullable=True)  # 'escalada' ou 'atrasada'
```

### 2. **Lógica de Rastreamento no Controller**
**Arquivo**: `backend/controllers/alerta_controller.py`

Atualizada a função `atualizar_status_operacao` para rastrear a origem:

```python
# Se mudou para operando, salva o horário e rastreia origem
if novo_status == 'operando':
    tz_br = pytz.timezone('America/Sao_Paulo')
    alerta.horario_operando = datetime.now(tz_br)
    # Se mudou para operando, vai para encerradas (tanto de escalada quanto de atrasada)
    if alerta.status in ['escalada', 'atrasada']:
        # Rastreia a origem do encerramento ANTES de mudar o status
        if alerta.status == 'atrasada':
            alerta.origem_encerramento = 'atrasada'
        elif alerta.status == 'escalada':
            alerta.origem_encerramento = 'escalada'
        alerta.status = 'encerrada'
        logger.info(f"Alerta {alerta_id} encerrado - origem: {alerta.origem_encerramento}")
```

### 3. **API Atualizada**
**Arquivo**: `backend/controllers/alerta_controller.py`

Adicionado campo `origem_encerramento` na resposta da API para alertas encerrados:

```python
"encerradas": [
    {
        # ... outros campos ...
        "origem_encerramento": a.origem_encerramento,
        # ... outros campos ...
    } for a in encerradas
]
```

### 4. **Frontend Atualizado**
**Arquivo**: `decision-tree-automation-ui/index.html`

#### Nova função para determinar cor do texto:
```javascript
function getEncerradoTextColor(a) {
    // Usa o novo campo origem_encerramento se disponível
    if (a.origem_encerramento) {
        if (a.origem_encerramento === 'atrasada') {
            return 'color: #dc3545; font-weight: bold;'; // Vermelho - veio de atrasadas
        } else {
            return 'color: #28a745; font-weight: bold;'; // Verde - veio de escaladas
        }
    }
    
    // Fallback para lógica antiga (compatibilidade)
    // ... lógica de fallback ...
}
```

#### Função de background atualizada:
```javascript
function getEncerradoBackground(a) {
    // Usa o novo campo origem_encerramento se disponível
    if (a.origem_encerramento) {
        if (a.origem_encerramento === 'atrasada') {
            return 'background-color: #ffe6e6;'; // Vermelho claro - veio de atrasadas
        } else {
            return 'background-color: #e6ffe6;'; // Verde claro - veio de escaladas
        }
    }
    
    // Fallback para lógica antiga (compatibilidade)
    // ... lógica de fallback ...
}
```

#### Aplicação da cor do texto:
```javascript
<td><span style="${getEncerradoTextColor(a)}">${a.previsao || '-'}</span></td>
```

## 🔄 Fluxo de Funcionamento

### Fluxo Normal (Escaladas → Encerradas)
1. Alerta criado → **Pendente**
2. Líder informa previsão → **Escalada**
3. Status muda para "operando" → **Encerrada** (texto verde, background verde claro)

### Fluxo de Recuperação (Atrasadas → Encerradas)
1. Alerta criado → **Pendente**
2. Líder informa previsão → **Escalada**
3. Previsão expira → **Atrasada**
4. Status muda para "operando" → **Encerrada** (texto vermelho, background vermelho claro)

## 🎨 Cores de Identificação

### Alertas Encerrados que vieram de Escaladas:
- **Texto**: Verde (`#28a745`)
- **Background**: Verde claro (`#e6ffe6`)

### Alertas Encerrados que vieram de Atrasadas:
- **Texto**: Vermelho (`#dc3545`)
- **Background**: Vermelho claro (`#ffe6e6`)

## 🧪 Testes Implementados

### 1. Teste Local
**Arquivo**: `teste_local_atrasadas_encerradas.py`
- Testa a lógica de backend localmente
- Verifica se o campo `origem_encerramento` é preenchido corretamente
- Confirma que alertas são movidos para encerradas

### 2. Teste de Produção
**Arquivo**: `teste_correcao_atrasadas_encerradas.py`
- Testa a funcionalidade completa via API
- Verifica se alertas atrasados podem ser movidos para encerradas
- Confirma se o campo de origem é retornado pela API

## 📋 Checklist de Funcionalidades

- ✅ Campo `origem_encerramento` adicionado ao modelo
- ✅ Lógica de rastreamento implementada no controller
- ✅ API retorna campo de origem para alertas encerrados
- ✅ Frontend identifica origem usando novo campo
- ✅ Texto vermelho para alertas que vieram de atrasadas
- ✅ Background diferenciado por origem
- ✅ Lógica de fallback para compatibilidade
- ✅ Testes locais e de produção implementados

## 🚀 Como Testar

### Teste Local:
```bash
python teste_local_atrasadas_encerradas.py
```

### Teste de Produção:
```bash
python teste_correcao_atrasadas_encerradas.py
```

### Teste Manual:
1. Acesse a interface web
2. Crie um alerta atrasado (ou use o botão de teste)
3. Verifique se aparece na categoria "Atrasadas"
4. Clique no botão "Operando" para mudar o status
5. Verifique se o alerta vai para "Encerradas" com texto vermelho

## 🔧 Arquivos Modificados

1. **Backend**:
   - `backend/models/alerta_model.py` - Novo campo origem_encerramento
   - `backend/controllers/alerta_controller.py` - Lógica de rastreamento e API

2. **Frontend**:
   - `decision-tree-automation-ui/index.html` - Funções de cor e renderização

3. **Testes**:
   - `teste_local_atrasadas_encerradas.py` - Teste local
   - `teste_correcao_atrasadas_encerradas.py` - Teste de produção

## 📝 Próximos Passos

1. **Deploy das correções** para o servidor
2. **Teste em produção** com alertas reais
3. **Monitoramento** para garantir que as funcionalidades estão funcionando corretamente
4. **Documentação** para usuários finais sobre a nova funcionalidade

## 🎯 Resultado Esperado

Após o deploy das correções:
- ✅ Alertas de atrasadas podem ser movidos para encerradas
- ✅ Alertas encerrados que vieram de atrasadas têm texto vermelho
- ✅ Alertas encerrados que vieram de escaladas têm texto verde
- ✅ Background diferenciado por origem
- ✅ Rastreamento completo da origem do encerramento 