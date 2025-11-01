import datetime
import requests
import telebot
import time
import json
import logging
import os
from typing import List, Dict, Optional

class BotBranco:
    
    def __init__(self, config_file: str = "config.json"):
        """Inicializa o bot com configurações do arquivo JSON"""
        self.carregar_configuracoes(config_file)
        self.configurar_logging()
        
        # Estado do sistema
        self.ausencias_branco = 0
        self.ultimo_resultado = []
        self.sinal_ativo = False
        self.horarios_entrada = []  # Lista dos 3 horários de entrada
        self.horario_confirmacao = None  # Horário quando o sinal foi confirmado
        self.sinais_enviados_hoje = 0
        self.data_atual = datetime.date.today()
        self.acertos_sinal_atual = 0  # Contador de acertos do sinal ativo
        self.fim_ultimo_horario_sinal: Optional[datetime.datetime] = None  # Término fixo do último horário do sinal atual
        
        # NOVO: Estado para aguardar próximo branco após WIN
        self.aguardando_proximo_branco = False  # Flag para aguardar outro branco após WIN
        self.ultimo_branco_win = None  # Último resultado que gerou WIN
        
        # Estatísticas
        self.total_sinais = 0
        self.total_acertos = 0
        self.total_erros = 0
        
        # Bot Telegram
        self.bot = telebot.TeleBot(token=self.config['token'], parse_mode="MARKDOWN")
        
        logging.info("🤖 Bot Branco inicializado com sucesso!")
        
    def carregar_configuracoes(self, config_file: str):
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            self.config = config_data.get('telegram', {})
            self.strategy = config_data.get('strategy', {})
            self.api_config = config_data.get('api', {})
            
            # Permitir override por variáveis de ambiente (não logar valores sensíveis)
            token_env = os.environ.get('TELEGRAM_TOKEN')
            chat_id_env = os.environ.get('TELEGRAM_CHAT_ID')
            if token_env:
                self.config['token'] = token_env
            if chat_id_env:
                self.config['chat_id'] = chat_id_env
            
            # Validar configurações obrigatórias
            if not self.config.get('token') or not self.config.get('chat_id'):
                raise ValueError("Token e chat_id são obrigatórios!")
                
        except FileNotFoundError:
            logging.error(f"❌ Arquivo {config_file} não encontrado!")
            self.criar_config_exemplo(config_file)
            raise
        except Exception as e:
            logging.error(f"❌ Erro ao carregar configurações: {e}", exc_info=True)
            raise
    
    def criar_config_exemplo(self, config_file: str):
        """Cria arquivo de configuração exemplo"""
        config_exemplo = {
            "telegram": {
                "token": "SEU_TOKEN_AQUI",
                "chat_id": "SEU_CHAT_ID_AQUI"
            },
            "strategy": {
                "ausencias_minimas": 15,
                "intervalo_horarios": 3,
                "margem_seguranca": 1,
                "max_sinais_por_dia": 50
            },
            "api": {
                "url": "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1",
                "timeout": 10,
                "retry_attempts": 3
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_exemplo, f, indent=4, ensure_ascii=False)
            
        print(f"📝 Arquivo {config_file} criado! Configure suas credenciais.")
    
    def configurar_logging(self):
        """Configura sistema de logs"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_branco.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def calcular_horarios_entrada(self):
        """Calcula os 3 horários de entrada baseados na configuração personalizada"""
        agora = datetime.datetime.now()
        horarios_config = self.strategy.get('horarios_personalizados', [4, 7, 10])
        
        self.horario_confirmacao = agora.replace(second=0, microsecond=0)
        self.horarios_entrada = []
        
        for minutos in horarios_config:
            horario = self.horario_confirmacao + datetime.timedelta(minutes=minutos)
            self.horarios_entrada.append(horario)
        
        horarios_str = [h.strftime('%H:%M') for h in self.horarios_entrada]
        logging.info(f"⏰ Horários calculados: {horarios_str}")
        
        return [h.strftime('%H:%M') for h in self.horarios_entrada]
    
    def contar_ausencias_branco(self, resultados: List[int]) -> int:
        """Conta resultados consecutivos sem branco (0)"""
        ausencias = 0
        for resultado in resultados:
            if resultado == 0:  # Branco encontrado
                break
            ausencias += 1
        return ausencias
    
    def verificar_horario_para_sinal(self) -> bool:
        """Verifica se devemos enviar sinal (sem sinal ativo e não aguardando próximo branco)"""
        # Só pode enviar sinal se não há sinal ativo E não está aguardando próximo branco após WIN
        return not self.sinal_ativo and not self.aguardando_proximo_branco
    
    def verificar_horario_para_win(self) -> bool:
        """Verifica se estamos em algum horário válido para WIN"""
        if not self.sinal_ativo or not self.horarios_entrada:
            return False
            
        agora = datetime.datetime.now()
        margem = self.strategy.get('margem_seguranca', 1)
        
        # Verificar se estamos em algum dos 3 horários (com margem)
        for horario in self.horarios_entrada:
            inicio_janela = horario - datetime.timedelta(minutes=margem)
            fim_janela = horario + datetime.timedelta(minutes=margem)
            
            if inicio_janela <= agora <= fim_janela:
                return True
                
        return False
    
    def verificar_fim_dos_horarios(self) -> bool:
        """Verifica se já passou de todos os horários válidos"""
        if not self.horarios_entrada:
            return False
            
        agora = datetime.datetime.now()
        # Preferir o término fixado no momento do envio do sinal
        if self.fim_ultimo_horario_sinal is not None:
            return agora > self.fim_ultimo_horario_sinal
        # Fallback: calcular dinamicamente
        margem = self.strategy.get('margem_seguranca', 1)
        ultimo_horario = self.horarios_entrada[-1]
        fim_ultimo_horario = ultimo_horario + datetime.timedelta(minutes=margem)
        return agora > fim_ultimo_horario
    
    def enviar_sinal_branco(self):
        """Envia sinal de entrada para branco"""
        if self.sinais_enviados_hoje >= self.strategy.get('max_sinais_por_dia', 50):
            logging.warning("⚠️ Limite diário de sinais atingido!")
            return
            
        # Calcular horários baseados na configuração
        horarios = self.calcular_horarios_entrada()
        margem = self.strategy.get('margem_seguranca', 1)
        # Fixar término do último horário para este sinal (evita finalizar antes da hora)
        if self.horarios_entrada:
            self.fim_ultimo_horario_sinal = self.horarios_entrada[-1] + datetime.timedelta(minutes=margem)
        else:
            self.fim_ultimo_horario_sinal = None
        
        mensagem = f"""ENTRADA CONFIRMADA ✅
⚪️{horarios[0]}
⚪️{horarios[1]}
⚪️{horarios[2]}
{margem} MIN ANTES {margem} MIN DEPOIS

[🎯 BLAZE DOUBLE](https://blaze.bet.br/r/6jEa6)
"""
        
        try:
            self.bot.send_message(self.config['chat_id'], mensagem)
            
            self.sinal_ativo = True
            self.total_sinais += 1
            self.sinais_enviados_hoje += 1
            self.acertos_sinal_atual = 0  # Resetar contador para o novo sinal
            
            logging.info(f"🎯 Sinal enviado! Ausências: {self.ausencias_branco}")
            logging.info(f"⏰ Horários válidos: {horarios}")
            if self.fim_ultimo_horario_sinal:
                logging.info(
                    f"🕒 Fim do último horário deste sinal: {self.fim_ultimo_horario_sinal.strftime('%H:%M:%S')}"
                )
            
        except Exception as e:
            logging.error(f"❌ Erro ao enviar sinal: {e}", exc_info=True)
    
    def enviar_win(self):
        """Envia mensagem de WIN quando acerta"""
        try:
            # Capturar horário atual quando o branco sai
            horario_branco = datetime.datetime.now().strftime('%H:%M')
            win_message = f"GREEN BRANCO-⚪️✅({horario_branco})"
            self.bot.send_message(self.config['chat_id'], win_message)
            
            self.total_acertos += 1
            self.acertos_sinal_atual += 1  # Incrementar acertos do sinal atual
            
            # NOVO: Ativar flag para aguardar próximo branco
            self.aguardando_proximo_branco = True
            self.ultimo_branco_win = 0  # Marcar que o último branco gerou WIN
            
            logging.info(f"🎉 WIN! Branco saiu no horário válido! ({horario_branco}) - Aguardando próximo branco para nova tabela")
            
        except Exception as e:
            logging.error(f"❌ Erro ao enviar WIN: {e}", exc_info=True)
    
    def enviar_loss(self):
        """Envia mensagem de LOSS quando não acerta ou finaliza sinal"""
        try:
            # Verificar se houve pelo menos um acerto durante o sinal atual ANTES de resetar
            houve_acertos = self.acertos_sinal_atual > 0
            
            if houve_acertos:
                # Se houve acertos, apenas finalizar o sinal sem contar como erro
                loss_message = "⏰ Sinal finalizado! Todos os horários foram analisados."
                logging.info("✅ Sinal finalizado - houve acertos durante os horários")
            else:
                # Se não houve acertos, contar como LOSS
                loss_message = "Não veio ! Analisando Possível entrada!🎯"
                self.total_erros += 1
                logging.info(loss_message)

            self.bot.send_message(self.config['chat_id'], loss_message)
            
            self.sinal_ativo = False  # Resetar sinal
            self.horarios_entrada = []  # Limpar horários
            self.acertos_sinal_atual = 0  # Resetar contador de acertos do sinal
            self.fim_ultimo_horario_sinal = None  # Limpar término fixado do sinal
            
            # NOVO: Manter aguardando próximo branco se houve WIN
            if houve_acertos:
                logging.info("🔄 Aguardando próximo branco para nova tabela de horários")
                # Manter as flags ativas para aguardar próximo branco
            else:
                self.aguardando_proximo_branco = False  # Resetar se não houve WIN
                self.ultimo_branco_win = None
            
        except Exception as e:
            logging.error(f"❌ Erro ao enviar mensagem de finalização: {e}", exc_info=True)
    
    def verificar_resultado_sinal(self, ultimo_resultado: int):
        """Verifica resultado quando há sinal ativo"""
        if not self.sinal_ativo:
            return
            
        # Se saiu branco, verificar se está em horário válido
        if ultimo_resultado == 0:  # Branco
            if self.verificar_horario_para_win():
                self.enviar_win()
                # NÃO fazer return aqui - continuar monitorando até o final
            else:
                logging.info("⚪️ Branco fora do horário válido")
        
        # Verificar se já passou de todos os horários
        if self.verificar_fim_dos_horarios():
            self.enviar_loss()
    
    def coletar_dados_api(self) -> List[int]:
        """Coleta dados da API da Blaze com tentativas e backoff exponencial"""
        url = self.api_config.get('url')
        timeout = self.api_config.get('timeout', 10)
        tentativas = self.api_config.get('retry_attempts', 3)
        intervalo = 1.0
        
        for tentativa in range(1, max(1, tentativas) + 1):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                json_data = response.json()
                resultados = [item['roll'] for item in json_data]
                return resultados
            except requests.exceptions.RequestException as e:
                logging.error(
                    f"❌ Erro na API (tentativa {tentativa}/{tentativas}): {e}",
                    exc_info=True
                )
                if tentativa < tentativas:
                    time.sleep(intervalo)
                    intervalo *= 2
            except Exception as e:
                logging.error(f"❌ Erro ao processar dados: {e}", exc_info=True)
                break
        return []
    
    def analisar_resultados(self, resultados: List[int]):
        """Analisa resultados e decide se deve enviar sinal"""
        if not resultados:
            return
            
        # Verificar se houve mudança
        if resultados == self.ultimo_resultado:
            return
            
        self.ultimo_resultado = resultados.copy()
        
        # Verificar resultado do sinal ativo (WIN/LOSS em tempo real)
        if self.sinal_ativo:
            self.verificar_resultado_sinal(resultados[0])

        # Sempre contar ausências para fins de log
        self.ausencias_branco = self.contar_ausencias_branco(resultados)

        # NOVO: Verificar se estamos aguardando próximo branco após WIN
        if self.aguardando_proximo_branco and resultados[0] == 0:
            # Se estamos aguardando próximo branco e saiu branco, resetar flag
            self.aguardando_proximo_branco = False
            self.ultimo_branco_win = None
            logging.info("🔄 Próximo branco detectado após WIN - pronto para nova tabela")
            logging.info("📊 Resetando contagem de ausências para nova sequência")
            # IMPORTANTE: Não enviar sinal imediatamente após detectar o próximo branco
            # Aguardar que as ausências se acumulem novamente

        # Parâmetros atuais de estratégia
        ausencias_min = self.strategy.get('ausencias_minimas', 5)
        pode_enviar_sinal = self.verificar_horario_para_sinal()

        # Log mais detalhado do estado atual
        if self.aguardando_proximo_branco:
            logging.info(f"⏳ Aguardando próximo branco após WIN - não enviando sinais")
        else:
            logging.info(
                f"📊 Ausências: {self.ausencias_branco}/{ausencias_min} | Pode enviar: {pode_enviar_sinal} | Ativo: {self.sinal_ativo}"
            )

        # Disparo do sinal - SÓ se pode enviar sinal (não aguardando próximo branco)
        if pode_enviar_sinal:
            if ausencias_min <= 0:
                # Estratégia: confirmar entrada imediatamente ao detectar BRANCO (0)
                if resultados[0] == 0:
                    self.enviar_sinal_branco()
            else:
                # Estratégia tradicional baseada em ausências
                if self.ausencias_branco >= ausencias_min:
                    self.enviar_sinal_branco()
    
    def verificar_novo_dia(self):
        """Verifica se é um novo dia e reseta contadores"""
        hoje = datetime.date.today()
        if hoje != self.data_atual:
            self.data_atual = hoje
            self.sinais_enviados_hoje = 0
            
            # Enviar relatório do dia anterior
            self.enviar_relatorio_diario()
            
            logging.info("📅 Novo dia iniciado - contadores resetados")
    
    def enviar_relatorio_diario(self):
        """Envia relatório de performance diária"""
        if self.total_sinais > 0:
            assertividade = (self.total_acertos / self.total_sinais) * 100
        else:
            assertividade = 0
            
        relatorio = f"""📊 RELATÓRIO DIÁRIO - BOT BRANCO

✅ Acertos: {self.total_acertos}
❌ Erros: {self.total_erros}
🎯 Total de sinais: {self.total_sinais}
📈 Assertividade: {assertividade:.1f}%

📅 Data: {self.data_atual.strftime('%d/%m/%Y')}"""
        
        try:
            self.bot.send_message(self.config['chat_id'], relatorio)
        except Exception as e:
            logging.error(f"❌ Erro ao enviar relatório: {e}", exc_info=True)
    
    def exibir_status(self):
        """Exibe status atual no console"""
        agora = datetime.datetime.now()
        ausencias_min = self.strategy.get('ausencias_minimas', 5)
        
        print(f"\n{'='*60}")
        print(f"🤖 BOT BRANCO - {agora.strftime('%H:%M:%S')}")
        print(f"📊 Ausências: {self.ausencias_branco}/{ausencias_min}")
        
        if self.aguardando_proximo_branco:
            print(f"⏳ AGUARDANDO PRÓXIMO BRANCO após WIN")
            print(f"🎯 Sinal ativo: {'Sim' if self.sinal_ativo else 'Não'}")
        elif self.sinal_ativo and self.horarios_entrada:
            horarios_str = [h.strftime('%H:%M') for h in self.horarios_entrada]
            print(f"⏰ Horários válidos: {horarios_str}")
            print(f"🔄 Em horário WIN: {'Sim' if self.verificar_horario_para_win() else 'Não'}")
            print(f"🎯 Sinal ativo: Sim")
        else:
            print(f"⏰ Aguardando ausências para próximo sinal")
            print(f"🎯 Sinal ativo: Não")
            
        print(f"🔄 Aguardando próximo branco: {'Sim' if self.aguardando_proximo_branco else 'Não'}")
        print(f"📈 Sinais hoje: {self.sinais_enviados_hoje}")
        if self.total_sinais > 0:
            assertividade = (self.total_acertos / self.total_sinais) * 100
            print(f"🏆 Assertividade: {assertividade:.1f}% ({self.total_acertos}/{self.total_sinais})")
        print(f"{'='*60}")
    
    def iniciar(self):
        """Inicia o monitoramento do bot"""
        logging.info("🚀 Iniciando Bot Branco...")
        
        # Exibir configurações
        horarios_config = self.strategy.get('horarios_personalizados', [4, 7, 10])
        print(f"⚪️ Ausências mínimas: {self.strategy.get('ausencias_minimas', 5)}")
        print(f"⏰ Horários: {horarios_config} minutos após confirmação")
        print(f"📍 Margem: {self.strategy.get('margem_seguranca', 1)} minuto(s)")
        print(f"🎯 Sistema de WIN em tempo real ativado!")
        print(f"🔄 Aguardando próximo branco após WIN ativado!")
        
        contador_status = 0
        
        while True:
            try:
                # Verificar novo dia
                self.verificar_novo_dia()
                
                # Coletar e analisar dados
                resultados = self.coletar_dados_api()
                if resultados:
                    self.analisar_resultados(resultados)
                
                # Exibir status periodicamente
                contador_status += 1
                if contador_status >= 60:  # A cada minuto
                    self.exibir_status()
                    contador_status = 0
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot interrompido pelo usuário")
                if self.total_sinais > 0:
                    self.enviar_relatorio_diario()
                break
            except Exception as e:
                logging.error(f"❌ Erro inesperado: {e}", exc_info=True)
                time.sleep(5)


if __name__ == "__main__":
    import sys
    
    # Verificar se foi passado arquivo de config específico
    config_file = "config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    try:
        bot = BotBranco(config_file)
        bot.iniciar()
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        print(f"📝 Verifique o arquivo {config_file} e suas configurações") 