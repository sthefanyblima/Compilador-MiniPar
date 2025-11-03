# Estrutura do Projeto - Compilador MiniPar

## 📁 Arquivos Essenciais do Projeto

### Core do Compilador (pasta `Core/`)
- `motor_compilador.py` - Núcleo completo do compilador (lexer, parser, análise semântica, gerador C3E, gerador ARMv7, interpretador)
- `lexer.py` - Analisador léxico (MiniParLexer)
- `parser.py` - Analisador sintático (MiniParParser)
- `semantic.py` - Analisador semântico (SemanticAnalyzer)
- `c3e_generator.py` - Gerador de código intermediário (C3EGenerator)
- `armv7_generator.py` - Gerador de código ARMv7 (ARMv7CodeGenerator)
- `interpreter.py` - Interpretador do código MiniPar (MiniParInterpreter)
- `compiler.py` - Funções principais de compilação
- `utils.py` - Utilitários auxiliares

### Interface Web
- `app.py` - Ponto de entrada principal da aplicação Flask (raiz)
- `Core/app.py` - Aplicação Flask para interface web interativa
- `templates/index.html` - Interface HTML do compilador web

### Configuração
- `Configuração/requirements.txt` - Dependências Python (flask, sly)
- `Configuração/Tema1-Projeto1-Compilador-MiniPar-2025-1-FINAL-okok.pdf` - Especificação do projeto
- `.gitignore` - Arquivos a serem ignorados pelo Git

### Documentação
- `README.md` - Documentação principal do projeto
- `relatorio_compatibilidade.md` - Relatório de compatibilidade dos testes com CPUlator
- `ESTRUTURA_PROJETO.md` - Este arquivo (estrutura do projeto)

## 🧪 Arquivos de Teste (Versões Finais Funcionais)

Todos os testes são compatíveis com CPUlator e logicamente equivalentes ao PDF:

**Testes Principais:**
- `teste1_servidor.mp` - Teste de servidor/calculadora com canais de comunicação
- `teste2_threads.mp` - Teste de programação paralela (PAR)
- `teste3_neuronio.mp` - Teste de neurônio com funções
- `teste4_XOR.mp` - Teste de arrays bidimensionais
- `teste5_rede_neural.mp` - Teste de rede neural com arrays de strings
- `teste6_fatorial.mp` - Teste de loop enquanto (fatorial)
- `teste7_fibonacci.mp` - Teste de loop enquanto (Fibonacci)
- `teste8_quicksort.mp` - Teste de arrays e ordenação

**Testes Adicionais:**
- `teste_simples.mp` - Exemplo simples de código MiniPar
- `teste_enquanto_fim.mp` - Teste de loop enquanto

## 🛠️ Scripts de Compilação e Teste

- `compilar_testes.py` - Compila todos os arquivos de teste e gera executáveis
- `testar_execucao.py` - Testa a execução dos programas de teste
- `testar_todos.py` - Testa todos os testes principais
- `testar_todos_testes.py` - Testa todos os testes com detalhes completos
- `verificar_todos_testes.py` - Verifica compatibilidade com CPUlator
- `exemplo_uso.py` - Exemplo de uso do compilador


## 🚫 Arquivos Ignorados pelo Git

Os seguintes arquivos são gerados automaticamente e não devem ser commitados:
- `*.s` - Arquivos assembly gerados
- `*.o`, `*.out`, `*.exe`, `*.elf` - Executáveis compilados
- `__pycache__/` - Cache Python
- `parser.out`, `parsetab.py` - Arquivos gerados pelo parser
- Arquivos de IDEs e ambientes virtuais

## ✅ Checklist para Commit

- [x] Arquivos fonte (.mp) dos testes organizados
- [x] Código Python limpo e funcional
- [x] Documentação atualizada
- [x] .gitignore configurado corretamente
- [x] Arquivos gerados removidos
- [x] Relatório de compatibilidade incluído
- [x] Estrutura do projeto documentada

