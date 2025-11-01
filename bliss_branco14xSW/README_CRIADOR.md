# 🎯 BLISS SINAIS COMPANY CRIADOR

Bot do Telegram responsável por criar e gerenciar salas de sinais personalizadas para Double e Branco.

## 🚀 Funcionalidades

- ✅ **Criação automática de salas de sinais**
- ✅ **Suporte para modos Double e Branco**
- ✅ **Gerenciamento de múltiplas salas**
- ✅ **Validação automática de configurações**
- ✅ **Interface amigável via Telegram**

## 📋 Pré-requisitos

1. **Python 3.7+** instalado
2. **Bibliotecas necessárias:**
   ```bash
   pip install telebot requests
   ```
3. **Token do bot criador** (obtido via @BotFather)

## ⚙️ Configuração

### 1. Configure o Bot Criador

1. Crie um bot no @BotFather
2. Copie o token gerado
3. Execute o script para gerar o arquivo de configuração:
   ```bash
   python iniciar_criador.py
   ```
4. Edite o arquivo `config_criador.json` com seu token:
   ```json
   {
       "creator": {
           "token": "SEU_TOKEN_AQUI",
           "admin_chat_id": "SEU_CHAT_ID"
       }
   }
   ```

### 2. Inicie o Bot Criador

```bash
python iniciar_criador.py
```

## 🎮 Como Usar

### 📱 **No Telegram:**

1. **Inicie uma conversa** com seu bot criador
2. **Digite `/start`** para ver as opções
3. **Use `/criar_sala`** para criar uma nova sala

### 🏗️ **Criando uma Sala:**

Envie os dados no formato:
```
TOKEN: 1234567890:ABCdefGHI...
CANAL: -1001234567890
MODO: branco
```

**Onde:**
- **TOKEN:** Token do bot que enviará os sinais
- **CANAL:** ID do canal/grupo (deve começar com -)
- **MODO:** `branco` ou `double`

### 📊 **Comandos Disponíveis:**

| Comando | Descrição |
|---------|-----------|
| `/start` | Mensagem de boas-vindas |
| `/help` | Ajuda detalhada |
| `/criar_sala` | Criar nova sala de sinais |
| `/minhas_salas` | Listar salas ativas |
| `/parar_sala` | Parar uma sala específica |

## 🔧 Configurações Automáticas

### **Modo Branco:**
- **Ausências mínimas:** 5
- **Horários:** 4, 7, 10 minutos
- **Margem:** 1 minuto

### **Modo Double:**
- **Ausências mínimas:** 7
- **Horários:** 2, 5, 8 minutos
- **Margem:** 1 minuto

## 🛡️ Validações

O sistema valida automaticamente:
- ✅ **Formato do token** (deve conter :)
- ✅ **ID do canal** (deve começar com - e ter 10+ dígitos)
- ✅ **Modo válido** (branco ou double)
- ✅ **Permissões do bot** (teste de envio)

## 📂 Estrutura de Arquivos

```
📁 Projeto/
├── 🤖 bliss_criador_bot.py     # Bot criador principal
├── ⚙️ config_criador.json      # Configurações do criador
├── 🚀 iniciar_criador.py       # Script de inicialização
├── 🎯 BotBranco.py             # Bot de sinais branco
├── 📝 README_CRIADOR.md        # Este arquivo
└── 📊 config_sala_*.json       # Configs das salas criadas
```

## 🎯 Exemplo de Uso Completo

### 1. **Usuário no Telegram:**
```
/criar_sala
```

### 2. **Bot responde:**
```
🏗️ CRIANDO NOVA SALA DE SINAIS

Por favor, envie os dados no formato abaixo:

TOKEN: seu_token_aqui
CANAL: -1001234567890
MODO: branco
```

### 3. **Usuário envia:**
```
TOKEN: 1234567890:ABCdefGHI...
CANAL: -1001234567890
MODO: branco
```

### 4. **Bot confirma:**
```
✅ SALA CRIADA COM SUCESSO!

🆔 ID da Sala: sala_123456_1234567890
🎯 Modo: BRANCO
📢 Canal: -1001234567890
⏰ Criada em: 15/12/2024 14:30

🚀 Sua sala está ativa e funcionando!
```

## 🔄 Gerenciamento de Salas

### **Ver Salas Ativas:**
```
/minhas_salas
```

### **Parar uma Sala:**
```
/parar_sala sala_123456_1234567890
```

## 🆘 Suporte

- 📞 **Telegram:** @bliss_suporte
- 📧 **Email:** suporte@blisssinais.com
- 📖 **Documentação:** [Link da documentação]

## 🔒 Segurança

- ✅ **Tokens são validados** antes do uso
- ✅ **Arquivos de configuração** são únicos por sala
- ✅ **Processos isolados** para cada bot
- ✅ **Logs detalhados** para debugging

---

**© 2024 BLISS SINAIS COMPANY - Todos os direitos reservados** 