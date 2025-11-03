#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testar todos os testes e mostrar problemas"""

import sys
import os
import glob

# Ajustar path para importar motor_compilador do diretório Core
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(os.path.dirname(script_dir), 'Core')
sys.path.insert(0, core_dir)
from motor_compilador import (MiniParLexer, MiniParParser, SemanticAnalyzer, 
                              MiniParInterpreter)

# Diretório dos testes
testes_dir = os.path.join(os.path.dirname(script_dir), 'Testes')

# Configurar encoding para UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def encontrar_arquivo_teste(numero_teste):
    """Encontra o arquivo de teste pelo número, considerando sub-nomes descritivos"""
    # Primeiro tenta o arquivo básico
    arquivo_basico = os.path.join(testes_dir, f'teste{numero_teste}.mp')
    if os.path.exists(arquivo_basico):
        return arquivo_basico
    
    # Se não existe, procura arquivos com sub-nomes (ex: teste1_servidor.mp, teste2_threads.mp)
    padrao = os.path.join(testes_dir, f'teste{numero_teste}_*.mp')
    arquivos_encontrados = glob.glob(padrao)
    
    if arquivos_encontrados:
        return arquivos_encontrados[0]
    
    return None

def extrair_descricao_teste(nome_arquivo):
    """Extrai a descrição do sub-nome do arquivo de teste"""
    nome_base = nome_arquivo.replace('.mp', '').replace('teste', '')
    if '_' in nome_base:
        partes = nome_base.split('_', 1)
        if len(partes) > 1:
            return partes[1].replace('_', ' ').title()
    return ''

def testar(teste_num):
    arquivo = encontrar_arquivo_teste(teste_num)
    if not arquivo:
        print(f"\n{'='*70}")
        print(f"TESTE {teste_num} - Arquivo não encontrado")
        print('='*70)
        return
    
    descricao = extrair_descricao_teste(arquivo)
    nome_exibicao = arquivo
    if descricao:
        nome_exibicao = f"{arquivo} ({descricao})"
    
    print(f"\n{'='*70}")
    print(f"TESTE {teste_num} - {nome_exibicao}")
    print('='*70)
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        lexer = MiniParLexer()
        parser = MiniParParser()
        sem = SemanticAnalyzer()
        
        tokens = list(lexer.tokenize(codigo))
        ast = parser.parse(iter(tokens))
        sem.visit(ast)
        
        if sem.errors:
            print(f"❌ Erros semânticos: {sem.errors}")
            return
        
        inter = MiniParInterpreter()
        saida = inter.execute(ast)
        
        print("\n📋 SAÍDA:")
        print("-" * 70)
        print(saida)
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    for i in [1, 2, 3, 4, 5, 6, 7, 8]:
        testar(i)




