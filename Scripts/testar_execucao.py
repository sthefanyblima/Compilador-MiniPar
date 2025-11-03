#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para testar a execução dos programas de teste"""

import os
import sys
import glob

# Ajustar path para importar motor_compilador do diretório Core
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(os.path.dirname(script_dir), 'Core')
sys.path.insert(0, core_dir)
from motor_compilador import (MiniParLexer, MiniParParser, SemanticAnalyzer, 
                              MiniParInterpreter)

# Diretório dos testes
testes_dir = os.path.join(os.path.dirname(script_dir), 'Testes')

def encontrar_arquivo_teste(numero_teste):
    """Encontra o arquivo de teste pelo número, considerando sub-nomes descritivos"""
    arquivo_basico = os.path.join(testes_dir, f'teste{numero_teste}.mp')
    if os.path.exists(arquivo_basico):
        return arquivo_basico
    
    padrao = os.path.join(testes_dir, f'teste{numero_teste}_*.mp')
    arquivos_encontrados = glob.glob(padrao)
    
    if arquivos_encontrados:
        return arquivos_encontrados[0]
    
    return None

def testar_execucao(arquivo_mp):
    """Testa a execução de um programa MiniPar"""
    print(f"\n{'='*60}")
    print(f"Testando: {arquivo_mp}")
    print('='*60)
    
    try:
        # Ler código
        with open(arquivo_mp, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        # Compilar
        lexer = MiniParLexer()
        parser = MiniParParser()
        sem = SemanticAnalyzer()
        
        tokens = list(lexer.tokenize(codigo))
        ast = parser.parse(iter(tokens))
        sem.visit(ast)
        
        if sem.errors:
            print(f"❌ Erros semânticos: {sem.errors}")
            return
        
        # Executar
        interpreter = MiniParInterpreter()
        
        # Determinar entrada baseada no programa
        entrada = ""
        if "teste1" in arquivo_mp:
            entrada = "+\n10\n5"
        elif "teste3" in arquivo_mp:
            entrada = ""  # Não precisa entrada
        
        saida = interpreter.execute(ast, entrada)
        
        print("\n📋 SAÍDA DO PROGRAMA:")
        print("-" * 60)
        print(saida)
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Testar cada arquivo de teste
    for i in range(1, 9):
        arquivo = encontrar_arquivo_teste(i)
        if arquivo:
            try:
                testar_execucao(arquivo)
            except FileNotFoundError:
                print(f"Arquivo {arquivo} não encontrado")
        else:
            print(f"Arquivo teste{i}.mp não encontrado")



