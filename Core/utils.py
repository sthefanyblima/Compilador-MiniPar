#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitários do compilador: funções auxiliares e gerenciadores de canais/threads
"""

import threading


# --- SISTEMA DE CANAIS E THREADS ---
class ChannelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.channels = {}
            return cls._instance
    
    def create_channel(self, name, comp1, comp2):
        self.channels[name] = {
            'comp1': comp1,
            'comp2': comp2,
            'data': None,
            'lock': threading.Lock()
        }
    
    def send_data(self, channel_name, data):
        if channel_name in self.channels:
            with self.channels[channel_name]['lock']:
                self.channels[channel_name]['data'] = data
                return True
        return False
    
    def receive_data(self, channel_name):
        if channel_name in self.channels:
            with self.channels[channel_name]['lock']:
                data = self.channels[channel_name]['data']
                self.channels[channel_name]['data'] = None
                return data
        return None


class ThreadManager:
    def __init__(self):
        self.threads = []
        self.results = {}
        self.lock = threading.Lock()
    
    def execute_parallel(self, blocks):
        self.threads = []
        self.results = {}
        
        def run_block(block_id, block_code):
            try:
                result = f"Thread_{block_id}_completed"
                with self.lock:
                    self.results[block_id] = result
            except Exception as e:
                with self.lock:
                    self.results[block_id] = f"Error: {str(e)}"
        
        for i, block in enumerate(blocks):
            thread = threading.Thread(target=run_block, args=(i, block))
            self.threads.append(thread)
            thread.start()
        
        for thread in self.threads:
            thread.join()
        
        return self.results


# --- FUNÇÃO AUXILIAR PARA FORMATAR A AST ---
def formatar_ast(node, level=0):
    """Formata uma AST em uma string legível"""
    if node is None:
        return ""
    
    # Se node não for uma tupla ou lista, tratamos como valor simples
    if not isinstance(node, (tuple, list)):
        indent = '  ' * level
        return f"{indent}- {repr(node)}\n"
    
    indent = '  ' * level
    result = f"{indent}- {node[0]}\n"
    
    for item in node[1:]:
        if isinstance(item, tuple):
            result += formatar_ast(item, level + 1)
        elif isinstance(item, list):
            for sub_item in item:
                result += formatar_ast(sub_item, level + 1)
        elif item is not None:
            if node[0] == 'string':
                result += f"{'  ' * (level + 1)}- \"{item}\"\n"
            else:
                result += f"{'  ' * (level + 1)}- '{item}'\n"
            
    return result

