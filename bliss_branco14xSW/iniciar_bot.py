#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simplificado para iniciar o Bot Branco
Com verificações básicas e configuração fácil
"""

import os
import sys
import json

def verificar_config():
    """Verifica se config.json existe e está configurado"""
    if not os.path.exists('config.json'):
        print("❌ Arquivo config.json não encontrado!")
        print("📝 Executando: python teste_configuracao.py para criar")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Verificar se está configurado
        telegram = config.get('telegram', {})
        token_env = os.environ.get('TELEGRAM_TOKEN')
        chat_id_env = os.environ.get('TELEGRAM_CHAT_ID')

        # Se as variáveis de ambiente estiverem definidas, aceitar mesmo com placeholders
        if token_env and chat_id_env:
            return True

        if (telegram.get('token') == "SEU_TOKEN_AQUI" or 
            telegram.get('chat_id') == "SEU_CHAT_ID_AQUI"):
            print("❌ Credenciais não configuradas!")
            print("🎯 Opções:")
            print("   1) Edite config.json com token e chat_id válidos")
            print("   2) OU defina variáveis de ambiente TELEGRAM_TOKEN e TELEGRAM_CHAT_ID")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler config.json: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 INICIANDO BOT BRANCO")
    print("=" * 40)
    
    # Verificar configurações
    if not verificar_config():
        print("\n📋 PASSOS PARA CONFIGURAR:")
        print("1. python teste_configuracao.py")
        print("2. Editar config.json com suas credenciais")
        print("3. python iniciar_bot.py")
        return
    
    print("✅ Configurações OK!")
    print("🤖 Iniciando Bot Branco...\n")
    
    # Importar e iniciar bot
    try:
        from BotBranco import BotBranco
        bot = BotBranco()
        bot.iniciar()
        
    except ImportError:
        print("❌ Arquivo BotBranco.py não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot interrompido pelo usuário")
        print("👋 Até logo!") 