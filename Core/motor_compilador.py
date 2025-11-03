#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor Compilador - Módulo principal de compatibilidade
Este módulo importa e re-exporta todos os componentes do compilador
"""

# Importar todos os componentes dos módulos separados
# Usar try/except para suportar imports relativos e absolutos
try:
    from .utils import formatar_ast, ChannelManager, ThreadManager
    from .lexer import MiniParLexer
    from .parser import MiniParParser
    from .semantic import SemanticAnalyzer
    from .c3e_generator import C3EGenerator
    from .armv7_generator import ARMv7CodeGenerator
    from .interpreter import MiniParInterpreter
    from .compiler import (
        compilar_codigo,
        salvar_assembly,
        compilar_executavel,
        compilar_programa_minipar
    )
except ImportError:
    # Fallback para imports absolutos quando usado diretamente
    from utils import formatar_ast, ChannelManager, ThreadManager
    from lexer import MiniParLexer
    from parser import MiniParParser
    from semantic import SemanticAnalyzer
    from c3e_generator import C3EGenerator
    from armv7_generator import ARMv7CodeGenerator
    from interpreter import MiniParInterpreter
    from compiler import (
        compilar_codigo,
        salvar_assembly,
        compilar_executavel,
        compilar_programa_minipar
    )

# Re-exportar tudo para manter compatibilidade
__all__ = [
    'formatar_ast',
    'ChannelManager',
    'ThreadManager',
    'MiniParLexer',
    'MiniParParser',
    'SemanticAnalyzer',
    'C3EGenerator',
    'ARMv7CodeGenerator',
    'MiniParInterpreter',
    'compilar_codigo',
    'salvar_assembly',
    'compilar_executavel',
    'compilar_programa_minipar',
]
