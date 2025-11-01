#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para inicializar o BLISS SINAIS COMPANY CRIADOR
"""

import json
import os
import sys
from bliss_criador_bot import BlissCriadorBot

def carregar_configuracao():
    """Carrega configuração do bot criador"""
    config_file = "config_criador.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Arquivo {config_file} não encontrado!")
        print("📝 Criando arquivo de exemplo...")
        
        config_exemplo = {
            "creator": {
                "token": "SEU_TOKEN_DO_BOT_CRIADOR_AQUI",
                "admin_chat_id": "SEU_CHAT_ID_DE_ADMIN"
            },
            "configuracoes_padrao": {
                "branco": {
                    "ausencias_minimas": 5,
                    "horarios_personalizados": [4, 7, 10],
                    "margem_seguranca": 1,
                    "max_sinais_por_dia": 50
                },
                "double": {
                    "ausencias_minimas": 7,
                    "horarios_personalizados": [2, 5, 8],
                    "margem_seguranca": 1,
                    "max_sinais_por_dia": 50
                }
            },
            "api": {
                "url": "https://blaze.bet.br/api/singleplayer-originals/originals/roulette_games/recent/1",
                "timeout": 10,
                "retry_attempts": 3
            }
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_exemplo, f, indent=4, ensure_ascii=False)
        
        print(f"📝 Configure o token no arquivo {config_file} e execute novamente!")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        token = config['creator']['token']
        if token == "SEU_TOKEN_DO_BOT_CRIADOR_AQUI":
            print("❌ Configure o token do bot criador!")
            print(f"📝 Edite o arquivo {config_file}")
            return None
        
        return config
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 BLISS SINAIS COMPANY CRIADOR")
    print("=" * 50)
    
    # Carregar configuração
    config = carregar_configuracao()
    if not config:
        sys.exit
    
    # Inicializar bot
    try:
        token = config['creator']['token']
        bot_criador = BlissCriadorBot(token)
        bot_criador.iniciar()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 