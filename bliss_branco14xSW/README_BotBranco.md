# 🤖 Bot Branco - Blaze Double

Bot automatizado para sinais de **branco (0)** no jogo Blaze Double, baseado em ausências consecutivas e horários programados.

## 📋 **Como Funciona**

O bot monitora a API da Blaze em tempo real e envia sinais quando:
- **Ausências mínimas** de branco são atingidas (padrão: 5)
- Calcula **horários personalizados** (4, 7, 10 minutos após confirmação)
- Detecta **WIN em tempo real** quando branco sai nos horários válidos
- Há **margem de segurança** (1 minuto antes/depois de cada horário)

## 🚀 **Instalação**

### 1. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 2. **Configurar Credenciais**
Edite o arquivo `config.json`:
```json
{
    "telegram": {
        "token": "SEU_TOKEN_DO_BOT_TELEGRAM",
        "chat_id": "SEU_CHAT_ID_OU_GRUPO"
    }
}
```

### 3. **Executar o Bot**
```bash
python BotBranco.py
```

## ⚙️ **Configurações**

### **Estratégia** (`config.json`)
```json
"strategy": {
    "ausencias_minimas": 5,              // Mínimo de ausências para sinal
    "horarios_personalizados": [4, 7, 10], // Horários após confirmação
    "margem_seguranca": 1,               // Minutos antes/depois do horário
    "max_sinais_por_dia": 50             // Limite diário de sinais
}
```

### **Personalizar Configurações**
**Ausências (quantas casas sem branco aguardar):**
```json
"ausencias_minimas": 8   // Mais ausências = sinais mais raros
"ausencias_minimas": 3   // Menos ausências = mais sinais
```

**Horários (minutos após confirmação):**
```json
"horarios_personalizados": [3, 6, 9]    // Horários mais rápidos
"horarios_personalizados": [5, 8, 12]   // Horários mais espaçados
```

## 📱 **Formato da Mensagem**

Quando um sinal é detectado, o bot envia:

```
ENTRADA CONFIRMADA ✅
⚪️12:31
⚪️12:34
⚪️12:37
1 MIN ANTES 1 MIN DEPOIS

📊 Ausências: 18
🎯 Sinais hoje: 5
```

## 📊 **Funcionalidades**

### **✅ Monitoramento Automático**
- Verifica API da Blaze a cada segundo
- Detecta mudanças em tempo real
- Sistema de logs detalhado

### **⏰ Sistema de Horários Personalizados**
- Horários baseados em configuração [4, 7, 10] minutos
- Exemplo: Confirmação 12:27 → Entradas: 12:31, 12:34, 12:37
- Margem de 1 minuto para cada horário (12:30-12:32, 12:33-12:35, 12:36-12:38)
- Detecção automática de WIN quando branco sai nos horários válidos

### **📈 Estatísticas**
- Contador de acertos/erros
- Assertividade em tempo real
- Relatório diário automático
- Limite de sinais por dia

### **🔄 Reset Automático**
- Zera contadores à meia-noite
- Envia relatório do dia anterior
- Logs persistentes

## 🎯 **Como Obter Token do Telegram**

1. **Criar Bot**:
   - Acesse [@BotFather](https://t.me/botfather) no Telegram
   - Digite `/newbot`
   - Escolha nome e username
   - Copie o **token** fornecido

2. **Obter Chat ID**:
   - Adicione seu bot ao grupo/chat
   - Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Procure pelo `"chat":{"id":` no JSON
   - Copie o **chat_id**

## 📁 **Estrutura dos Arquivos**

```
📂 Projeto/
├── 🤖 BotBranco.py         # Bot principal
├── ⚙️ config.json          # Configurações
├── 📋 requirements.txt     # Dependências
├── 📊 bot_branco.log      # Logs (criado automaticamente)
└── 📖 README_BotBranco.md # Documentação
```

## 🔧 **Solução de Problemas**

### **❌ Erro: Token inválido**
- Verifique se o token está correto no `config.json`
- Teste o token: `https://api.telegram.org/bot<TOKEN>/getMe`

### **❌ Erro: Chat não encontrado**
- Certifique-se que o bot foi adicionado ao chat/grupo
- Verifique se o chat_id está correto (pode ser negativo)

### **❌ Erro: API da Blaze**
- Verifique sua conexão com a internet
- A API pode estar temporariamente indisponível

### **🔄 Bot não envia sinais**
- Verifique se as ausências mínimas foram atingidas
- Confirme se está no horário correto (com margem)
- Veja os logs no arquivo `bot_branco.log`

## 📱 **Status no Console**

O bot exibe status a cada minuto:
```
============================================================
🤖 BOT BRANCO - 14:23:15
📊 Ausências: 3/5
⏰ Horários válidos: ['12:31', '12:34', '12:37']
🔄 Em horário WIN: Sim
🎯 Sinal ativo: Sim
📈 Sinais hoje: 3
🏆 Assertividade: 66.7% (2/3)
============================================================
```

## ⚠️ **Aviso Legal**

Este bot é apenas para fins educacionais. Jogos de azar envolvem riscos financeiros. Use com responsabilidade e nunca aposte mais do que pode perder.

## 🛠️ **Suporte**

Para dúvidas ou problemas:
1. Verifique os logs em `bot_branco.log`
2. Teste as configurações no `config.json`
3. Confirme que as dependências estão instaladas

---

**🎯 Bot criado especificamente para sinais de branco no Blaze Double** 