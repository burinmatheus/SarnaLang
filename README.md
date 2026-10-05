# SarnaLang 1.0 — Trabalho Prático 1

Transpilador acadêmico de uma linguagem temática inspirada no universo dos
Gêmeos Show de Bola.

**Entrada:** `.sarna`  
**Saída:** `.c`

## Pipeline

```text
Código SarnaLang
      ↓
     Lexer
      ↓
    Tokens
      ↓
     Parser
      ↓
      AST
      ↓
Análise Semântica
      ↓
  Gerador de C
      ↓
   Programa C
```

## Requisitos

- Python 3.10+
- GCC/Clang para executar a suíte completa e os programas C gerados
- Node.js apenas para desenvolver/testar a extensão do VS Code
- Nenhuma biblioteca Python externa

Nos comandos abaixo, use `python3` no Linux/macOS. No Windows, substitua
por `py -3` ou pelo executável Python configurado no computador.

## Uso

```bash
python3 main.py examples/demo_sarnalang.sarna
```

Isso gera:

```text
examples/demo_sarnalang.c
```

Definindo arquivo de saída:

```bash
python3 main.py \
  tests/casos/01_valido_basico.sarna \
  -o generated/01_valido_basico.c
```

Tokens:

```bash
python3 main.py \
  tests/casos/02_valido_completo.sarna \
  --tokens
```

AST:

```bash
python3 main.py \
  tests/casos/02_valido_completo.sarna \
  --ast
```

Tokens + AST:

```bash
python3 main.py \
  tests/casos/02_valido_completo.sarna \
  --tokens --ast
```

## Compilando o C

Linux/macOS:

```bash
gcc generated/01_valido_basico.c -o programa
./programa
```

Windows com GCC/MinGW:

```powershell
gcc generated\01_valido_basico.c -o programa.exe
.\programa.exe
```

## Rodando a suíte

```bash
python3 run_tests.py
```

A execução padrão verifica as fases do transpilador, compila os programas
válidos e compara sua saída com o resultado esperado. Inclui entrada controlada,
precedência, escopos, Unicode, erros e os exemplos/snippets da extensão.
Os binários são criados em diretórios temporários.

```bash
python3 run_tests.py --cc clang
python3 run_tests.py --skip-c  # checagem parcial, sem execução C
```

Sem compilador C, a execução padrão informa a dependência ausente. Os detalhes
e as saídas dos exemplos estão em [RESULTADOS_TESTES.md](RESULTADOS_TESTES.md).

## Extensão para VS Code

A extensão em [gsb-vscode](gsb-vscode/README.md) usa a mesma sintaxe e o próprio
analisador Python para diagnósticos. Para verificar a integração:

```bash
node gsb-vscode/scripts/prepare-server.js
npm run lint --prefix gsb-vscode
npm test --prefix gsb-vscode
```

## Estrutura

```text
SarnaLang_TP1_v1/
├── sarnalang/
│   ├── ast_nodes.py
│   ├── lexer.py
│   ├── parser.py
│   ├── semantic.py
│   ├── codegen_c.py
│   ├── editor.py
│   ├── transpiler.py
│   └── __init__.py
├── tests/
│   ├── test_transpiler.py
│   ├── support.py
│   └── casos/
│       ├── 01_valido_basico.sarna
│       ├── 02_valido_completo.sarna
│       ├── 03_erro_lexico.sarna
│       ├── 04_erro_sintatico.sarna
│       ├── 05_erro_semantico.sarna
│       ├── 06_erro_redeclaracao.sarna
│       ├── 07_erro_tipo.sarna
│       ├── 08_valido_escopos.sarna
│       └── 09_erro_identificador.sarna
├── generated/
│   ├── 01_valido_basico.c
│   ├── 02_valido_completo.c
│   ├── 08_valido_escopos.c
│   └── demo_sarnalang.c
├── examples/
│   └── demo_sarnalang.sarna
├── gsb-vscode/
├── ESPECIFICACAO_LEXICA.md
├── GRAMATICA.md
├── REGRAS_SEMANTICAS.md
├── RELATORIO_TECNICO.md
├── CHECKLIST_ENUNCIADO.md
├── RESULTADOS_TESTES.md
├── GUIA_APRESENTACAO.md
├── run_tests.py
├── main.py
└── README.md
```

## Vocabulário principal

| SarnaLang | Significado |
|---|---|
| `E AÍ MARCELO, É O QUÊ?` | início do programa |
| `SHOW DE BOLA, VALEU!` | fim do programa |
| `ABRE O PORTÃO` | abre bloco |
| `FECHA O PORTÃO` | fecha bloco |
| `PORTÃOZÃO` | inteiro |
| `CASONA` | real |
| `NENEZINHO` | texto |
| `GRAXA VÉIA` | lógico |
| `SHOW` | verdadeiro |
| `NÃO SHOW` | falso |
| `MAS TU É SARNA NÉ?` | if |
| `NÃO É SARNA NÃO` | else |
| `DE NOVO MARCELO` | while |
| `E AÍ MARCELO, MOSTRA AÍ` | saída |
| `ME DIZ AÍ` | entrada |
| `E MAIS` | AND |
| `OU O QUÊ?` | OR |
| `NEM A PAU` | NOT |
| `BAH:` | comentário |

## Importante

Esta versão é propositalmente menor do que uma linguagem industrial. O
objetivo é demonstrar corretamente as fases de um compilador/transpilador e
manter a gramática, o código e o relatório consistentes.

Projeto acadêmico/paródico independente, sem afiliação oficial com os Gêmeos
Show de Bola.
