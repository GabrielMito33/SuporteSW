#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BLISS SINAIS COMPANY CRIADOR
Bot responsável por criar salas de sinais personalizadas
"""

import telebot
import json
import logging
import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, Optional
import sys

class BlissCriadorBot:
    
    def __init__(self, creator_token: str):
        """Inicializa o bot criador"""
        self.creator_token = creator_token
        self.bot = telebot.TeleBot(creator_token, parse_mode="MARKDOWN")
        self.salas_ativas = {}  # Dicionário com salas criadas
        self.processos_bots = {}  # Processos dos bots ativos
        
        # Configurar logging
        self.configurar_logging()
        
        # Registrar handlers
        self.registrar_handlers()
        
        logging.info("🤖 BLISS SINAIS COMPANY CRIADOR inicializado!")
    
    def configurar_logging(self):
        """Configura sistema de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bliss_criador.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def registrar_handlers(self):
        """Registra os handlers de comandos"""
        
        @self.bot.message_handler(commands=['start'])
        def comando_start(message):
            self.enviar_boas_vindas(message)
        
        @self.bot.message_handler(commands=['help'])
        def comando_help(message):
            self.enviar_ajuda(message)
        
        @self.bot.message_handler(commands=['criar_sala'])
        def comando_criar_sala(message):
            self.iniciar_criacao_sala(message)
        
        @self.bot.message_handler(commands=['minhas_salas'])
        def comando_minhas_salas(message):
            self.listar_salas_usuario(message)
        
        @self.bot.message_handler(commands=['parar_sala'])
        def comando_parar_sala(message):
            self.parar_sala(message)
        
        @self.bot.message_handler(func=lambda message: True)
        def processar_mensagem(message):
            self.processar_dados_sala(message)
    
    def enviar_boas_vindas(self, message):
        """Envia mensagem de boas-vindas"""
        welcome_text = """🎯 **BLISS SINAIS COMPANY CRIADOR** 🎯

Bem-vindo ao criador oficial de salas de sinais!

🚀 **O que posso fazer:**
• Criar salas de sinais personalizadas
• Configurar bots Double ou Branco
• Gerenciar suas salas ativas

📋 **Comandos disponíveis:**
/criar_sala - Criar nova sala de sinais
/minhas_salas - Ver suas salas ativas
/parar_sala - Parar uma sala específica
/help - Ajuda detalhada

💡 **Para começar:**
Digite /criar_sala e siga as instruções!

📞 **Suporte:** @bliss_suporte"""

        self.bot.send_message(message.chat.id, welcome_text)
    
    def enviar_ajuda(self, message):
        """Envia ajuda detalhada"""
        help_text = """📖 **AJUDA - BLISS CRIADOR**

🔧 **Como criar uma sala:**

1️⃣ Digite /criar_sala
2️⃣ Forneça os dados solicitados:
   • Token do seu bot
   • ID do canal/grupo
   • Modo (double/branco)

📝 **Formato dos dados:**
```
TOKEN: 1234567890:ABC...
CANAL: -1001234567890
MODO: double
```

⚠️ **Importante:**
• O token deve ser válido
• Você deve ser admin do canal
• Modos disponíveis: `double` ou `branco`

🎯 **Exemplo completo:**
```
TOKEN: 1234567890:ABCdefGHI...
CANAL: -1001234567890
MODO: branco
```

📊 **Gerenciamento:**
• Use /minhas_salas para ver salas ativas
• Use /parar_sala ID para parar uma sala

💬 **Suporte:** @bliss_suporte"""

        self.bot.send_message(message.chat.id, help_text)
    
    def iniciar_criacao_sala(self, message):
        """Inicia o processo de criação de sala"""
        user_id = message.from_user.id
        
        # Verificar se usuário já tem sala sendo criada
        if user_id in self.salas_ativas and 'pendente' in str(self.salas_ativas[user_id]):
            self.bot.send_message(
                message.chat.id, 
                "⚠️ Você já tem uma sala sendo criada! Complete o processo atual primeiro."
            )
            return
        
        # Inicializar dados da sala
        self.salas_ativas[user_id] = {
            'status': 'aguardando_dados',
            'dados_recebidos': {},
            'chat_id': message.chat.id
        }
        
        instrucoes = """🏗️ **CRIANDO NOVA SALA DE SINAIS**

Por favor, envie os dados no formato abaixo:

```
TOKEN: seu_token_aqui
CANAL: -1001234567890
MODO: double
```

📋 **Instruções:**
• **TOKEN:** Token do bot que enviará os sinais
• **CANAL:** ID do canal/grupo (com o hífen)
• **MODO:** `double` ou `branco`

⚡ **Envie tudo em uma única mensagem!**"""

        self.bot.send_message(message.chat.id, instrucoes)
    
    def processar_dados_sala(self, message):
        """Processa os dados da sala enviados pelo usuário"""
        user_id = message.from_user.id
        
        # Verificar se usuário está criando sala
        if user_id not in self.salas_ativas or self.salas_ativas[user_id]['status'] != 'aguardando_dados':
            return
        
        try:
            dados = self.extrair_dados_mensagem(message.text)
            
            if not dados:
                self.bot.send_message(
                    message.chat.id,
                    "❌ Formato inválido! Use:\n\n```\nTOKEN: seu_token\nCANAL: -1001234567890\nMODO: double\n```"
                )
                return
            
            # Validar dados
            if self.validar_dados_sala(dados):
                self.criar_sala_sinais(message, dados)
            else:
                self.bot.send_message(
                    message.chat.id,
                    "❌ Dados inválidos! Verifique o token, canal e modo."
                )
                
        except Exception as e:
            logging.error(f"Erro ao processar dados: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ Erro ao processar dados. Tente novamente."
            )
    
    def extrair_dados_mensagem(self, texto: str) -> Optional[Dict]:
        """Extrai dados da mensagem do usuário"""
        try:
            linhas = texto.strip().split('\n')
            dados = {}
            
            for linha in linhas:
                if ':' in linha:
                    chave, valor = linha.split(':', 1)
                    chave = chave.strip().upper()
                    valor = valor.strip()
                    
                    if chave == 'TOKEN':
                        dados['token'] = valor
                    elif chave == 'CANAL':
                        dados['canal'] = valor
                    elif chave == 'MODO':
                        dados['modo'] = valor.lower()
            
            # Verificar se todos os dados foram fornecidos
            if all(key in dados for key in ['token', 'canal', 'modo']):
                return dados
            
            return None
            
        except Exception as e:
            logging.error(f"Erro ao extrair dados: {e}")
            return None
    
    def validar_dados_sala(self, dados: Dict) -> bool:
        """Valida os dados fornecidos para a sala"""
        try:
            # Validar modo
            if dados['modo'] not in ['double', 'branco']:
                return False
            
            # Validar formato do canal (deve começar com - e ter pelo menos 10 dígitos)
            canal = dados['canal']
            if not (canal.startswith('-') and len(canal) >= 10 and canal[1:].isdigit()):
                return False
            
            # Validar formato básico do token
            token = dados['token']
            if ':' not in token or len(token) < 20:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Erro na validação: {e}")
            return False
    
    def criar_sala_sinais(self, message, dados: Dict):
        """Cria a sala de sinais com os dados fornecidos"""
        user_id = message.from_user.id
        
        try:
            # Gerar ID único para a sala
            sala_id = f"sala_{user_id}_{int(time.time())}"
            
            # Criar arquivo de configuração
            config_sala = self.criar_config_sala(dados, sala_id)
            
            # Tentar enviar mensagem de teste
            if self.testar_bot_configuracao(dados):
                # Salvar sala
                self.salas_ativas[user_id] = {
                    'status': 'ativa',
                    'sala_id': sala_id,
                    'dados': dados,
                    'config_file': config_sala,
                    'criada_em': datetime.now().isoformat(),
                    'chat_id': message.chat.id
                }
                
                # Iniciar bot da sala
                self.iniciar_bot_sala(sala_id, config_sala, dados['modo'])
                
                sucesso_msg = f"""✅ **SALA CRIADA COM SUCESSO!**

🆔 **ID da Sala:** `{sala_id}`
🎯 **Modo:** {dados['modo'].upper()}
📢 **Canal:** `{dados['canal']}`
⏰ **Criada em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

🚀 **Sua sala está ativa e funcionando!**

📊 **Comandos úteis:**
• /minhas_salas - Ver todas as salas
• /parar_sala {sala_id} - Parar esta sala

💡 Os sinais começarão a ser enviados automaticamente!"""

                self.bot.send_message(message.chat.id, sucesso_msg)
                
            else:
                self.bot.send_message(
                    message.chat.id,
                    "❌ **Erro na configuração!**\n\nVerifique se:\n• O token é válido\n• O bot é admin do canal\n• O canal existe"
                )
                
        except Exception as e:
            logging.error(f"Erro ao criar sala: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ Erro interno. Tente novamente ou contate o suporte."
            )
    
    def criar_config_sala(self, dados: Dict, sala_id: str) -> str:
        """Cria arquivo de configuração para a sala"""
        config = {
            "telegram": {
                "token": dados['token'],
                "chat_id": dados['canal']
            },
            "strategy": {
                "ausencias_minimas": 5 if dados['modo'] == 'branco' else 7,
                "horarios_personalizados": [4, 7, 10] if dados['modo'] == 'branco' else [2, 5, 8],
                "margem_seguranca": 1,
                "max_sinais_por_dia": 50
            },
            "api": {
                "url": "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1",
                "timeout": 10,
                "retry_attempts": 3
            }
        }
        
        config_file = f"config_{sala_id}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        return config_file
    
    def testar_bot_configuracao(self, dados: Dict) -> bool:
        """Testa se a configuração do bot está correta"""
        try:
            test_bot = telebot.TeleBot(dados['token'])
            test_bot.send_message(
                dados['canal'], 
                "🔧 **TESTE DE CONFIGURAÇÃO**\n\nSua sala foi criada com sucesso!"
            )
            return True
        except Exception as e:
            logging.error(f"Erro no teste: {e}")
            return False
    
    def iniciar_bot_sala(self, sala_id: str, config_file: str, modo: str):
        """Inicia o bot da sala em processo separado"""
        try:
            if modo == 'branco':
                cmd = [sys.executable, 'BotBranco.py', config_file]
            else:
                # Verificar existência do arquivo para evitar erro silencioso
                if not os.path.exists('BotDouble.py'):
                    logging.error("BotDouble.py não encontrado. Modo 'double' ainda não suportado.")
                    return
                cmd = [sys.executable, 'BotDouble.py', config_file]

            # Iniciar processo sem pipes não consumidos
            processo = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )

            self.processos_bots[sala_id] = processo
            logging.info(f"Bot da sala {sala_id} iniciado com PID {processo.pid}")

        except Exception as e:
            logging.error(f"Erro ao iniciar bot da sala: {e}", exc_info=True)
    
    def listar_salas_usuario(self, message):
        """Lista as salas ativas do usuário"""
        user_id = message.from_user.id
        
        if user_id not in self.salas_ativas or self.salas_ativas[user_id]['status'] != 'ativa':
            self.bot.send_message(
                message.chat.id,
                "📭 **Você não tem salas ativas.**\n\nUse /criar_sala para criar uma nova sala!"
            )
            return
        
        sala = self.salas_ativas[user_id]
        dados = sala['dados']
        
        lista_msg = f"""📊 **SUAS SALAS ATIVAS**

🆔 **ID:** `{sala['sala_id']}`
🎯 **Modo:** {dados['modo'].upper()}
📢 **Canal:** `{dados['canal']}`
⏰ **Criada:** {datetime.fromisoformat(sala['criada_em']).strftime('%d/%m/%Y %H:%M')}
🟢 **Status:** ATIVA

🛑 **Para parar:** /parar_sala {sala['sala_id']}"""

        self.bot.send_message(message.chat.id, lista_msg)
    
    def parar_sala(self, message):
        """Para uma sala específica"""
        user_id = message.from_user.id
        
        if user_id not in self.salas_ativas:
            self.bot.send_message(message.chat.id, "❌ Você não tem salas ativas.")
            return
        
        sala = self.salas_ativas[user_id]
        sala_id = sala['sala_id']
        
        try:
            # Parar processo do bot
            if sala_id in self.processos_bots:
                self.processos_bots[sala_id].terminate()
                del self.processos_bots[sala_id]
            
            # Remover arquivo de config
            if os.path.exists(sala['config_file']):
                os.remove(sala['config_file'])
            
            # Remover da lista
            del self.salas_ativas[user_id]
            
            self.bot.send_message(
                message.chat.id,
                f"🛑 **Sala {sala_id} foi parada com sucesso!**"
            )
            
        except Exception as e:
            logging.error(f"Erro ao parar sala: {e}")
            self.bot.send_message(
                message.chat.id,
                "❌ Erro ao parar a sala. Contate o suporte."
            )
    
    def iniciar(self):
        """Inicia o bot criador"""
        print("🚀 BLISS SINAIS COMPANY CRIADOR")
        print("=" * 50)
        print("🤖 Bot iniciado e aguardando comandos...")
        print("📞 Suporte: @bliss_suporte")
        print("=" * 50)
        
        try:
            self.bot.polling(none_stop=True)
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido pelo usuário")
            self.parar_todos_bots()
        except Exception as e:
            logging.error(f"Erro no bot: {e}")
    
    def parar_todos_bots(self):
        """Para todos os bots ativos"""
        for sala_id, processo in self.processos_bots.items():
            try:
                processo.terminate()
                logging.info(f"Bot da sala {sala_id} finalizado")
            except:
                pass


if __name__ == "__main__":
    print("🚀 BLISS SINAIS COMPANY CRIADOR")
    print("=" * 50)
    print("💡 Use 'python iniciar_criador.py' para inicialização completa")
    print("📝 Este arquivo é apenas a classe principal do bot")
    print("=" * 50) 