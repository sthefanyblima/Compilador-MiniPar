#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para compilar todos os programas de teste e gerar executáveis
"""

import os
import sys
import glob

# Ajustar path para importar motor_compilador do diretório Core
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(os.path.dirname(script_dir), 'Core')
sys.path.insert(0, core_dir)
from motor_compilador import compilar_programa_minipar

# Diretório dos testes
testes_dir = os.path.join(os.path.dirname(script_dir), 'Testes')

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
        # Retorna o primeiro encontrado (deve haver apenas um por número de teste)
        return arquivos_encontrados[0]
    
    return None

def extrair_descricao_teste(nome_arquivo):
    """Extrai a descrição do sub-nome do arquivo de teste"""
    # Remove extensão e prefixo "teste"
    nome_base = nome_arquivo.replace('.mp', '').replace('teste', '')
    
    # Se tem underscore, extrai a parte após o número
    if '_' in nome_base:
        partes = nome_base.split('_', 1)
        if len(partes) > 1:
            return partes[1].replace('_', ' ').title()
    
    return ''

def compilar_todos_testes():
    """Compila todos os arquivos teste*.mp e gera executáveis"""
    
    # Lista de arquivos de teste
    arquivos_teste = []
    for i in range(1, 9):
        arquivo = encontrar_arquivo_teste(i)
        if arquivo:
            arquivos_teste.append(arquivo)
    
    if not arquivos_teste:
        print("❌ Nenhum arquivo de teste encontrado!")
        return
    
    print(f"📋 Encontrados {len(arquivos_teste)} arquivos de teste\n")
    print("=" * 70)
    
    resultados = []
    
    for arquivo in arquivos_teste:
        descricao = extrair_descricao_teste(arquivo)
        nome_exibicao = arquivo
        if descricao:
            nome_exibicao = f"{arquivo} ({descricao})"
        print(f"\n🔄 Compilando {nome_exibicao}...")
        print("-" * 70)
        
        try:
            # Ler código fonte
            with open(arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            # Compilar - extrair apenas o nome base do arquivo (sem caminho)
            nome_base = os.path.basename(arquivo).replace('.mp', '')
            resultado = compilar_programa_minipar(
                codigo, 
                nome_arquivo_saida=nome_base,
                gerar_asm=True,
                gerar_executavel=True
            )
            
            resultados.append((arquivo, resultado))
            
            # Exibir resultados
            if resultado['sucesso']:
                print(f"✅ Compilação bem-sucedida!")
                
                if resultado.get('arquivo_asm'):
                    print(f"   📄 Assembly: {resultado['arquivo_asm']}")
                
                if resultado.get('arquivo_executavel'):
                    print(f"   🎯 Executável: {resultado['arquivo_executavel']}")
                elif resultado.get('msg_executavel'):
                    print(f"   ⚠️  {resultado['msg_executavel']}")
                    
            else:
                print(f"❌ Erros encontrados:")
                if resultado.get('erros'):
                    print(f"   {resultado['erros']}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo}: {str(e)}")
            import traceback
            traceback.print_exc()
            resultados.append((arquivo, {'sucesso': False, 'erro': str(e)}))
    
    # Resumo
    print("\n" + "=" * 70)
    print("\n📊 RESUMO DA COMPILAÇÃO\n")
    
    sucesso = sum(1 for _, r in resultados if r.get('sucesso'))
    total = len(resultados)
    
    print(f"Total de programas: {total}")
    print(f"✅ Compilados com sucesso: {sucesso}")
    print(f"❌ Com erros: {total - sucesso}")
    
    if sucesso < total:
        print("\n⚠️  Programas com erros:")
        for arquivo, resultado in resultados:
            if not resultado.get('sucesso'):
                print(f"   - {arquivo}")
                if resultado.get('erros'):
                    print(f"     Erros: {resultado['erros'][:100]}...")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    print("🚀 Compilador MiniPar - Gerador de Executáveis")
    print("=" * 70)
    
    try:
        compilar_todos_testes()
    except KeyboardInterrupt:
        print("\n\n⚠️  Compilação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




