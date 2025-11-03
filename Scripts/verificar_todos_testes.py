#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar se todos os testes compilam corretamente"""

import os
import sys

# Ajustar path para importar motor_compilador do diretório Core
script_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(os.path.dirname(script_dir), 'Core')
sys.path.insert(0, core_dir)
from motor_compilador import compilar_programa_minipar

# Diretório dos testes
testes_dir = os.path.join(os.path.dirname(script_dir), 'Testes')

testes = [
    'teste1_servidor.mp',
    'teste2_threads.mp',
    'teste3_neuronio.mp',
    'teste4_XOR.mp',
    'teste5_rede_neural.mp',
    'teste6_fatorial.mp',
    'teste7_fibonacci.mp',
    'teste8_quicksort.mp'
]

print("=" * 70)
print("VERIFICAÇÃO DE COMPATIBILIDADE DOS TESTES")
print("=" * 70)

resultados = []

for teste in testes:
    print(f"\n[{teste}]")
    print("-" * 70)
    
    teste_path = os.path.join(testes_dir, teste)
    if not os.path.exists(teste_path):
        print(f"[ERRO] Arquivo {teste} nao encontrado")
        resultados.append((teste, False, "Arquivo nao encontrado"))
        continue
    
    try:
        codigo = open(teste_path, encoding='utf-8').read()
        resultado = compilar_programa_minipar(codigo, teste.replace('.mp', ''), True, False)
        
        if resultado['sucesso']:
            print("[OK] Compilacao bem-sucedida")
            
            # Verificar se o arquivo .s foi gerado (no diretório atual ou Testes)
            arquivo_s = teste.replace('.mp', '.s')
            if not os.path.exists(arquivo_s):
                arquivo_s = os.path.join(testes_dir, teste.replace('.mp', '.s'))
            if os.path.exists(arquivo_s):
                with open(arquivo_s, 'r', encoding='utf-8') as f:
                    asm = f.read()
                    linhas = len(asm.split('\n'))
                    tem_start = '_start:' in asm
                    tem_loop_infinito = 'B .' in asm or 'b .' in asm
                    tem_printf = '.extern printf' in asm or 'bl printf' in asm
                    
                print(f"   [INFO] Assembly gerado: {linhas} linhas")
                print(f"   [{'OK' if tem_start else 'ERRO'}] Ponto de entrada _start presente")
                print(f"   [{'OK' if tem_loop_infinito else 'ERRO'}] Loop infinito (B .) presente")
                print(f"   [{'ERRO' if tem_printf else 'OK'}] Sem dependencias externas (printf)")
                
                # Verificar estrutura básica
                if tem_start and tem_loop_infinito and not tem_printf:
                    print("   [OK] Compativel com CPUlator")
                    resultados.append((teste, True, "OK"))
                else:
                    problemas = []
                    if not tem_start:
                        problemas.append("falta _start")
                    if not tem_loop_infinito:
                        problemas.append("falta B .")
                    if tem_printf:
                        problemas.append("tem printf")
                    resultados.append((teste, False, ", ".join(problemas)))
            else:
                print("   [AVISO] Arquivo .s nao foi gerado")
                resultados.append((teste, False, "Arquivo .s nao gerado"))
        else:
            erros = resultado.get('erros', 'Erro desconhecido')
            print(f"[ERRO] Erros de compilacao:")
            print(f"   {erros[:300]}")
            resultados.append((teste, False, erros[:100]))
            
    except Exception as e:
        print(f"[ERRO] Erro ao processar: {str(e)}")
        import traceback
        traceback.print_exc()
        resultados.append((teste, False, str(e)[:100]))

# Resumo
print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)

sucesso = sum(1 for _, ok, _ in resultados if ok)
total = len(resultados)

print(f"\nTotal de testes: {total}")
print(f"[OK] Sucesso: {sucesso}")
print(f"[ERRO] Falhas: {total - sucesso}")

if total - sucesso > 0:
    print("\n[AVISO] Testes com problemas:")
    for teste, ok, msg in resultados:
        if not ok:
            print(f"   - {teste}: {msg}")

print("\n" + "=" * 70)

