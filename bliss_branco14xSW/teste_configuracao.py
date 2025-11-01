#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar as configurações do Bot Branco
Execute este script antes de usar o bot principal
"""

import json
import requests
import telebot
from datetime import datetime

def testar_config():
    """Testa se o arquivo config.json existe e está válido"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ config.json carregado com sucesso!")
        
        # Verificar estrutura
        required_keys = ['telegram', 'strategy', 'api']
        for key in required_keys:
            if key not in config:
                print(f"❌ Chave '{key}' não encontrada no config.json")
                return False
        
        # Verificar telegram
        telegram = config['telegram']
        if not telegram.get('token') or telegram['token'] == "SEU_TOKEN_AQUI":
            print("❌ Token do Telegram não configurado!")
            return False
            
        if not telegram.get('chat_id') or telegram['chat_id'] == "SEU_CHAT_ID_AQUI":
            print("❌ Chat ID não configurado!")
            return False
        
        print("✅ Configurações básicas OK!")
        return config
        
    except FileNotFoundError:
        print("❌ Arquivo config.json não encontrado!")
        return False
    except json.JSONDecodeError:
        print("❌ Erro ao ler config.json - formato inválido!")
        return False

def testar_telegram(config):
    """Testa conexão com o Telegram"""
    try:
        token = config['telegram']['token']
        chat_id = config['telegram']['chat_id']
        
        # Testar bot
        bot = telebot.TeleBot(token)
        bot_info = bot.get_me()
        
        print(f"✅ Bot conectado: @{bot_info.username}")
        
        # Testar envio de mensagem
        test_message = f"""🧪 TESTE DO BOT BRANCO
        
⏰ {datetime.now().strftime('%H:%M:%S')}
✅ Configurações OK!
🤖 Bot funcionando corretamente!

Este é um teste automático."""
        
        sent_message = bot.send_message(chat_id, test_message)
        print(f"✅ Mensagem de teste enviada com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Telegram: {e}")
        return False

def testar_api_blaze(config):
    """Testa conexão com a API da Blaze"""
    try:
        url = config['api']['url']
        timeout = config['api']['timeout']
        
        print(f"🔗 Testando API: {url}")
        
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or not isinstance(data, list):
            print("❌ Formato de resposta da API inválido!")
            return False
        
        # Mostrar alguns resultados
        resultados = [item['roll'] for item in data[:10]]
        print(f"✅ API funcionando! Últimos resultados: {resultados}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na API da Blaze: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao processar dados da API: {e}")
        return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = ['requests', 'telebot', 'json', 'datetime']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Execute: pip install {dep}")
            return False
    
    return True

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONFIGURAÇÃO - BOT BRANCO")
    print("=" * 50)
    
    # 1. Verificar dependências
    print("\n1️⃣ Verificando dependências...")
    if not verificar_dependencias():
        print("\n❌ Instale as dependências antes de continuar!")
        return
    
    # 2. Testar configurações
    print("\n2️⃣ Testando configurações...")
    config = testar_config()
    if not config:
        print("\n❌ Configure o arquivo config.json antes de continuar!")
        return
    
    # 3. Testar API da Blaze
    print("\n3️⃣ Testando API da Blaze...")
    if not testar_api_blaze(config):
        print("\n❌ Problemas com a API da Blaze!")
        return
    
    # 4. Testar Telegram
    print("\n4️⃣ Testando Telegram...")
    if not testar_telegram(config):
        print("\n❌ Problemas com o Telegram!")
        return
    
    # Sucesso!
    print("\n" + "=" * 50)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Seu bot está pronto para funcionar!")
    print("\n🚀 Execute: python BotBranco.py")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}") 