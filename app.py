#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal da aplicação Flask
Redireciona para Core/app.py
"""

import os
import sys

# Obter diretórios
base_dir = os.path.dirname(os.path.abspath(__file__))
core_dir = os.path.join(base_dir, 'Core')

# Adicionar Core ao path
sys.path.insert(0, core_dir)

# Mudar para o diretório base para que os caminhos relativos funcionem
os.chdir(base_dir)

# Importar app do Core
from app import app

if __name__ == '__main__':
    print("=" * 70)
    print("Compilador MiniPar - Interface Web")
    print("=" * 70)
    print("\nAcesse: http://127.0.0.1:5001")
    print("Pressione Ctrl+C para parar o servidor\n")
    app.run(debug=True, port=5001)

