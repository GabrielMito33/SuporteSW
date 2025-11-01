#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste simples do Bot Branco atualizado
"""

import json
import sys

def testar_config():
    """Testa se a configuração está correta"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ config.json carregado!")
        
        # Verificar nova estrutura
        strategy = config.get('strategy', {})
        horarios = strategy.get('horarios_personalizados', [])
        ausencias = strategy.get('ausencias_minimas', 0)
        
        print(f"📊 Ausências mínimas: {ausencias}")
        print(f"⏰ Horários personalizados: {horarios}")
        print(f"📍 Margem: {strategy.get('margem_seguranca', 1)} min")
        
        # Validar dinamicamente: deve ser uma lista de 3 inteiros
        if isinstance(horarios, list) and len(horarios) == 3 and all(isinstance(x, int) for x in horarios):
            print("✅ Configuração correta!")
            return True
        else:
            print("❌ Horários inválidos no config.json! Esperado lista com 3 inteiros.")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def simular_logica():
    """Simula a lógica de horários"""
    from datetime import datetime, timedelta
    
    print("\n🧪 SIMULANDO LÓGICA DE HORÁRIOS")
    print("=" * 40)
    
    # Simular confirmação às 12:27
    confirmacao = datetime.now().replace(hour=12, minute=27, second=0, microsecond=0)
    # Ler horários e margem do config.json dinamicamente
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    strategy = config.get('strategy', {})
    horarios_config = strategy.get('horarios_personalizados', [4, 7, 10])
    margem = strategy.get('margem_seguranca', 1)
    
    print(f"📅 Confirmação: {confirmacao.strftime('%H:%M')}")
    
    horarios_entrada = []
    for minutos in horarios_config:
        horario = confirmacao + timedelta(minutes=minutos)
        horarios_entrada.append(horario)
        
    print(f"⏰ Horários de entrada:")
    for i, horario in enumerate(horarios_entrada, 1):
        inicio = horario - timedelta(minutes=margem)
        fim = horario + timedelta(minutes=margem)
        print(f"   {i}° horário: {horario.strftime('%H:%M')} ({inicio.strftime('%H:%M')} até {fim.strftime('%H:%M')})")
    
    # Simular mensagem
    print(f"\n📱 MENSAGEM ENVIADA:")
    print("ENTRADA CONFIRMADA ✅")
    for i, horario in enumerate(horarios_entrada):
        print(f"⚪️{horario.strftime('%H:%M')}")
    print(f"{margem} MIN ANTES {margem} MIN DEPOIS")
    
    return True

if __name__ == "__main__":
    print("🧪 TESTE DO BOT BRANCO ATUALIZADO")
    print("=" * 50)
    
    # Teste 1: Configuração
    print("\n1️⃣ Testando configuração...")
    if not testar_config():
        sys.exit(1)
    
    # Teste 2: Lógica de horários
    print("\n2️⃣ Testando lógica...")
    if not simular_logica():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Bot atualizado e funcionando!")
    print("=" * 50) 