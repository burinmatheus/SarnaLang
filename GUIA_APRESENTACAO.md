# Guia de Apresentação e Defesa Técnica — SarnaLang 1.0

## Objetivo da demonstração

A apresentação deve evidenciar o pipeline completo:

```text
fonte .sarna
  -> lexer
  -> tokens
  -> parser
  -> AST
  -> análise semântica
  -> gerador C
  -> compilação/execução do C
```

## Sequência recomendada

### 1. Tema e proposta

Apresentar a SarnaLang como linguagem temática inspirada nos Gêmeos Show de
Bola, deixando claro que o humor está na sintaxe superficial e que a
implementação segue as fases formais de um transpilador.

### 2. Três decisões próprias

Explicar a diferença estrutural de cada decisão usando as produções:

1. Programa e blocos têm delimitadores distintos; cada ramo de `if/else`
   possui seu próprio `Bloco`, com abertura e fechamento.
2. `ListaSaida` admite várias expressões de tipos diferentes e lista vazia.
3. Expressões lógicas são valores: podem ser armazenadas, impressas e
   combinadas com precedência por `E MAIS`, `OU O QUÊ?` e `NEM A PAU`.

Mostrar os exemplos e justificativas da seção 3 do relatório. Identificadores
C únicos são uma decisão de implementação adicional.

### 3. Léxico

Executar:

```bash
python3 main.py tests/casos/02_valido_completo.sarna --tokens \
  -o generated/02_valido_completo.c
```

Explicar:

- palavras reservadas compostas;
- identificadores e literais;
- `=` versus `==` por longest match;
- comentários `//` e `BAH:`;
- erro léxico com linha e coluna.

### 4. Gramática e precedência

Mostrar as produções de:

```text
ExpressaoArit -> Termo { (+ | -) Termo }
Termo         -> Unario { (* | /) Unario }
```

Usar o exemplo:

```text
2 + 3 * 4
```

para explicar que a AST representa:

```text
2 + (3 * 4)
```

### 5. AST

Executar:

```bash
python3 main.py tests/casos/02_valido_completo.sarna --ast \
  -o generated/02_valido_completo.c
```

Apontar nós como:

```text
Program
VarDecl
WhileStmt
IfStmt
Binary
PrintStmt
```

### 6. Semântica

Explicar que o parser responde “a forma está correta?”, enquanto o analisador
semântico responde “o programa faz sentido no contexto?”.

Demonstrar:

```bash
python3 main.py tests/casos/05_erro_semantico.sarna
```

Depois, se solicitado:

```bash
python3 main.py tests/casos/06_erro_redeclaracao.sarna
python3 main.py tests/casos/07_erro_tipo.sarna
```

### 7. Geração de C

Abrir lado a lado:

```text
tests/casos/02_valido_completo.sarna
generated/02_valido_completo.c
```

Mostrar que a geração percorre a AST e produz `if`, `while`, `printf`,
`scanf` e expressões C.

### 8. Executar o C gerado

```bash
gcc generated/02_valido_completo.c -o programa
./programa
```

No Windows com MinGW:

```powershell
gcc generated\02_valido_completo.c -o programa.exe
.\programa.exe
```

### 9. Casos inválidos

Rodar na ordem:

```text
03_erro_lexico.sarna
04_erro_sintatico.sarna
05_erro_semantico.sarna
```

Isso evidencia claramente as três categorias de erro.

## Perguntas que o professor pode fazer

### “Por que `2 + 3 * 4` dá 14?”

Porque o parser possui níveis diferentes para `ExpressaoArit` e `Termo`.
A multiplicação é consumida em `Termo` antes que a soma seja construída.

### “Por que a gramática não tem recursão à esquerda?”

Porque foi planejada para descida recursiva. Em vez de algo como
`Expr -> Expr + Termo`, usa-se `Expr -> Termo { (+|-) Termo }`.

### “Qual a diferença entre erro sintático e semântico?”

`PORTÃOZÃO x = ;` viola a forma prevista pela GLC, portanto é sintático.
`y = x + 1;`, quando `y` nunca foi declarada, pode ter forma sintaticamente
correta, mas viola uma regra contextual, portanto é semântico.

### “Como `=` e `==` não entram em conflito?”

O lexer verifica o operador de dois caracteres antes do operador de um
caractere, aplicando longest match.

### “Por que não é substituição textual?”

Porque o código-fonte é tokenizado, transformado em AST, validado
semanticamente e somente depois a AST é percorrida pelo gerador de C.

### “Onde está a tabela de símbolos?”

Em `sarnalang/semantic.py`, implementada como uma pilha de dicionários de
escopo. Cada símbolo armazena nome, tipo e linha de declaração.

### “O que acontece com `PORTÃOZÃO x = 2.5;`?”

É rejeitado semanticamente: `PORTÃOZÃO` é `int` e não existe conversão
implícita `float -> int`. A promoção `int -> float` é permitida.

### “Por que gerar `sl_1_x` e `sl_2_x` para variáveis chamadas `x`?”

Cada nome identifica uma declaração. A semântica resolve a referência no
escopo correto, e o gerador preserva essa associação. Em um bloco com
`PORTÃOZÃO x = x + 1;`, o inicializador pode consultar um `x` externo;
o nome C único impede que ele leia o novo `x` ainda não inicializado.

Demonstrar `tests/casos/08_valido_escopos.sarna`: com entrada `9`, a saída é
`6 externo`, `9`, `SHOW` e `5 externo`, cada trecho em sua linha.

### “Por que o lexer tem mapas de posições?”

A remoção de marcas Unicode pode encurtar a visão usada para reconhecer
palavras reservadas. Os mapas relacionam essa visão ao texto original,
preservando lexemas, conteúdo de strings e localização dos erros.
Identificadores continuam restritos a ASCII.

### “Como o editor sabe que um programa é inválido?”

A extensão envia o documento, inclusive alterações não salvas, ao módulo
`sarnalang.editor`. Ele usa `Lexer`, `Parser` e `SemanticAnalyzer`, devolvendo
JSON. A extensão apresenta o primeiro erro no painel Problems, sem gerar C.

### “Passar na suíte significa que o C funciona?”

A execução padrão compila e executa o C com entrada controlada, compara a
saída e verifica as rejeições. `--skip-c` é uma checagem parcial, identificada
explicitamente como tal.

## Ensaio individual e preparação

Cada integrante deve conseguir executar o pipeline completo e explicar pelo
menos um token, uma produção, um nó da AST e uma regra de tipos. No ensaio,
alterem os papéis para que todos pratiquem diagnóstico e pequenas mudanças:

- Trocar `2 + 3 * 4` por `(2 + 3) * 4`, prever 14/20 e localizar a mudança na AST.
- Introduzir `@`, remover uma expressão e usar uma variável inexistente;
  identificar a fase que rejeita cada programa.
- Alterar uma condição para `1` e explicar por que a sintaxe aceita a forma,
  mas a semântica exige um lógico.
- Explicar a diferença entre redeclaração no mesmo escopo e sombreamento.

Antes da apresentação, executar `python3 run_tests.py` e os testes da extensão
indicados no README dela. Conferir Python e GCC/Clang no computador da sala.
Se usar o VS Code, abrir a extensão atual e verificar `sarna.pythonPath`.
