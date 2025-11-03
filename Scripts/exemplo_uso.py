#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso do motor compilador para gerar executáveis
"""

import os
import sys

# Ajustar path para importar motor_compilador do diretório Core
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(os.path.dirname(script_dir), 'Core')
sys.path.insert(0, core_dir)
from motor_compilador import compilar_programa_minipar

# Exemplo de código MiniPar simples
codigo_exemplo = """
programa-miniPar

SEQ:
    declare x : inteiro
    declare y : inteiro
    
    x = 10
    y = x + 5
    escreva("O valor de y é: ")
    escreva(y)
"""

if __name__ == '__main__':
    print("🔄 Compilando programa exemplo...")
    
    # Compilar e gerar executável
    resultado = compilar_programa_minipar(
        codigo_exemplo,
        nome_arquivo_saida="exemplo",
        gerar_asm=True,
        gerar_executavel=True
    )
    
    # Exibir resultados
    if resultado['sucesso']:
        print("✅ Compilação bem-sucedida!")
        print(f"\n📄 Arquivo Assembly: {resultado.get('arquivo_asm', 'N/A')}")
        print(f"🎯 Executável: {resultado.get('arquivo_executavel', 'N/A')}")
        print(f"\n💬 Mensagens:")
        print(f"   - Assembly: {resultado.get('msg_asm', 'N/A')}")
        print(f"   - Executável: {resultado.get('msg_executavel', 'N/A')}")
    else:
        print("❌ Erros encontrados:")
        print(resultado.get('erros', 'Erros desconhecidos'))




